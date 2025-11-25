"""
Herramientas de calendario (Google Calendar mock).
En producción, esto se conectará a Google Calendar API.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


# Archivo mock para simular calendario
MOCK_CALENDAR_FILE = Path(__file__).parent.parent / "data" / "calendar_mock.json"


def _ensure_data_dir():
    """Crea el directorio de datos si no existe"""
    MOCK_CALENDAR_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not MOCK_CALENDAR_FILE.exists():
        MOCK_CALENDAR_FILE.write_text(json.dumps({"meetings": []}, indent=2))


def _load_mock_calendar() -> Dict[str, Any]:
    """Carga el calendario mock"""
    _ensure_data_dir()
    return json.loads(MOCK_CALENDAR_FILE.read_text())


def _save_mock_calendar(data: Dict[str, Any]):
    """Guarda el calendario mock"""
    _ensure_data_dir()
    MOCK_CALENDAR_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def check_availability(date: str, time: str) -> Dict[str, Any]:
    """
    Verifica disponibilidad en el calendario.
    
    Args:
        date: Fecha en formato YYYY-MM-DD
        time: Hora en formato HH:MM
    
    Returns:
        Dict indicando si está disponible
    """
    try:
        calendar = _load_mock_calendar()
        
        # Verifica si ya hay una reunión en ese horario
        for meeting in calendar["meetings"]:
            if meeting["date"] == date and meeting["time"] == time:
                return {
                    "available": False,
                    "message": f"Ya hay una reunión agendada el {date} a las {time}",
                    "suggested_times": _get_available_slots(date)
                }
        
        return {
            "available": True,
            "message": f"Horario disponible: {date} a las {time}"
        }
        
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "message": "Error verificando disponibilidad"
        }


def schedule_meeting(
    prospect_name: str,
    prospect_phone: str,
    prospect_email: str,
    date: str,
    time: str,
    duration_minutes: int = 30,
    meeting_type: str = "Llamada de descubrimiento"
) -> Dict[str, Any]:
    """
    Agenda una reunión en el calendario.
    
    Args:
        prospect_name: Nombre del prospecto
        prospect_phone: Teléfono del prospecto
        prospect_email: Email del prospecto
        date: Fecha en formato YYYY-MM-DD
        time: Hora en formato HH:MM
        duration_minutes: Duración en minutos
        meeting_type: Tipo de reunión
    
    Returns:
        Dict con resultado de la operación
    """
    try:
        # Verifica disponibilidad primero
        availability = check_availability(date, time)
        if not availability["available"]:
            return {
                "success": False,
                "message": availability["message"],
                "suggested_times": availability.get("suggested_times", [])
            }
        
        calendar = _load_mock_calendar()
        
        meeting = {
            "id": f"meeting_{len(calendar['meetings']) + 1}",
            "prospect_name": prospect_name,
            "prospect_phone": prospect_phone,
            "prospect_email": prospect_email,
            "date": date,
            "time": time,
            "duration_minutes": duration_minutes,
            "meeting_type": meeting_type,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "meeting_link": f"https://meet.google.com/mock-{len(calendar['meetings']) + 1}"  # Mock link
        }
        
        calendar["meetings"].append(meeting)
        _save_mock_calendar(calendar)
        
        return {
            "success": True,
            "meeting_id": meeting["id"],
            "meeting_link": meeting["meeting_link"],
            "message": f"Reunión agendada exitosamente para el {date} a las {time}",
            "details": {
                "date": date,
                "time": time,
                "duration": f"{duration_minutes} minutos",
                "type": meeting_type
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al agendar reunión"
        }


def _get_available_slots(date: str, num_slots: int = 3) -> List[str]:
    """
    Genera horarios disponibles sugeridos.
    Simplificado para el mock.
    """
    base_times = ["10:00", "14:00", "16:00"]
    return base_times[:num_slots]


def get_upcoming_meetings(days_ahead: int = 7) -> List[Dict[str, Any]]:
    """
    Obtiene reuniones próximas.
    Útil para evitar conflictos.
    
    Args:
        days_ahead: Días hacia adelante a consultar
    
    Returns:
        Lista de reuniones próximas
    """
    try:
        calendar = _load_mock_calendar()
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        upcoming = []
        for meeting in calendar["meetings"]:
            meeting_date = datetime.fromisoformat(meeting["date"]).date()
            if today <= meeting_date <= future_date:
                upcoming.append(meeting)
        
        return upcoming
        
    except Exception as e:
        print(f"Error obteniendo reuniones: {e}")
        return []