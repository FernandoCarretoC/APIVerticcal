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
- **N8N**
- **Git**
- **API Key de modelo de IA**

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

# ⚙️ Integración del Workflow Conversacional con n8n

Este documento describe el proceso completo para ejecutar n8n, importar el workflow y conectarlo con una API local desarrollada en FastAPI.

---

## 1. Ejecutar n8n

### ▶️ Si tienes N8N instalado en Local

```bash
n8n start
```

Interfaz disponible en: http://localhost:5678

### 🟦 Si tienes n8n Cloud

Acceso directo: https://app.n8n.cloud

### 🐳 Docker

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

---

## 2. Importar el workflow

| Paso | Acción |
|------|--------|
| 1 | Abrir la interfaz de n8n |
| 2 | Ir a **Workflows** |
| 3 | Seleccionar **Add Workflow** o ícono "+" |
| 4 | Elegir **Import from File** |
| 5 | Cargar: `n8n/FlujoPruebaTecnica.json` |
| 6 | Confirmar importación |

El flujo aparecerá listo con todos los nodos preconfigurados.

---

## 3. Configurar el Chat Agent (Gemini)

El workflow se basa en un agente conversacional que usa IA para interpretar comandos.

### 🔧 Configuración del modelo

1. Abrir el nodo: **AI Agent / Chat Agent**
2. En **Model**, crear credenciales nuevas
3. **API Key** desde: https://makersuite.google.com/app/apikey
4. Modelo recomendado:

```
gemini-2.5-flash
```

5. Guardar

---

## 4. Ajustar endpoints en los HTTP Request

Los nodos HTTP deben apuntar correctamente a la API FastAPI según el entorno:

### 🖥️ n8n local: Configurar los nodos HTTP Request

```
http://0.0.0.0:8000/crm/contact
http://0.0.0.0:8000/crm/contact/note
```

### 🐳 Docker (macOS / Windows)

```
http://host.docker.internal:8000/crm/contact
http://host.docker.internal:8000/crm/contact/note
```

### 🐧 Docker (Linux)

```
http://172.17.0.1:8000/crm/contact
http://172.17.0.1:8000/crm/contact/note
```

### 🌐 n8n Cloud → API Local

Requiere túnel. Ejemplo con ngrok:

```bash
ngrok http 8000
```

ngrok generará una URL temporal del tipo:

```
https://xxxx-xx-xx.ngrok-free.app
```

Usar esa URL en todos los HTTP Request:

```
https://xxxx-xx-xx.ngrok-free.app/crm/contact
```

---

## 5. Probar el chat integrado

### 🧪 Procedimiento

1. Ubicar el nodo **Chat Trigger**
2. Clic en **Test Chat / Open Chat**
3. En la ventana emergente, enviar un mensaje de ejemplo como los siguientes:
```
1. “Crea a Ana Gómez con email ana.gomez@ejemplo.com y teléfono +57 315 222 3344.”
2. “Agrega una nota al contacto de Ana: ‘Solicita demo del plan Pro’”
3. “Actualiza el estado de Ana a ‘Qualified’ y su teléfono a +57 320 000 1122.”
```
4. El agente debe responder indicando que el flujo está funcionando.
4.1 Reenviar mensaje de ser necesario para activar flujo
