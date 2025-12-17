# 🧠 Agenda Inteligente (WhatsApp Backend)

Backend para una Agenda Inteligente completamente integrada con **WhatsApp**, diseñada para gestionar tu vida personal y profesional mediante lenguaje natural (texto y voz). Utiliza tecnologías de vanguardia como **FastAPI**, **Groq** (LLM Llama 3), **Pinecone** (Base de Datos Vectorial) y **HuggingFace** (Embeddings).

Ahora incluye soporte completo para **Notas de Voz**, **Recordatorios Automáticos** programados y una gestión avanzada de eventos.

## 🚀 Concepto

Imagina un asistente personal en WhatsApp que no solo "entiende" lo que dices, sino que recuerda el contexto, gestiona tu calendario y te avisa proactivamente. A diferencia de los bots tradicionales basados en reglas, este sistema utiliza IA Generativa para interpretar intenciones complejas.

### Capacidades Principales
- **Comprensión Multimodal**: Texto y Notas de Voz (transcripción automática con Whisper).
- **Gestión de Eventos Completa**: Crear, Leer, Actualizar, Borrar (CRUD) usando lenguaje natural.
- **Inteligencia Temporal**: Entiende "mañana", "el próximo viernes", "en dos semanas".
- **Memoria Semántica**: Busca eventos por contexto (ej: "médico") no solo por coincidencia exacta.
- **Proactividad**: Sistema de recordatorios automáticos vía Cron Jobs.

## 🛠️ Stack Tecnológico

-   **Backend**: Python 3.10+ con **FastAPI**.
-   **IA / LLM**:
    -   Razonamiento: **Groq** (`llama-3.3-70b-versatile`) para una respuesta ultrarrápida.
    -   Transcripción de Audio: **Groq** (`whisper-large-v3`) para notas de voz.
-   **Base de Datos**: **Pinecone** (Serverless) para almacenamiento de vectores y metadatos.
-   **Embeddings**: **HuggingFace Inference API** (`BAAI/bge-small-en-v1.5`) para vectorizar textos.
-   **Mensajería**: **WhatsApp Cloud API** (Meta).
-   **Infraestructura**: Desplegable en Render/Railway/Heroku.

## ✨ Funcionalidades y Uso

Interactúa con tu agenda como si hablaras con una persona real.

### 1. Gestión de Eventos

#### **Guardar (Save)**
Crea eventos especificando fecha y hora implícita o explícitamente.
-   *"Tengo dentista mañana a las 10"*
-   *"Recordar cumpleaños de Ana el 15 de Octubre, avísame 2 días antes"* (Configura recordatorio personalizado).
-   *"Reunión de equipo todos los lunes a las 9"* (Mencionar recurrencia para guardar contexto, aunque la gestión recurrente es manual por ahora).

#### **Consultar (Query)**
Recupera información usando búsqueda semántica.
-   *"¿Qué tengo hoy?"*
-   *"¿Cuándo era la cita del médico?"*
-   *"Ver agenda de esta semana"*

#### **Editar (Edit)**
Modifica eventos existentes. El sistema busca el evento más probable y aplica los cambios.
-   *"Cambiar la cita del médico a las 18:00"*
-   *"Mover la reunión de mañana al viernes"*
-   *"Corregir: el cumpleaños de Ana es el 16, no el 15"*

#### **Eliminar (Delete)**
Borra eventos específicos o resetea la agenda.
-   *"Borrar la reunión de ayer"*
-   *"Eliminar cita con el mecánico"*
-   **Borrado Total**:
    -   Usuario: *"Borrar todo"* o *"Resetear agenda"*
    -   Bot: Solicitará confirmación.
    -   Usuario: *"CONFIRMAR BORRADO TOTAL"* (Necesario para ejecutar la acción).

