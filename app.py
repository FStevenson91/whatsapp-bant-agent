"""
FastAPI app para recibir webhooks de WhatsApp (vía Spicy).
Maneja las conversaciones con el agente inbound.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from agent import InboundAgentSession

app = FastAPI(
    title="Inbound BANT Agent API",
    description="API para agente inbound que califica prospectos usando BANT",
    version="1.0.0"
)


# Almacenamiento temporal de sesiones
# En producción, esto debería ser Redis o similar
active_sessions: Dict[str, InboundAgentSession] = {}


class WhatsAppMessage(BaseModel):
    """Modelo para mensajes entrantes de WhatsApp"""
    phone: str = Field(..., description="Número de teléfono del remitente")
    message: str = Field(..., description="Contenido del mensaje")
    tenant_id: str = Field(default="default", description="ID del tenant/cliente")
    timestamp: Optional[str] = Field(default=None, description="Timestamp del mensaje")


class AgentResponse(BaseModel):
    """Modelo para respuestas del agente"""
    phone: str
    response: str
    session_id: str
    qualified: bool = False
    meeting_scheduled: bool = False


@app.get("/")
async def root():
    """Endpoint raíz para health check"""
    return {
        "service": "Inbound BANT Agent",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "api_key_configured": bool(os.getenv('GOOGLE_API_KEY'))
    }


@app.post("/webhook/whatsapp", response_model=AgentResponse)
async def whatsapp_webhook(message: WhatsAppMessage):
    """
    Webhook que recibe mensajes de WhatsApp desde Spicy.
    
    Este endpoint:
    1. Recibe el mensaje del prospecto
    2. Crea o recupera la sesión del agente
    3. Procesa el mensaje con el agente
    4. Retorna la respuesta para enviar al prospecto
    """
    try:
        phone = message.phone
        session_id = f"{message.tenant_id}_{phone}"
        
        # Obtiene o crea sesión del agente para este prospecto
        if session_id not in active_sessions:
            print(f"🆕 Creando nueva sesión para {phone}")
            active_sessions[session_id] = InboundAgentSession(
                tenant_id=message.tenant_id,
                prospect_phone=phone
            )
        
        session = active_sessions[session_id]
        
        # Procesa el mensaje con el agente (versión async)
        print(f"📨 Mensaje de {phone}: {message.message}")
        agent_response = await session.send_message_async(message.message)
        print(f"🤖 Respuesta: {agent_response[:100]}...")
        
        # Obtiene el estado de calificación
        status = session.get_qualification_status()
        
        return AgentResponse(
            phone=phone,
            response=agent_response,
            session_id=session_id,
            qualified=status["is_qualified"],
            meeting_scheduled=status["meeting_scheduled"]
        )
        
    except Exception as e:
        print(f"❌ Error procesando mensaje: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando mensaje: {str(e)}"
        )


@app.post("/session/close/{session_id}")
async def close_session(session_id: str):
    """
    Cierra una sesión activa.
    Útil para liberar recursos.
    """
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": f"Sesión {session_id} cerrada exitosamente"}
    
    raise HTTPException(status_code=404, detail="Sesión no encontrada")


@app.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Obtiene el estado de calificación de una sesión.
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session = active_sessions[session_id]
    return session.get_qualification_status()


@app.get("/sessions")
async def list_sessions():
    """Lista todas las sesiones activas"""
    return {
        "active_sessions": len(active_sessions),
        "sessions": [
            {
                "session_id": sid,
                "status": session.get_qualification_status()
            }
            for sid, session in active_sessions.items()
        ]
    }


# Endpoint para testing local (sin necesidad de WhatsApp real)
@app.post("/test/chat")
async def test_chat(message: WhatsAppMessage):
    """
    Endpoint de prueba para simular conversaciones.
    Útil para desarrollo local.
    """
    return await whatsapp_webhook(message)


if __name__ == "__main__":
    import uvicorn
    
    # Inicia el servidor
    print("=" * 60)
    print("🚀 Iniciando servidor del agente inbound...")
    print("📱 Webhook disponible en: http://localhost:8000/webhook/whatsapp")
    print("🧪 Testing disponible en: http://localhost:8000/test/chat")
    print("📊 Docs en: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload en desarrollo
    )