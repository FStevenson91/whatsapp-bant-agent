# 🤖 Agente Inbound BANT - Calificación de Prospectos

Agente conversacional que califica prospectos usando metodología BANT (Budget, Authority, Need, Timeline) de forma natural y humana a través de WhatsApp.

## 🎯 Características

- ✅ **Calificación BANT automatizada** de forma conversacional
- 👤 **Personalidad humana**: El prospecto no nota que es un bot
- 📅 **Agendamiento automático** de reuniones
- 💾 **Integración con CRM** (mock JSON por ahora, preparado para MongoDB)
- 🔧 **Multi-tenant**: Cada cliente puede personalizar su agente
- 📱 **WhatsApp ready**: Recibe webhooks de Whatsapp
- 🚀 **Escalable**: Arquitectura preparada para producción

## 📁 Estructura del Proyecto
```
inbound_agent/
├── tools/
│   ├── __init__.py          # Exporta todas las tools
│   ├── crm_tools.py         # Integración con CRM (mock)
│   └── calendar_tools.py    # Google Calendar (mock)
├── data/                     # Datos mock (se crea automáticamente)
│   ├── crm_mock.json
│   └── calendar_mock.json
├── .venv/                    # Entorno virtual
├── config.py                 # Configuración multi-tenant
├── prompts.py               # Templates de prompts personalizables
├── schemas.py               # Modelos de datos (opcional)
├── agent.py                 # Definición del agente con Google ADK
├── app.py                   # FastAPI webhook receiver
├── requirements.txt
├── .env                     # Variables de entorno (NO commitear)
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Instalación

### 1. Clonar y preparar entorno
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
# Copiar el ejemplo
cp .env.example .env

# Editar .env y agregar tu API key de Google
GOOGLE_API_KEY=tu_api_key_aqui
GOOGLE_GENAI_USE_VERTEXAI=false
```

### 3. Obtener Google API Key

1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Crea una nueva API key
3. Cópiala a tu archivo `.env`

## 💻 Uso

### Modo 1: Testing Local (Consola)

Prueba el agente directamente desde la terminal:
```bash
python agent.py
```

**Ejemplo de conversación:**
```
🤖 Agente Inbound iniciado. Escribe 'salir' para terminar.

Agente: ¡Hola! 👋 Soy Ana de Spicy...

Tú: Hola, necesito información sobre un CRM
Tú: Soy el CEO de mi empresa
Tú: Tenemos un presupuesto de 20000 dólares
Tú: Lo necesitamos en 60 días
```

### Modo 2: Servidor API (Webhook)

Inicia el servidor FastAPI para recibir webhooks:
```bash
python app.py
```

El servidor estará disponible en:
- 📱 **Webhook**: `http://localhost:8000/webhook/whatsapp`
- 🧪 **Testing**: `http://localhost:8000/test/chat`
- 📖 **Docs**: `http://localhost:8000/docs`

### Testing del Webhook

**Opción 1: Swagger UI (Recomendado)**

1. Ve a http://localhost:8000/docs
2. Busca `POST /test/chat`
3. Click en "Try it out"
4. Pega este JSON:
```json
{
  "phone": "+56912345678",
  "message": "Hola, me gustaría información sobre sus servicios",
  "tenant_id": "default"
}
```
5. Click en "Execute"