### 2. Notas de Voz 🎙️
¡Ya no necesitas escribir! Envía una nota de voz a tu bot.
-   El sistema descarga el audio automáticamente.
-   Lo transcribe usando el modelo **Whisper-v3**.
-   Procesa el texto transcrito como si fuera un mensaje escrito.
    -   *Ejemplo de audio*: "Agrégame una cena con Carlos para este sábado a las 9 de la noche".

### 3. Recordatorios y Listas
-   **Listar Pendientes**:
    -   *"Ver mis recordatorios"*
    -   *"¿Qué tengo pendiente?"*
-   **Ayuda**:
    -   *"Ayuda"*, *"Comandos"*, *"¿Qué puedes hacer?"* (Devuelve una guía rápida).

## ⚙️ Configuración Local

Sigue estos pasos para levantar el entorno de desarrollo.

### Prerrequisitos
-   Python 3.10+
-   Cuenta en **Groq Cloud** (API Key).
-   Cuenta en **Pinecone** (API Key e Índice creado).
-   Cuenta en **HuggingFace** (Token).
-   App en **Meta for Developers** (WhatsApp Cloud API configurado).

### Instalación

1.  **Clonar y crear entorno**:
    ```bash
    git clone <repo-url>
    cd agenda-whatsapp
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Variables de Entorno**:
    Crea un archivo `.env` en la raíz basado en `.env.example`:

    ```env
    # WhatsApp (Meta)
    VERIFY_TOKEN=tu_token_seguro_arbitrario
    WHATSAPP_PHONE_ID=1234567890
    WHATSAPP_TOKEN=EAAG... (Token de acceso permanente o temporal)

    # IA Services
    GROQ_API_KEY=gsk_...
    HUGGINGFACE_API_TOKEN=hf_...

    # Vector DB (Pinecone)
    PINECONE_API_KEY=pcsk_...
    PINECONE_INDEX_NAME=agenda-index
    ```

## ▶️ Ejecución y Pruebas

### 1. Servidor de Desarrollo
```bash
uvicorn main:app --reload
```
El servidor escuchará en `http://localhost:8000`.

### 2. Conectar con WhatsApp (Ngrok)
Para que WhatsApp pueda comunicarse con tu servidor local (webhook), necesitas un túnel HTTPS.
```bash
ngrok http 8000
```
-   Copia la URL HTTPS generada (ej: `https://abcd-123.ngrok-free.app`).
-   Ve al panel de desarrolladores de Meta -> WhatsApp -> Configuration.
-   En **Webhook URL** pon: `https://abcd-123.ngrok-free.app/webhook`.
-   En **Verify Token** pon el valor de `VERIFY_TOKEN` de tu `.env`.

### 3. Suite de Verificación
El proyecto incluye herramientas para garantizar la robustez.

-   **Check de Integridad**:
    Verifica conexión con todas las APIs (Groq, Pinecone, HF).
    ```bash
    python check_integrity.py
    ```

-   **Test Suite (End-to-End simulado)**:
    Corre pruebas automatizadas mocking de servicios para validar la lógica del bot.
    ```bash
    python test_suite.py
    ```

## ☁️ Despliegue en Producción

El archivo `Dockerfile` (o configuración base) está listo para despliegues ligeros.

1.  **Render / Railway**:
    -   Conecta tu repositorio.
    -   Configura las variables de entorno en el panel del servicio.
    -   Comando de inicio: `uvicorn main:app --host 0.0.0.0 --port 10000` (ajusta el puerto según corresponda).

2.  **Cron Job para Recordatorios**:
    Para que el bot te avise proactivamente, necesitas un servicio externo que "despierte" al bot.
    -   Usa **cron-job.org** (gratuito).
    -   Crea un job que llame a: `https://tu-app.onrender.com/reminders/check`
    -   Frecuencia: Cada 1 hora (o lo que desees).
    -   Timezone: Tu zona horaria local (ej: `Europe/Madrid`).

---
Desarrollado con ❤️ y mucha IA.
