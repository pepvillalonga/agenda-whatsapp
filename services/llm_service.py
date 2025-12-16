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
    
    2. CASO LISTAR (LIST):
       - Si pide "listar", "ver recordatorios", "qué tengo pendiente":
         * Acción: "LIST_REMINDERS"
         * Respuesta: "Aquí tienes tus recordatorios:" (El código listará los detalles).

    3. CASO AYUDA (HELP):
       - Si escribe "ayuda", "comandos", "qué puedes hacer":
         * Acción: "HELP"
         * Respuesta: (El código enviará la lista de comandos).

    4. CASO BORRADO TOTAL vs ESPECÍFICO:
       - "borrar todo", "resetea la agenda" -> Acción: "ASK_DELETE_CONFIRMATION".
       - "CONFIRMAR BORRADO TOTAL" -> Acción: "DELETE_ALL".
       - "borrar [algo]" (ej: "borrar dentista", "eliminar cita médico"):
         * Acción: "DELETE_SPECIFIC"
         * Extrae "query": "dentista"

    5. CASO EDITAR (EDIT):
       - "cambiar [algo] a [fecha/hora]" o "modificar [algo]":
         * Acción: "EDIT_EVENT"
         * Extrae "query": lo que quiere cambiar (ej: "dentista")
         * Extrae cambios: "new_date" (YYYY-MM-DD), "new_time" (HH:MM), "new_name".
         * Si no menciona un campo, déjalo null.

    6. CASO GUARDAR (SAVE):
       - Si quiere GUARDAR un evento (ej: "tengo médico el martes"):
       - Extrae: "nombre", "fecha" (YYYY-MM-DD), "hora" (HH:MM).
       - Extrae días aviso: "recordar 1 día antes" -> reminder_days_before.
       - Acción: "SAVE".

    7. CASO CONSULTAR (QUERY):
       - "qué tengo hoy", "busca eventos de X":
         * Acción: "QUERY"

    8. Responde SIEMPRE en formato JSON estricto.
    
    FORMATO JSON ESPERADO:
    {{
      "action": "SAVE" | "QUERY" | "LIST_REMINDERS" | "HELP" | "DELETE_SPECIFIC" | "EDIT_EVENT" | "ASK_DELETE_CONFIRMATION" | "DELETE_ALL",
      "response_text": "Texto respuesta",
      "data": {{ 
         "nombre": "...", 
         "fecha": "YYYY-MM-DD", 
         "hora": "HH:MM",
         "reminder_days_before": 1,
         "query": "termino busqueda para borrar/editar",
         "new_name": "...",
         "new_date": "...",
         "new_time": "..."
      }}
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
        
        content = completion.choices[0].message.content
        # Limpiar posibles bloques de código markdown
        if "```json" in content:
            content = content.replace("```json", "").replace("```", "")
        elif "```" in content:
            content = content.replace("```", "")
            
        return json.loads(content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return {
            "action": "ERROR", 
            "response_text": "Lo siento, tuve un problema procesando tu mensaje.",
            "data": None
        }
