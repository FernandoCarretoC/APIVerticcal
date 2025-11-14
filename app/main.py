from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import crm_router
from app.core.config import settings
from app.core.exceptions import CRMException, ContactNotFoundException, DuplicateContactException

app = FastAPI(
    title="API - FASTAPI - Integración con Pipedrive CRM",
    description="API para integración con Pipedrive CRM mediante agente conversacional n8n",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(CRMException)
async def crm_exception_handler(request, exc: CRMException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details
        }
    )

@app.exception_handler(ContactNotFoundException)
async def contact_not_found_handler(request, exc: ContactNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": exc.message,
            "contact_identifier": exc.contact_identifier
        }
    )

@app.exception_handler(DuplicateContactException)
async def duplicate_contact_handler(request, exc: DuplicateContactException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": exc.message,
            "duplicates": exc.duplicates
        }
    )

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "API - FASTAPI - Integración con Pipedrive CRM",
        "version": "1.0.0",
        "pipedrive_configured": bool(settings.PIPEDRIVE_API_TOKEN)
    }

app.include_router(crm_router, prefix="/crm", tags=["CRM"])

