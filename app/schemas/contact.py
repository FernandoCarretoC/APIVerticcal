from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re

class ContactCreate(BaseModel):
    """Schema para crear un contacto"""
    name: str = Field(..., min_length=1, max_length=255, description="Nombre completo del contacto")
    email: Optional[EmailStr] = Field(None, description="Email del contacto")
    phone: Optional[str] = Field(None, description="Teléfono del contacto (formato internacional)")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Permitir formato internacional con o sin +
        phone_pattern = r'^\+?[\d\s\-\(\)]{7,20}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Formato de teléfono inválido. Use formato internacional (ej: +57 300 123 4567)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Falcao García",
                "email": "falcao@verticcal.com",
                "phone": "+57 300 123 4567"
            }
        }

class ContactUpdate(BaseModel):
    """Schema para actualizar un contacto"""
    contact_identifier: str = Field(..., description="Nombre, email o ID del contacto")
    fields: dict = Field(..., description="Campos a actualizar")

    class Config:
        json_schema_extra = {
            "example": {
                "contact_identifier": "Falcao García",
                "fields": {
                    "phone": "+57 311 999 0000"
                }
            }
        }

class ContactNote(BaseModel):
    """Schema para agregar una nota a un contacto"""
    contact_identifier: str = Field(..., description="Nombre, email o ID del contacto")
    content: str = Field(..., min_length=1, description="Contenido de la nota")

    class Config:
        json_schema_extra = {
            "example": {
                "contact_identifier": "Falcao García",
                "content": "Cliente interesado en plan Premium"
            }
        }

class ContactResponse(BaseModel):
    """Schema para respuesta de contacto"""
    success: bool
    message: str
    contact_id: Optional[int] = None
    contact_url: Optional[str] = None
    data: Optional[dict] = None

class NoteResponse(BaseModel):
    """Schema para respuesta de nota"""
    success: bool
    message: str
    note_id: Optional[int] = None
    data: Optional[dict] = None