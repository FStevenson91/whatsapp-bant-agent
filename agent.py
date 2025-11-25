"""
Definición del agente inbound BANT con Google ADK.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Verificar que la API key esté cargada
if not os.getenv('GOOGLE_API_KEY'):
    raise ValueError("❌ GOOGLE_API_KEY no encontrada en .env. Por favor configura tu API key.")

from google.adk.agents import Agent
from config import TenantConfig, load_tenant_config
from prompts import get_system_prompt
from tools import crm_tools, calendar_tools


def create_inbound_agent(tenant_id: str = "default") -> Agent:
    """
    Crea un agente inbound personalizado según la configuración del tenant.
    
    Args:
        tenant_id: ID del tenant/cliente
    
    Returns:
        Agente configurado y listo para usar
    """
    # Carga configuración del tenant
    config = load_tenant_config(tenant_id)
    
    # Genera el system prompt personalizado
    system_prompt = get_system_prompt(config)
    
    # Define las herramientas disponibles para el agente
    tools = [
        crm_tools.save_to_crm,
        crm_tools.get_prospect_info,
        calendar_tools.schedule_meeting,
        calendar_tools.check_availability
    ]
    
    # Crea el agente con Google ADK
    agent = Agent(
        name="inbound_bant_agent",
        model="gemini-2.0-flash",
        instruction=system_prompt,
        description="Agente de calificación BANT para prospectos inbound",
        tools=tools
    )
    
    return agent


class InboundAgentSession:
    """
    Maneja una sesión de conversación con un prospecto.
    Mantiene el estado de la conversación.
    """
    
    def __init__(self, tenant_id: str = "default", prospect_phone: str = None):
        self.tenant_id = tenant_id
        self.prospect_phone = prospect_phone
        self.agent = create_inbound_agent(tenant_id)
        self.config = load_tenant_config(tenant_id)
        
        # Estado de la calificación BANT
        self.bant_data = {
            "budget": None,
            "authority": None,
            "need": None,
            "timeline": None
        }
        self.qualified = None
        self.meeting_scheduled = False
        
        # Inicializar runner y sesión
        self._initialize_session()
    
    def _initialize_session(self):
        """Inicializa el runner y la sesión"""
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name="inbound_bant_agent",
            session_service=self.session_service
        )
        self.user_id = self.prospect_phone or "user_default"
        self.session_id = f"session_{self.user_id}"
        self.session_initialized = False
    
    async def _ensure_session_async(self):
        """Asegura que la sesión esté creada (async)"""
        if not self.session_initialized:
            await self.session_service.create_session(
                app_name="inbound_bant_agent",
                user_id=self.user_id,
                session_id=self.session_id
            )
            self.session_initialized = True
    
    def send_message(self, message: str) -> str:
        """
        Envía un mensaje al agente y obtiene la respuesta (versión sync para CLI).
        
        Args:
            message: Mensaje del prospecto
        
        Returns:
            Respuesta del agente
        """
        import asyncio
        
        # Crear sesión si no existe (modo sync para CLI)
        if not self.session_initialized:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    self.session_service.create_session(
                        app_name="inbound_bant_agent",
                        user_id=self.user_id,
                        session_id=self.session_id
                    )
                )
                loop.close()
                self.session_initialized = True
            except Exception as e:
                print(f"Error creando sesión: {e}")
        
        try:
            from google.genai import types
            
            # Envía el mensaje
            content = types.Content(
                role='user',
                parts=[types.Part(text=message)]
            )
            
            # Ejecuta de forma síncrona
            events = self.runner.run(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=content
            )
            
            # Obtiene la respuesta final
            response_text = ""
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text = part.text
            
            return response_text if response_text else "Lo siento, no pude procesar tu mensaje."
            
        except Exception as e:
            print(f"\n❌ Error en conversación: {e}")
            import traceback
            traceback.print_exc()
            return f"Disculpa, tuve un problema técnico. ¿Podrías repetir eso?"
    
    async def send_message_async(self, message: str) -> str:
        """
        Envía un mensaje al agente y obtiene la respuesta (versión async para FastAPI).
        
        Args:
            message: Mensaje del prospecto
        
        Returns:
            Respuesta del agente
        """
        try:
            from google.genai import types
            
            # Asegura que la sesión esté creada
            await self._ensure_session_async()
            
            # Envía el mensaje
            content = types.Content(
                role='user',
                parts=[types.Part(text=message)]
            )
            
            # Ejecuta de forma síncrona (Runner.run es sync)
            events = self.runner.run(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=content
            )
            
            # Obtiene la respuesta final
            response_text = ""
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text = part.text
            
            return response_text if response_text else "Lo siento, no pude procesar tu mensaje."
            
        except Exception as e:
            print(f"\n❌ Error en conversación: {e}")
            import traceback
            traceback.print_exc()
            return f"Disculpa, tuve un problema técnico. ¿Podrías repetir eso?"
    
    def is_qualified(self) -> bool:
        """Verifica si el prospecto está calificado según BANT"""
        return all(self.bant_data.values())
    
    def get_qualification_status(self) -> dict:
        """Retorna el estado de calificación del prospecto"""
        return {
            "bant_data": self.bant_data,
            "is_qualified": self.is_qualified(),
            "meeting_scheduled": self.meeting_scheduled,
            "prospect_phone": self.prospect_phone
        }


# Ejemplo de uso simple
if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Verificando configuración...")
    print(f"✓ GOOGLE_API_KEY: {'Configurada ✅' if os.getenv('GOOGLE_API_KEY') else 'NO ENCONTRADA ❌'}")
    print("=" * 60)
    print()
    
    try:
        # Crea una sesión con el agente
        print("🚀 Iniciando agente...")
        session = InboundAgentSession(
            tenant_id="default",
            prospect_phone="+56912345678"
        )
        
        print("✅ Agente iniciado correctamente")
        print("=" * 60)
        print("🤖 Agente Inbound BANT listo. Escribe 'exit' para terminar.\n")
        
        # Mensaje inicial del agente
        initial_message = session.send_message("Hola")
        print(f"Agente: {initial_message}\n")
        
        while True:
            user_input = input("Tú: ")
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!")
                break
            
            response = session.send_message(user_input)
            print(f"\nAgente: {response}\n")
            
            # Muestra estado de calificación (solo para debug)
            status = session.get_qualification_status()
            if status["is_qualified"]:
                print("✅ Prospecto CALIFICADO\n")
    
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()