**Opción 2: PowerShell**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/test/chat" -Method POST -ContentType "application/json" -Body '{"phone": "+56912345678", "message": "Hola", "tenant_id": "default"}'
```

**Opción 3: curl (si lo tienes instalado)**
```bash
curl -X POST "http://localhost:8000/test/chat" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+56912345678", "message": "Hola", "tenant_id": "default"}'
```

## 🎨 Personalización Multi-Tenant

Cada cliente puede personalizar su agente editando `config.py`:
```python
# Ejemplo de configuración personalizada
custom_config = TenantConfig(
    tenant_id="empresa_xyz",
    personality=AgentPersonality(
        name="Carlos",
        tone="formal y técnico",
        company_name="TechCorp",
        company_description="empresa de software empresarial"
    ),
    bant_criteria=BANTCriteria(
        min_budget=10000,
        valid_authorities=["CTO", "Director TI"],
        required_needs=["integración", "API", "cloud"],
        max_timeline_days=60
    )
)
```

## 🔗 Integración con WhatsApp

El webhook en `/webhook/whatsapp` espera recibir mensajes en este formato:
```json
{
  "phone": "+56912345678",
  "message": "Contenido del mensaje",
  "tenant_id": "company_001",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Spicy debe enviar los mensajes entrantes de WhatsApp a este endpoint:
- **URL**: `http://tu-servidor:8000/webhook/whatsapp`
- **Method**: POST
- **Content-Type**: application/json

**Respuesta del webhook:**
```json
{
  "phone": "+56912345678",
  "response": "Respuesta del agente...",
  "session_id": "default_+56912345678",
  "qualified": false,
  "meeting_scheduled": false
}
```

## 📊 Flujo de Calificación BANT

1. **Saludo inicial**: El agente inicia la conversación de forma natural
2. **Construcción de rapport**: Establece conexión antes de calificar
3. **Descubrimiento conversacional**: Pregunta por BANT sin que parezca interrogatorio:
   - 💰 **Budget**: "¿Tienen un presupuesto definido para este proyecto?"
   - 👔 **Authority**: "¿Cuál es tu rol en la empresa?"
   - 🎯 **Need**: "¿Cuál es el principal desafío que buscan resolver?"
   - ⏰ **Timeline**: "¿Para cuándo necesitarían tener esto funcionando?"
4. **Calificación automática**: El agente determina si el prospecto califica
5. **Guardado en CRM**: Información se guarda automáticamente
6. **Agendamiento**: Si califica, ofrece agendar reunión

## 🛠️ Herramientas Disponibles

El agente tiene acceso a estas herramientas:

### CRM Tools (`tools/crm_tools.py`)
- `save_to_crm()`: Guarda prospecto calificado
- `get_prospect_info()`: Busca información existente

### Calendar Tools (`tools/calendar_tools.py`)
- `schedule_meeting()`: Agenda reuniones
- `check_availability()`: Verifica disponibilidad

## 📝 Datos Mock

Por defecto, los datos se guardan en JSON locales:
- `data/crm_mock.json`: Prospectos calificados
- `data/calendar_mock.json`: Reuniones agendadas

Estos archivos se crean automáticamente al ejecutar el agente.

**Ejemplo de `crm_mock.json`:**
```json
{
  "prospects": [
    {
      "id": "prospect_1",
      "name": "Juan Pérez",
      "phone": "+56912345678",
      "email": "juan@empresa.com",
      "bant": {
        "budget": "20000 USD",
        "authority": "CEO",
        "need": "Automatización de ventas",
        "timeline": "60 días"
      },
      "qualification_status": "QUALIFIED",
      "created_at": "2024-11-21T10:30:00",
      "source": "whatsapp_inbound"
    }
  ]
}
```

## 🔄 Migración a Producción

### Conectar MongoDB (CRM Real)

1. Instalar dependencia:
```bash
pip install pymongo
```

2. Actualizar `tools/crm_tools.py` para conectar a MongoDB en lugar del mock
3. Configurar en `.env`:
```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DATABASE=crm_db
```

### Conectar Google Calendar (Real)

1. Habilitar Google Calendar API en GCP
2. Descargar credenciales
3. Instalar dependencia:
```bash
pip install google-cloud-calendar
```

4. Actualizar `tools/calendar_tools.py`
5. Configurar en `.env`:
```env
GOOGLE_CALENDAR_CREDENTIALS=./credentials.json
```

## 🚀 Deployment

El proyecto está preparado para:
- **Vertex AI**: Para el agente
- **Cloud Run**: Para el servidor FastAPI
- **Azure**: Alternativa para la infraestructura

### Variables de entorno necesarias en producción:
```env
GOOGLE_API_KEY=xxx
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=tu-proyecto
GOOGLE_CLOUD_LOCATION=us-central1
MONGODB_URI=xxx
GOOGLE_CALENDAR_CREDENTIALS=xxx
```

## 📚 API Endpoints

### Principales
- `GET /` - Información del servicio
- `GET /health` - Health check
- `POST /webhook/whatsapp` - Recibe mensajes de WhatsApp
- `GET /sessions` - Lista sesiones activas
- `GET /session/{id}/status` - Estado de calificación de una sesión
- `POST /session/close/{id}` - Cierra una sesión

### Testing
- `POST /test/chat` - Simula conversación sin WhatsApp

Ver documentación completa en `/docs` cuando el servidor esté corriendo.

## 🎯 Ejemplo de Conversación Completa
```
Usuario: Hola, necesito información

Agente: ¡Hola! 👋 Soy Ana de Spicy. ¿Cómo estás? Vi que te interesa 
        conocer más sobre nuestras soluciones. ¿En qué podemos ayudarte?

Usuario: Necesitamos un CRM

Agente: Perfecto, entiendo que buscan un CRM. Para poder ayudarte mejor, 
        cuéntame: ¿qué desafío específico buscan resolver con el CRM?

Usuario: Perdemos seguimiento de leads porque usamos Excel

Agente: Ah, te entiendo perfectamente. El Excel se queda corto cuando 
        el equipo crece. ¿Cuál es tu rol en la empresa? Para saber 
        cómo enfocarte mejor.

Usuario: Soy el CEO

Agente: Genial, entonces tú tomas las decisiones 😊. ¿Tienen ya un 
        presupuesto definido para este proyecto?

Usuario: Entre 15000 y 20000 dólares

Agente: Perfecto, ese presupuesto nos permite implementar una solución 
        robusta. ¿Para cuándo necesitarían tener el CRM funcionando?

Usuario: En 2 meses

Agente: Excelente, 2 meses es un timeline razonable. Creo que podemos 
        ayudarte. ¿Te parece si agendamos una llamada de 30 minutos 
        para revisar esto en detalle? ¿Qué día te viene bien?
```

## 🔧 Troubleshooting

### Error: `asyncio.run() cannot be called from a running event loop`
**Solución**: Asegúrate de usar `send_message_async()` en FastAPI y `send_message()` en CLI.

### Error: `Model not found`
**Solución**: Verifica que estés usando `gemini-2.0-flash` en `agent.py`.

### Error: `RESOURCE_EXHAUSTED` (429)
**Solución**: Has excedido la cuota gratuita. Espera unos minutos o cambia a otro modelo.

### El servidor no inicia
**Solución**: 
1. Verifica que `.venv` esté activado
2. Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
3. Verifica que el puerto 8000 no esté ocupado

## 🧪 Testing

### Tests manuales recomendados:

1. **Test básico de conversación** (CLI)
```bash
python agent.py
# Prueba: "Hola" → debe responder naturalmente
```

2. **Test de webhook** (API)
```bash
python app.py
# Ve a http://localhost:8000/docs
# Prueba el endpoint /test/chat
```

3. **Test de calificación BANT completa**
- Inicia conversación
- Proporciona Budget, Authority, Need, Timeline
- Verifica que se guarde en `data/crm_mock.json`

4. **Test de agendamiento**
- Completa calificación BANT
- Agenda una reunión
- Verifica que se guarde en `data/calendar_mock.json`

## 📦 Dependencias Principales

- `google-adk==1.18.0` - Framework de agentes de Google
- `fastapi==0.115.0` - Framework web
- `uvicorn[standard]==0.30.0` - Servidor ASGI
- `pydantic==2.9.0` - Validación de datos
- `python-dotenv==1.0.1` - Variables de entorno

## 🤝 Contribuir

Este es un proyecto de práctica laboral para Spicy.

## 📞 Soporte

Para dudas o problemas:
- Revisa la documentación de Google ADK: https://google.github.io/adk-docs/

---

**Versión**: 1.0.0  
**Última actualización**: Noviembre 2024  
**Desarrollado con**: Google ADK, FastAPI, Python 3.14+