from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import sys
import logging
from dotenv import load_dotenv

from services.llm_service import process_message
from services.memory_service import search_relevant_context, save_memory
from services.whatsapp_service import send_whatsapp_message
from services.reminder_service import get_upcoming_reminders, mark_reminder_sent, format_reminder_message

load_dotenv()

# Configurar logging para Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# --- AÑADE ESTO A TU MAIN.PY ---
@app.get("/")
def home():
    return "¡Hola! El bot está vivo y funcionando 🤖"

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verificación del Webhook por parte de Meta."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            raise HTTPException(status_code=403, detail="Verification token mismatch")
    return HTTPException(status_code=400, detail="Missing parameters")

@app.post("/webhook")
async def handle_message(request: Request):
    """Recibe mensajes de WhatsApp."""
    try:
        data = await request.json()
        logger.info(f"DEBUG Webhook Payload: {data}")
        
        # Estructura típica de webhook de WhatsApp Cloud API
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            logger.info(f"Mensaje recibido: {msg}")
            if msg.get("type") == "text":
                fw_id = msg.get("from") # Número del usuario
                msg_body = msg.get("text", {}).get("body", "")
                logger.info(f"Texto: {msg_body} de {fw_id}")
                
                # --- LÓGICA PRINCIPAL ---
                
                # 1. Buscar contexto en memoria (RAG)
                memory_hits = search_relevant_context(msg_body)
                logger.info(f"Memory hits: {memory_hits}")
                
                # 2. Procesar con LLM (Groq)
                decision = process_message(msg_body, memory_hits)
                logger.info(f"Decision LLM: {decision}")
                
                action = decision.get("action")
                response_text = decision.get("response_text")
                
                # 3. Ejecutar acción
                if action == "SAVE":
                    event_data = decision.get("data")
                    if event_data:
                        # Añadir número de teléfono para recordatorios
                        event_data["user_phone"] = fw_id
                        saved = save_memory(msg_body, event_data)
                        if not saved:
                            response_text = "Tuve un error guardando el recuerdo en mi memoria."
                
                # 4. Responder al usuario
                logger.info(f"Enviando respuesta a {fw_id}: {response_text}")
                send_whatsapp_message(fw_id, response_text)
                
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error Webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/reminders/check")
async def check_reminders():
    """
    Endpoint para cron job - verifica y envía recordatorios pendientes.
    Llamar cada hora desde cron-job.org o similar.
    """
    try:
        logger.info("Iniciando verificación de recordatorios...")
        
        reminders = get_upcoming_reminders()
        sent_count = 0
        
        for reminder in reminders:
            user_phone = reminder.get('user_phone')
            event_id = reminder.get('id')
            
            if user_phone and event_id:
                message = format_reminder_message(reminder)
                logger.info(f"Enviando recordatorio a {user_phone}: {reminder.get('nombre')}")
                
                send_whatsapp_message(user_phone, message)
                mark_reminder_sent(event_id)
                sent_count += 1
        
        logger.info(f"Recordatorios enviados: {sent_count}")
        return {"status": "ok", "reminders_sent": sent_count}
        
    except Exception as e:
        logger.error(f"Error en check_reminders: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
