import httpx
from typing import Optional, List
from app.core.config import settings
from app.core.exceptions import (
    CRMException,
    ContactNotFoundException,
    DuplicateContactException
)

class PipedriveService:
    """Servicio para interactuar con la API de Pipedrive"""

    def __init__(self):
        self.base_url = settings.PIPEDRIVE_API_URL
        self.api_token = settings.PIPEDRIVE_API_TOKEN
        self.timeout = settings.REQUEST_TIMEOUT

    def _get_headers(self) -> dict:
        """Obtener encabezados comunes para las solicitudes"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _get_params(self, extra_params: dict = None) -> dict:
        """Obtener parámetros de consulta incluyendo el token de API"""
        params = {"api_token": self.api_token}
        if extra_params:
            params.update(extra_params)
        return params

    async def _make_request(
            self,
            method: str,
            endpoint: str,
            data: dict = None,
            params: dict = None
    ) -> dict:
        """Hacer una solicitud HTTP a la API de Pipedrive"""
        url = f"{self.base_url}/{endpoint}"
        request_params = self._get_params(params)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=request_params,
                    headers=self._get_headers()
                )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            raise CRMException(
                f"Error en Pipedrive API: {e.response.status_code}",
                {"detail": error_detail, "status_code": e.response.status_code}
            )
        except httpx.RequestError as e:
            raise CRMException(
                f"Error de conexión con Pipedrive: {str(e)}",
                {"error_type": type(e).__name__}
            )

    async def search_persons(self, term: str) -> List[dict]:
        """Buscar personas por término (nombre o email)"""
        try:
            response = await self._make_request(
                "GET",
                "persons/search",
                params={"term": term, "fields": "name,email", "exact_match": "false"}
            )

            if response.get("success") and response.get("data"):
                items = response["data"].get("items", [])
                return [item.get("item", {}) for item in items]
            return []

        except CRMException:
            return []

    async def find_contact_by_identifier(self, identifier: str) -> Optional[dict]:
        """
        Encuentra un contacto por nombre, email o ID. Maneja desambiguación y errores.
        Retorna un objeto persona completo si se encuentra un único contacto.
        """
        #  Intentar buscar por ID primero
        if identifier.isdigit():
            try:
                return await self.get_person(int(identifier))
            except ContactNotFoundException:
                # Si no se encuentra por ID, continuar con búsqueda por nombre/email
                pass

        # Buscar por nombre o email
        results = await self.search_persons(identifier)

        if not results:
            raise ContactNotFoundException(identifier)

        # Encontrar coincidencias exactas
        exact_matches = []
        for r in results:
            is_email_match = r.get("emails") and any(e.lower() == identifier.lower() for e in r["emails"])
            is_name_match = r.get("name", "").lower() == identifier.lower()
            if is_email_match or is_name_match:
                exact_matches.append(r)

        # Procesar coincidencias exactas
        if exact_matches:
            unique_exact_matches = list({m['id']: m for m in exact_matches}.values())
            if len(unique_exact_matches) == 1:
                return await self.get_person(unique_exact_matches[0]["id"])
            elif len(unique_exact_matches) > 1:
                raise DuplicateContactException([
                    {"id": r.get("id"), "name": r.get("name"), "email": r.get("emails")[0] if r.get("emails") else None}
                    for r in unique_exact_matches
                ])

        # Si no hay coincidencias exactas, manejar resultados parciales
        if len(results) == 1:
            return await self.get_person(results[0]["id"])

        if len(results) > 1:
            raise DuplicateContactException([
                {"id": r.get("id"), "name": r.get("name"), "email": r.get("emails")[0] if r.get("emails") else None}
                for r in results
            ])

        return None # No se encontró ningún contacto único

    async def check_duplicate_contact(self, name: str, email: Optional[str]) -> Optional[dict]:
        """Revisar si existe un contacto duplicado por nombre o email"""
        found_person_id = None
        if email:
            results = await self.search_persons(email)
            for r in results:
                if r.get("emails") and any(e.lower() == email.lower() for e in r["emails"]):
                    found_person_id = r.get("id")
                    break

        if not found_person_id:
            results = await self.search_persons(name)
            for r in results:
                if r.get("name", "").lower() == name.lower():
                    found_person_id = r.get("id")
                    break

        if found_person_id:
            try:
                return await self.get_person(found_person_id)
            except ContactNotFoundException:
                return None

        return None

    async def create_person(self, person_data: dict) -> dict:
        """Crear una persona en Pipedrive"""
        response = await self._make_request(
            "POST",
            "persons",
            data=person_data
        )

        if not response.get("success"):
            raise CRMException("No se pudo crear el contacto en Pipedrive", response)

        return response.get("data", {})

    async def get_person(self, person_id: int) -> dict:
        """Obtener una persona por ID"""
        response = await self._make_request(
            "GET",
            f"persons/{person_id}"
        )

        if not response.get("success"):
            raise ContactNotFoundException(str(person_id))

        return response.get("data", {})

    async def update_person(self, person_id: int, update_data: dict) -> dict:
        """Actualizar una persona por ID"""
        response = await self._make_request(
            "PUT",
            f"persons/{person_id}",
            data=update_data
        )

        if not response.get("success"):
            raise CRMException(
                f"No se pudo actualizar el contacto {person_id}",
                response
            )

        return response.get("data", {})

    async def add_note(self, person_id: int, content: str) -> dict:
        """Agregar una nota a una persona"""
        note_data = {
            "content": content,
            "person_id": person_id
        }

        response = await self._make_request(
            "POST",
            "notes",
            data=note_data
        )

        if not response.get("success"):
            raise CRMException(
                f"No se pudo crear la nota para el contacto {person_id}",
                response
            )

        return response.get("data", {})

    def get_person_url(self, person_id: int) -> str:
        """Obtener la URL del contacto en Pipedrive"""
        return f"https://app.pipedrive.com/person/{person_id}"