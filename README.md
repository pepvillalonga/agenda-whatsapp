# 🧠 Agenda Inteligente (WhatsApp Backend)

Backend para Agenda Inteligente que funciona a través de WhatsApp, utilizando **FastAPI**, **Groq** (LLM), **Pinecone** (Memoria Vectorial) y **HuggingFace** (Embeddings).

Ahora incluye un sistema de **Recordatorios Automáticos** programados y gestión avanzada de eventos.

## 🚀 Stack Tecnológico

-   **Backend**: Python (FastAPI).
-   **IA Chat**: Groq (`llama-3.3-70b-versatile`).
-   **Memoria (Vectores)**: Pinecone (Serverless).
-   **Embeddings**: HuggingFace Inference API (`BAAI/bge-small-en-v1.5`).
-   **Mensajería**: WhatsApp Cloud API.
-   **Tasks**: Cron jobs externos.

## ✨ Funcionalidades

Interactúa con tu agenda usando lenguaje natural. Comandos soportados:

-   **Guardar Eventos**:
    -   "Tengo dentista mañana a las 10"
    -   "Recordar cumpleaños de Ana el 15 de Octubre"
-   **Consultar Agenda**:
    -   "¿Qué tengo hoy?"
    -   "¿Cuándo es la cita del médico?"
-   **Editar Eventos**:
    -   "Cambiar la cita del médico a las 18:00"
    -   "Mover la reunión de mañana al viernes"
-   **Eliminar Eventos**:
    -   "Borrar la reunión de ayer"
    -   "Eliminar cita dentista"
    -   "Borrar todo" (Requiere confirmación)
-   **Listar Pendientes**:
    -   "Ver mis recordatorios"
    -   "Listar todo"

## ⚙️ Configuración

1.  **Entorno Virtual**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  **Dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Variables de Entorno**:
    Crea un archivo `.env` con las siguientes claves:
    ```env
    # WhatsApp Configuration
    VERIFY_TOKEN=tu_token_verificacion_personal
    WHATSAPP_PHONE_ID=tu_id_telefono
    WHATSAPP_TOKEN=tu_token_acceso_whatsapp

    # AI Services
    GROQ_API_KEY=gsk_...
    HUGGINGFACE_API_TOKEN=hf_...

    # Database
    PINECONE_API_KEY=pcsk_...
    PINECONE_INDEX_NAME=nombre_indice
    ```

## ▶️ Ejecución

### Servidor Local
Levanta el servidor con Uvicorn para desarrollo:
```bash
uvicorn main:app --reload
```
El servidor correrá en `http://localhost:8000`.

### Tests de Integridad
Verifica que todos los servicios y credenciales funcionen correctamente:
```bash
python check_integrity.py
```

### Suite de Pruebas
Ejecuta la suite completa de tests automatizados (mocking de servicios externos):
```bash
python test_suite.py
```

## 🌐 Exponer a Internet (Webhook)

Para conectar con WhatsApp necesitas una URL pública (HTTPS).

1.  **Ngrok** (Desarrollo):
    ```bash
    ngrok http 8000
    ```
2.  **Configura Meta Developer Portal**:
    -   **Callback URL**: `https://tu-url-ngrok.app/webhook`
    -   **Verify Token**: El valor de `VERIFY_TOKEN` en tu `.env`.

## ⏰ Recordatorios Automáticos (Cron Job)

El sistema soporta recordatorios proactivos (ej: "Tienes dentista mañana").

1.  Despliega tu backend (Render, Railway, Heroku).
2.  Configura un **Cron Job** (ej. cron-job.org) para llamar a tu endpoint cada hora:
    -   **URL**: `https://tu-app-desplegada.onrender.com/reminders/check`
    -   **Método**: GET
    -   **Timezone**: Europe/Madrid

---
*Backend listo para producción con arquitectura modular.*
