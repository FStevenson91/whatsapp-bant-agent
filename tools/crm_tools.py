"""
Herramientas de integración con CRM (MongoDB mock).
En producción, esto se conectará al CRM real.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


# Archivo mock para simular BD
MOCK_DB_FILE = Path(__file__).parent.parent / "data" / "crm_mock.json"


def _ensure_data_dir():
    """Crea el directorio de datos si no existe"""
    MOCK_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MOCK_DB_FILE.exists():
        MOCK_DB_FILE.write_text(json.dumps({"prospects": []}, indent=2))


def _load_mock_db() -> Dict[str, Any]:
    """Carga la BD mock"""
    _ensure_data_dir()
    return json.loads(MOCK_DB_FILE.read_text())


def _save_mock_db(data: Dict[str, Any]):
    """Guarda la BD mock"""
    _ensure_data_dir()
    MOCK_DB_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def save_to_crm(
    name: str,
    phone: str,
    email: str,
    budget: str,
    authority: str,
    need: str,
    timeline: str,
    qualification_status: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Guarda información del prospecto calificado en el CRM.
    
    Args:
        name: Nombre del prospecto
        phone: Teléfono (WhatsApp)
        email: Email del prospecto
        budget: Presupuesto disponible
        authority: Rol/autoridad del prospecto
        need: Necesidad identificada
        timeline: Timeline para implementación
        qualification_status: "QUALIFIED" o "NOT_QUALIFIED"
        notes: Notas adicionales
    
    Returns:
        Dict con resultado de la operación
    """
    try:
        db = _load_mock_db()
        
        prospect = {
            "id": f"prospect_{len(db['prospects']) + 1}",
            "name": name,
            "phone": phone,
            "email": email,
            "bant": {
                "budget": budget,
                "authority": authority,
                "need": need,
                "timeline": timeline
            },
            "qualification_status": qualification_status,
            "notes": notes or "",
            "created_at": datetime.now().isoformat(),
            "source": "whatsapp_inbound"
        }
        
        db["prospects"].append(prospect)
        _save_mock_db(db)
        
        return {
            "success": True,
            "prospect_id": prospect["id"],
            "message": f"Prospecto {name} guardado exitosamente en CRM"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al guardar en CRM"
        }


def get_prospect_info(phone: str) -> Optional[Dict[str, Any]]:
    """
    Busca información de un prospecto por teléfono.
    Útil para conversaciones recurrentes.
    
    Args:
        phone: Número de teléfono del prospecto
    
    Returns:
        Dict con info del prospecto o None si no existe
    """
    try:
        db = _load_mock_db()
        
        for prospect in db["prospects"]:
            if prospect["phone"] == phone:
                return prospect
        
        return None
        
    except Exception as e:
        print(f"Error buscando prospecto: {e}")
        return None