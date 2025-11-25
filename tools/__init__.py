"""
Herramientas del agente inbound.
"""
from .crm_tools import save_to_crm, get_prospect_info
from .calendar_tools import schedule_meeting, check_availability

__all__ = [
    'save_to_crm',
    'get_prospect_info',
    'schedule_meeting',
    'check_availability'
]