"""
Configuración base del agente inbound.
Permite fácil escalabilidad multi-tenant.
"""
from typing import Dict, Any
from pydantic import BaseModel, Field


class BANTCriteria(BaseModel):
    """Criterios de calificación BANT"""
    min_budget: int = Field(default=5000, description="Presupuesto mínimo en USD")
    max_budget: int = Field(default=100000, description="Presupuesto máximo en USD")
    valid_authorities: list[str] = Field(
        default=["CEO", "CTO", "Director", "Gerente", "Manager", "VP"],
        description="Roles con autoridad de decisión"
    )
    required_needs: list[str] = Field(
        default=["automatización", "CRM", "ventas", "marketing"],
        description="Necesidades que atendemos"
    )
    max_timeline_days: int = Field(default=90, description="Timeline máximo en días")


class AgentPersonality(BaseModel):
    """Personalidad del agente (configurable por cliente)"""
    name: str = Field(default="Ana", description="Nombre del agente")
    tone: str = Field(default="amigable y profesional", description="Tono de conversación")
    style: str = Field(default="casual pero educado", description="Estilo de comunicación")
    company_name: str = Field(default="Spicy", description="Nombre de la empresa")
    company_description: str = Field(
        default="empresa de soluciones tecnológicas",
        description="Descripción breve de la empresa"
    )


class TenantConfig(BaseModel):
    """Configuración por tenant/cliente - Fácilmente escalable"""
    tenant_id: str
    personality: AgentPersonality = Field(default_factory=AgentPersonality)
    bant_criteria: BANTCriteria = Field(default_factory=BANTCriteria)
    crm_endpoint: str = Field(default="mock", description="Endpoint del CRM")
    calendar_endpoint: str = Field(default="mock", description="Endpoint del calendario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "company_001",
                "personality": {
                    "name": "Ana",
                    "tone": "amigable y profesional",
                    "company_name": "Spicy"
                }
            }
        }


# Configuración default (para desarrollo)
DEFAULT_CONFIG = TenantConfig(
    tenant_id="default",
    personality=AgentPersonality(),
    bant_criteria=BANTCriteria()
)


def load_tenant_config(tenant_id: str) -> TenantConfig:
    """
    Carga configuración de un tenant.
    En producción, esto vendría de una BD.
    Por ahora retorna config default.
    """
    # TODO: Cargar desde BD/archivo según tenant_id
    return DEFAULT_CONFIG