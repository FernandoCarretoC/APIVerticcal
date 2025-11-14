from fastapi import APIRouter, HTTPException, status
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactNote,
    ContactResponse,
    NoteResponse
)
from app.services.pipedrive_service import PipedriveService
from app.core.exceptions import (
    CRMException,
    ContactNotFoundException,
    DuplicateContactException
)

crm_router = APIRouter()

@crm_router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo contacto",
    description="Crea un nuevo contacto en Pipedrive. Implementa idempotencia verificando duplicados."
)
async def create_contact(contact: ContactCreate):
    """
    Crea un nuevo contacto en Pipedrive.

    - **name**: Nombre completo del contacto (requerido)
    - **email**: Email del contacto (opcional)
    - **phone**: Teléfono en formato internacional (opcional)

    La API verifica duplicados antes de crear para evitar contactos repetidos.
    """
    service = PipedriveService()

    try:
        # Idempotencia: Verificar si el contacto ya existe
        existing = await service.check_duplicate_contact(
            contact.name,
            contact.email
        )

        if existing:
            return ContactResponse(
                success=True,
                message=f"El contacto '{contact.name}' ya existe. Se retorna el contacto existente.",
                contact_id=existing.get("id"),
                contact_url=service.get_person_url(existing.get("id")),
                data={
                    "id": existing.get("id"),
                    "name": existing.get("name"),
                    "email": existing.get("email", [{}])[0].get("value") if existing.get("email") else None,
                    "phone": existing.get("phone", [{}])[0].get("value") if existing.get("phone") else None,
                    "is_new": False
                }
            )

        # Preparar datos del nuevo contacto
        person_data = {
            "name": contact.name
        }

        if contact.email:
            person_data["email"] = [{"value": contact.email}]

        if contact.phone:
            person_data["phone"] = [{"value": contact.phone}]

        # Crear nuevo contacto en Pipedrive
        result = await service.create_person(person_data)

        return ContactResponse(
            success=True,
            message=f"Contacto '{contact.name}' creado exitosamente en Pipedrive",
            contact_id=result.get("id"),
            contact_url=service.get_person_url(result.get("id")),
            data={
                "id": result.get("id"),
                "name": result.get("name"),
                "email": result.get("email", [{}])[0].get("value") if result.get("email") else None,
                "phone": result.get("phone", [{}])[0].get("value") if result.get("phone") else None,
                "is_new": True
            }
        )

    except CRMException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@crm_router.post(
    "/contact/note",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar nota a un contacto",
    description="Agrega una nota a un contacto existente en Pipedrive"
)
async def add_contact_note(note: ContactNote):
    """
    Agrega una nota a un contacto existente.

    - **contact_identifier**: Nombre, email o ID del contacto
    - **content**: Contenido de la nota

    La API busca el contacto por nombre, email o ID y maneja desambiguación.
    """
    service = PipedriveService()

    try:
        # Encontrar contacto
        contact = await service.find_contact_by_identifier(note.contact_identifier)

        if not contact:
            raise ContactNotFoundException(note.contact_identifier)

        contact_id = contact.get("id")
        contact_name = contact.get("name")

        # Agregar nota al contacto
        result = await service.add_note(contact_id, note.content)

        return NoteResponse(
            success=True,
            message=f"Nota agregada exitosamente al contacto '{contact_name}'",
            note_id=result.get("id"),
            data={
                "note_id": result.get("id"),
                "contact_id": contact_id,
                "contact_name": contact_name,
                "content": note.content,
                "created_at": result.get("add_time")
            }
        )

    except ContactNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el contacto: {note.contact_identifier}"
        )
    except DuplicateContactException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Se encontraron múltiples contactos. Por favor, especifique cuál usando el ID.",
                "duplicates": e.duplicates
            }
        )
    except CRMException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@crm_router.patch(
    "/contact",
    response_model=ContactResponse,
    summary="Actualizar un contacto",
    description="Actualiza campos de un contacto existente en Pipedrive"
)
async def update_contact(update: ContactUpdate):
    """
    Actualiza un contacto existente en Pipedrive.

    - **contact_identifier**: Nombre, email o ID del contacto
    - **fields**: Diccionario con los campos a actualizar

    Campos comunes: name, email, phone, org_id, owner_id, etc.
    """
    service = PipedriveService()

    try:
        # Encontrar contacto
        contact = await service.find_contact_by_identifier(update.contact_identifier)

        if not contact:
            raise ContactNotFoundException(update.contact_identifier)

        contact_id = contact.get("id")
        contact_name = contact.get("name")

        # Actualizar contacto
        result = await service.update_person(contact_id, update.fields)

        return ContactResponse(
            success=True,
            message=f"Contacto '{contact_name}' actualizado exitosamente",
            contact_id=contact_id,
            contact_url=service.get_person_url(contact_id),
            data={
                "id": result.get("id"),
                "name": result.get("name"),
                "updated_fields": update.fields,
                "update_time": result.get("update_time")
            }
        )

    except ContactNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el contacto: {update.contact_identifier}"
        )
    except DuplicateContactException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Se encontraron múltiples contactos. Por favor, especifique cuál usando el ID.",
                "duplicates": e.duplicates
            }
        )
    except CRMException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )