# 🧠 Agenda Inteligente (WhatsApp Backend)

Backend para Agenda Inteligente que funciona a través de WhatsApp, utilizando **FastAPI**, **Groq**, **Pinecone** y **HuggingFace**.

## 🚀 Stack Tecnológico

-   **Backend**: Python (FastAPI).
-   **IA Chat**: Groq (`llama3-8b-8192`).
-   **Memoria (Vectores)**: Pinecone (Serverless).
-   **Embeddings**: HuggingFace Inference API (`all-MiniLM-L6-v2`).
-   **Mensajería**: WhatsApp Cloud API.

## �️ Configuración

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
    -   Renombra `.env.example` a `.env`.
    -   Rellena las claves de API (Groq, Pinecone, HF, Meta).

## ▶️ Ejecución Local

Levanta el servidor FastAPI:
```bash
python main.py
```
O con Uvicorn directo:
```bash
uvicorn main:app --reload
```

## 🌐 Exponer a Internet (Webhook)

Para conectar con WhatsApp necesitas una URL pública (HTTPS). Usa **ngrok**:

```bash
ngrok http 8000
```
Copia la URL generada (ej: `https://xxxx.ngrok-free.app`) y configúrala en el **Meta Developer Portal**:
-   **Callback URL**: `https://xxxx.ngrok-free.app/webhook`
-   **Verify Token**: El que definiste en `.env`.

---
*Backend listo para producción con arquitectura modular.*
