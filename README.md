# 🚀 API - FastAPI + Pipedrive
API REST para integración conversacional con Pipedrive CRM mediante agente n8n.

---

## ✨ Características

- ✔️ Crear contactos con validación y verificación de duplicados (idempotencia)
- ✔️ Agregar notas a contactos existentes
- ✔️ Actualizar campos de contactos
- ✔️ Desambiguación inteligente para contactos con nombres similares
- ✔️ Validaciones server-side para email y teléfono
- ✔️ Manejo robusto de errores con mensajes claros
- ✔️ Arquitectura limpia y escalable

---

## 📋 Requisitos

- **Python 3.8+**
- **Cuenta de Pipedrive** con API Token

---

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone <tu_repo_url>
cd <nombre_del_repo>
```
### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate        # Linux / MacOS
# En Windows:
# venv\Scripts\activate
```
### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```
### 4. Configurar variables de entorno
```bash
cp .env.example .env
```
Edita .env y agrega tu token:
```bash
PIPEDRIVE_API_TOKEN=tu_token_real_aqui
```
¿Dónde obtener el API Token?
Ingresa a tu cuenta de Pipedrive
Ve a Settings → Personal preferences → API
Copia tu API Token personal

---

### ▶️ Ejecución
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
La API estará disponible en:
👉 http://localhost:8000

---

### 📚 Documentación API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
---
### 🔌 Endpoints
#### 1. Health Check
GET /health
Respuesta:
```bash
{
  "status": "healthy",
  "service": "CRM Integration API",
  "version": "1.0.0",
  "pipedrive_configured": true
}
```
#### 2. Crear Contacto
POST /crm/contact
Body:
```bash
{
  "status": "healthy",
  "service": "CRM Integration API",
  "version": "1.0.0",
  "pipedrive_configured": true
}
```
Respuesta Exitosa:
```bash
{
  "success": true,
  "message": "Contacto 'Falcao García' creado exitosamente en Pipedrive",
  "contact_id": 123,
  "contact_url": "https://app.pipedrive.com/person/123",
  "data": {
    "id": 123,
    "name": "Falcao García",
    "email": "falcao@verticcal.com",
    "phone": "+57 300 123 4567",
    "is_new": true
  }
}
```
Características:
- ✔️ Validación de email
- ✔️ Validación de teléfono internacional
- ✔️ Idempotencia (no crea duplicados)


#### 3. Agregar Nota a Contacto
POST /crm/contact/note
Body:
```bash
{
  "contact_identifier": "Falcao García",
  "content": "Cliente interesado en plan Premium"
}
```
Respuesta Exitosa:
```bash
{
  "success": true,
  "message": "Nota agregada exitosamente al contacto 'Falcao García'",
  "note_id": 456,
  "data": {
    "note_id": 456,
    "contact_id": 123,
    "contact_name": "Falcao García",
    "content": "Cliente interesado en plan Premium",
    "created_at": "2025-11-13 10:30:00"
  }
}
```
contact_identifier puede ser:
- Nombre del contacto
- Email
- ID del contacto

#### 4. Actualizar Contacto
PATCH /crm/contact
Body (actualizar teléfono):
```bash
{
  "contact_identifier": "Falcao García",
  "fields": {
    "phone": "+57 311 999 0000"
  }
}
```
Body (actualizar múltiples campos):
```bash
{
  "contact_identifier": "falcao@verticcal.com",
  "fields": {
    "phone": "+57 311 999 0000",
    "name": "Radamel Falcao García"
  }
}
```
Respuesta Exitosa:
```bash
{
  "success": true,
  "message": "Contacto 'Falcao García' actualizado exitosamente",
  "contact_id": 123,
  "contact_url": "https://app.pipedrive.com/person/123",
  "data": {
    "id": 123,
    "name": "Falcao García",
    "updated_fields": {
      "phone": "+57 311 999 0000"
    },
    "update_time": "2025-11-13 10:35:00"
  }
}

```
--- 

### ⚠️ Manejo de Errores
❌ 404 – Contacto No Encontrado
```bash
{
  "success": false,
  "error": "No se encontró el contacto: Juan Pérez",
  "contact_identifier": "Juan Pérez"
}
```
❌ 409 – Contactos Duplicados
```bash
{
  "success": false,
  "error": "Se encontraron 2 contactos duplicados",
  "duplicates": [
    {
      "id": 123,
      "name": "Falcao García",
      "email": "falcao@verticcal.com"
    },
    {
      "id": 124,
      "name": "Falcao García",
      "email": "falcao@otro.com"
    }
  ]
}
```
Solución: usar el ID numérico del contacto.

❌ 400 – Error de Validación
```bash
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "phone"],
      "msg": "Formato de teléfono inválido. Use formato internacional (ej: +57 300 123 4567)"
    }
  ]
}
```

