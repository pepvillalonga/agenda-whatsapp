import os
import logging
from datetime import datetime, timedelta
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")

# Zona horaria - usar pytz para compatibilidad con Windows
try:
    import pytz
    TIMEZONE = pytz.timezone("Europe/Madrid")
except ImportError:
    # Fallback si pytz no está disponible
    TIMEZONE = None
    logger.warning("pytz no disponible, usando hora UTC")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)


def get_upcoming_reminders():
    """
    Busca eventos que necesitan recordatorio.
    Compara: fecha_evento - reminder_days_before == fecha_actual
    """
    try:
        # Obtener fecha/hora actual con zona horaria correcta
        if TIMEZONE:
            now = datetime.now(TIMEZONE)
        else:
            now = datetime.utcnow()
        
        today_str = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        
        logger.info(f"Buscando recordatorios. Hoy: {today_str}, Hora: {current_hour}")
        
        # Consultar todos los eventos que no han sido notificados
        # Pinecone no soporta queries complejas, así que traemos todos y filtramos
        # Usamos un vector dummy para hacer la query (limitación de Pinecone)
        
        # Alternativa: listar todos los vectores con list()
        results = index.query(
            vector=[0.0] * 384,  # Vector dummy (BGE tiene 384 dimensiones)
            top_k=100,
            include_metadata=True,
            filter={"reminder_sent": {"$eq": "false"}}
        )
        
        reminders_to_send = []
        
        for match in results.get('matches', []):
            meta = match.get('metadata', {})
            event_date_str = meta.get('fecha', '')
            reminder_days = int(meta.get('reminder_days_before', '1'))
            user_phone = meta.get('user_phone', '')
            
            if not event_date_str or not user_phone:
                continue
            
            try:
                event_date = datetime.strptime(event_date_str, "%Y-%m-%d")
                reminder_date = event_date - timedelta(days=reminder_days)
                reminder_date_str = reminder_date.strftime("%Y-%m-%d")
                
                if reminder_date_str == today_str:
                    reminders_to_send.append({
                        'id': match['id'],
                        'nombre': meta.get('nombre', 'Evento'),
                        'fecha': event_date_str,
                        'hora': meta.get('hora', ''),
                        'texto': meta.get('texto', ''),
                        'user_phone': user_phone,
                        'days_before': reminder_days
                    })
                    logger.info(f"Recordatorio encontrado: {meta.get('nombre')} para {user_phone}")
                    
            except ValueError as e:
                logger.error(f"Error parseando fecha {event_date_str}: {e}")
                continue
        
        logger.info(f"Total recordatorios a enviar: {len(reminders_to_send)}")
        return reminders_to_send
        
    except Exception as e:
        logger.error(f"Error buscando recordatorios: {e}")
        return []


def mark_reminder_sent(event_id):
    """Marca un evento como notificado para evitar duplicados."""
    try:
        # Pinecone no tiene update directo, necesitamos fetch + upsert
        result = index.fetch(ids=[event_id])
        
        if event_id in result.get('vectors', {}):
            vector_data = result['vectors'][event_id]
            metadata = vector_data.get('metadata', {})
            metadata['reminder_sent'] = 'true'
            
            index.upsert(vectors=[
                (event_id, vector_data['values'], metadata)
            ])
            logger.info(f"Evento {event_id} marcado como notificado")
            return True
            
    except Exception as e:
        logger.error(f"Error marcando recordatorio: {e}")
    
    return False


def format_reminder_message(reminder):
    """Genera el mensaje de recordatorio para WhatsApp."""
    nombre = reminder.get('nombre', 'Evento')
    fecha = reminder.get('fecha', '')
    hora = reminder.get('hora', '')
    days_before = reminder.get('days_before', 1)
    
    # Formatear fecha bonita
    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_bonita = fecha_dt.strftime("%d de %B")
    except:
        fecha_bonita = fecha
    
    if days_before == 1:
        tiempo = "mañana"
    else:
        tiempo = f"en {days_before} días"
    
    mensaje = f"🔔 *Recordatorio*\n\n"
    mensaje += f"Tienes *{nombre}* {tiempo}"
    
    if hora:
        mensaje += f" a las *{hora}*"
    
    mensaje += f".\n\n📅 {fecha_bonita}"
    
    return mensaje
