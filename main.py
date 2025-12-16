from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import sys
import logging
from dotenv import load_dotenv

from services.llm_service import process_message
from services.memory_service import search_relevant_context, save_memory, delete_all_memories, get_all_active_events, delete_event_by_id, find_best_match
from datetime import datetime, timedelta
import pytz
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
                        if not saved:
                            response_text = "Tuve un error guardando el recuerdo en mi memoria."
                
                elif action == "DELETE_ALL":
                    success = delete_all_memories()
                    if success:
                        response_text = "✅ Memoria borrada completamente. No recuerdo nada."
                    else:
                        response_text = "❌ Hubo un error al intentar borrar la memoria."
                
                elif action == "ASK_DELETE_CONFIRMATION":
                    # El response_text ya trae la pregunta del LLM
                    pass

                elif action == "LIST_REMINDERS":
                    events = get_all_active_events()
                    if not events:
                        response_text = "📭 No tienes recordatorios pendientes."
                    else:
                        response_text = "📋 *Tus Recordatorios:*\n\n"
                        for evt in events:
                            meta = evt['metadata']
                            nombre = meta.get('nombre', 'Evento')
                            fecha = meta.get('fecha', 'N/A')
                            # Calcular tiempo restante
                            try:
                                tz = pytz.timezone("Europe/Madrid")
                                now = datetime.now(tz)
                                event_date = datetime.strptime(fecha, "%Y-%m-%d")
                                event_date = tz.localize(event_date)
                                delta = event_date - now
                                days = delta.days
                                if days < 0:
                                    tiempo_restante = "Vencido"
                                elif days == 0:
                                    tiempo_restante = "Hoy"
                                else:
                                    tiempo_restante = f"Faltan {days} días"
                            except:
                                tiempo_restante = "Fecha inválida"

                            response_text += f"🔹 *{nombre}*: {fecha} ({tiempo_restante})\n"
                        response_text += "\nPara borrar uno, escribe: *borrar [nombre del evento]*"

                elif action == "HELP":
                    response_text = (
                        "🤖 *Comandos de la Agenda:*\n\n"
                        "📌 *Guardar*: 'Cita dentista mañana a las 10'\n"
                        "🔍 *Consultar*: '¿Qué tengo esta semana?'\n"
                        "📋 *Listar*: 'Listar recordatorios'\n"
                        "🗑️ *Borrar*: 'Borrar [nombre]' o 'Borrar ID'\n"
                        "⚠️ *Reset*: 'Borrar todo'\n"
                    )

                elif action == "DELETE_SPECIFIC":
                    query_term = decision.get("data", {}).get("query")
                    
                    # 1. Buscar la mejor coincidencia
                    match = find_best_match(query_term, threshold=0.65)
                    
                    if not match:
                         response_text = f"❌ No encontré ningún evento parecido a '{query_term}' para borrar."
                    else:
                        # 2. Si hay coincidencia, borrar directamente (es más natural)
                        # Se podría pedir confirmación, pero el usuario pidió "borrar [nombre]".
                        # Si el threshold es alto, asumimos que es lo correcto.
                        event_id = match['id']
                        event_name = match['metadata'].get('nombre', 'Evento')
                        
                        success = delete_event_by_id(event_id)
                        if success:
                             response_text = f"🗑️ He borrado el evento: *{event_name}*."
                        else:
                             response_text = "❌ Hubo un error al intentar borrar el evento."


                elif action == "EDIT_EVENT":
                    query_term = decision.get("data", {}).get("query")
                    new_name = decision.get("data", {}).get("new_name")
                    new_date = decision.get("data", {}).get("new_date")
                    new_time = decision.get("data", {}).get("new_time")
                    
                    match = find_best_match(query_term)
                    
                    if match:
                        old_id = match['id']
                        old_meta = match['metadata']
                        
                        # Preparar nuevos datos
                        final_name = new_name if new_name else old_meta.get('nombre')
                        final_date = new_date if new_date else old_meta.get('fecha')
                        final_time = new_time if new_time else old_meta.get('hora')
                        
                        # Construir nuevo texto para vectorizar
                        new_text = f"Recordatorio: {final_name} el {final_date} a las {final_time}"
                        
                        # Datos para save_memory
                        event_data = {
                            "nombre": final_name,
                            "fecha": final_date,
                            "hora": final_time,
                            "user_phone": fw_id,
                            "reminder_days_before": old_meta.get('reminder_days_before', '1')
                        }
                        
                        # Transacción atómica idealmente, pero aquí paso a paso
                        # Borrar viejo
                        delete_event_by_id(old_id)
                        # Crear nuevo
                        saved = save_memory(new_text, event_data)
                        
                        if saved:
                             response_text = f"✅ He actualizado el evento.\nAhora es: *{final_name}* el {final_date} {final_time}"
                        else:
                             response_text = "❌ Pude borrar el viejo pero fallé al guardar el nuevo. Lo siento."
                    else:
                        response_text = f"❌ No encontré el evento '{query_term}' para editar."

                logger.info(f"Enviando respuesta a {fw_id}: {response_text}")
                send_whatsapp_message(fw_id, response_text)
                
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error Webhook: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/summary/weekly")
async def weekly_summary():
    """Genera y envía un resumen semanal (Domingo noche)."""
    try:
        events = get_all_active_events()
        # Filtrar próxima semana
        tz = pytz.timezone("Europe/Madrid")
        now = datetime.now(tz)
        week_end = now + timedelta(days=7)
        
        upcoming = []
        for evt in events:
            try:
                date_str = evt['metadata'].get('fecha')
                if not date_str: continue
                
                evt_date = datetime.strptime(date_str, "%Y-%m-%d")
                evt_date = tz.localize(evt_date)
                
                if now <= evt_date <= week_end:
                    upcoming.append(evt)
            except:
                continue
                
        if not upcoming:
            return {"status": "no events"}
            
        # Agrupar por "tipo" (simple conteo por ahora)
        count = len(upcoming)
        
        # Enviar a todos los usuarios únicos encontrados (o hardcoded si es personal)
        # Aquí asumiremos que extraemos los teléfonos de los eventos
        phones = set(e['metadata'].get('user_phone') for e in upcoming if e['metadata'].get('user_phone'))
        
        msg = f"📅 *Resumen Semanal*\nEsta semana tienes *{count}* eventos pendientes.\n\n"
        for evt in upcoming:
            meta = evt['metadata']
            msg += f"- {meta.get('nombre')} ({meta.get('fecha')})\n"
            
        for phone in phones:
            send_whatsapp_message(phone, msg)
            
        return {"status": "ok", "sent_to": list(phones)}
    except Exception as e:
        logger.error(f"Error Weekly Summary: {e}")
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
