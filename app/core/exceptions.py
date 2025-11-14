class CRMException(Exception):
    """Exception base para errores relacionados con CRM"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class ContactNotFoundException(CRMException):
    """Excepción lanzada cuando no se encuentra un contacto"""
    def __init__(self, contact_identifier: str):
        self.contact_identifier = contact_identifier
        message = f"No se encontró el contacto: {contact_identifier}"
        super().__init__(message)

class DuplicateContactException(CRMException):
    """Excepción lanzada cuando se encuentran contactos duplicados"""
    def __init__(self, duplicates: list):
        self.duplicates = duplicates
        message = f"Se encontraron {len(duplicates)} contactos duplicados"
        super().__init__(message, {"duplicates": duplicates})

class ValidationException(CRMException):
    """Excepción lanzada para errores de validación de datos"""
    def __init__(self, field: str, message: str):
        super().__init__(f"Error de validación en {field}: {message}", {"field": field})