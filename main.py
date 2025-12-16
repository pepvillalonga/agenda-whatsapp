from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv

from services.llm_service import process_message
from services.memory_service import search_relevant_context, save_memory
from services.whatsapp_service import send_whatsapp_message

load_dotenv()

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
        print(f"DEBUG Webhook Payload: {data}")
        
        # Estructura típica de webhook de WhatsApp Cloud API
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if messages:
            msg = messages[0]
            if msg.get("type") == "text":
                fw_id = msg.get("from") # Número del usuario
                msg_body = msg.get("text", {}).get("body", "")
                
                # --- LÓGICA PRINCIPAL ---
                
                # 1. Buscar contexto en memoria (RAG)
                memory_hits = search_relevant_context(msg_body)
                
                # 2. Procesar con LLM (Groq)
                decision = process_message(msg_body, memory_hits)
                
                action = decision.get("action")
                response_text = decision.get("response_text")
                
                # 3. Ejecutar acción
                if action == "SAVE":
                    event_data = decision.get("data")
                    if event_data:
                        saved = save_memory(msg_body, event_data)
                        if not saved:
                            response_text = "Tuve un error guardando el recuerdo en mi memoria."
                
                # 4. Responder al usuario
                send_whatsapp_message(fw_id, response_text)
                
        return {"status": "ok"}
        
    except Exception as e:
        print(f"Error Webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
