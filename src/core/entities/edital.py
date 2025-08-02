"""Define a entidade Edital, que representa um edital da UEPA."""
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field


class Edital(BaseModel):
    """Representa um edital da UEPA."""
    title: str = Field(..., min_length=1, description="Título do edital")
    link: HttpUrl = Field(..., description="Link para o edital")
    date: Optional[str] = Field("Data não disponível", description="Data de publicação do edital")
    hash: str = Field(..., description="Hash MD5 único do edital")

    class Config:
        """Configurações para o modelo Pydantic."""
        frozen = True
