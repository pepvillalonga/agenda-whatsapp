import os
import json
from groq import Groq
from dotenv import load_dotenv
from utils.date_utils import get_current_date_context, generate_calendar_reference

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def process_message(user_text, memory_context):
    """
    Procesa el mensaje del usuario con Llama 3.
    Decide si es SAVE o QUERY y genera respuesta.
    """
    date_ctx = get_current_date_context()
    calendar_ref = generate_calendar_reference(7)
    
    memory_str = "\n".join(memory_context) if memory_context else "No hay memoria relevante."
    
    system_prompt = f"""
    Eres una Agenda Inteligente para WhatsApp. Tu objetivo es gestionar eventos y responder dudas.
    
    CONTEXTO TEMPORAL:
    - Fecha Actual: {date_ctx['human']}
    - Calendario Referencia:
    {calendar_ref}
    
    MEMORIA (Eventos encontrados):
    {memory_str}
    
    INSTRUCCIONES:
    1. Analiza el mensaje del usuario.
    2. Si quiere GUARDAR un evento (ej: "tengo médico el martes"):
       - Extrae: "nombre", "fecha" (YYYY-MM-DD), "hora" (HH:MM).
       - Extrae cuántos días ANTES quiere ser recordado:
         * "recuérdame mañana" o "avísame el día anterior" → reminder_days_before: 1
         * "avísame con 2 días" o "recuérdame dos días antes" → reminder_days_before: 2
         * Si NO menciona recordatorio, usar por defecto: reminder_days_before: 1
       - Acción: "SAVE".
       - Respuesta: Confirma que se guardó Y menciona cuándo se le recordará.
    3. Si es una CONSULTA (ej: "qué tengo hoy"):
       - Usa la MEMORIA para responder.
       - Acción: "QUERY".
       - Respuesta: Resumen amigable.
    4. Responde SIEMPRE en formato JSON estricto.
    
    FORMATO JSON ESPERADO:
    {{
      "action": "SAVE" | "QUERY",
      "response_text": "Texto para enviar al usuario por WhatsApp",
      "data": {{ 
         "nombre": "...", 
         "fecha": "YYYY-MM-DD", 
         "hora": "HH:MM",
         "reminder_days_before": 1
      }} (Solo si action es SAVE, sino null)
    }}
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return {
            "action": "ERROR", 
            "response_text": "Lo siento, tuve un problema procesando tu mensaje.",
            "data": None
        }
