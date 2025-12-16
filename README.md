# 🧠 Agenda Inteligente (WhatsApp Backend)

Backend para Agenda Inteligente que funciona a través de WhatsApp, utilizando **FastAPI**, **Groq** (LLM), **Pinecone** (Memoria Vectorial) y **HuggingFace** (Embeddings).

Ahora incluye un sistema de **Recordatorios Automáticos** programados.

## 🚀 Stack Tecnológico

-   **Backend**: Python (FastAPI).
-   **IA Chat**: Groq (`llama-3.3-70b-versatile`).
-   **Memoria (Vectores)**: Pinecone (Serverless).
-   **Embeddings**: HuggingFace Inference API (`BAAI/bge-small-en-v1.5`).
-   **Mensajería**: WhatsApp Cloud API.
-   **Tasks**: Cron jobs externos.

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

## ▶️ Ejecución Local

Levanta el servidor con Uvicorn:
```bash
uvicorn main:app --reload
```
El servidor correrá en `http://localhost:8000`.

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

El sistema soporta recordatorios proactivos (ej: "Tienes dentista mañana"). Para que funcionen, necesitas un "trigger" externo que despierte al bot periódicamente.

1.  Despliega tu backend en un servicio como **Render**, **Railway** o **Heroku**.
2.  Usa un servicio de Cron gratuito como [cron-job.org](https://cron-job.org/).
3.  Crea un nuevo Cron Job:
    -   **URL**: `https://tu-app-desplegada.onrender.com/reminders/check`
    -   **Método**: GET
    -   **Frecuencia**: Cada 1 hora (o cada 30 min).
    -   **Timezone**: Europe/Madrid (importante para que no te despierte de madrugada).

### Cómo funciona:
-   El usuario dice: *"Recuérdame la cita del médico mañana"*.
-   El LLM guarda el evento y configura `reminder_days_before: 1`.
-   El Cron Job llama a `/reminders/check` cada hora.
-   El sistema revisa si hoy es el día de avisar (Fecha Evento - 1 día).
-   Si coincide, envía un WhatsApp proactivo al usuario.

---
*Backend listo para producción con arquitectura modular.*
