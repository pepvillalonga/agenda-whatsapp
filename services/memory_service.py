import os
import requests
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
# Usar modelo optimizado para embeddings
HF_API_URL = "https://router.huggingface.co/hf-inference/models/BAAI/bge-small-en-v1.5"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def generate_embedding(text):
    """Genera embeddings usando HuggingFace Inference API."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(
            HF_API_URL, 
            headers=headers, 
            json={"inputs": text, "options": {"wait_for_model": True}}
        )
        if response.status_code == 200:
            data = response.json()
            # BGE devuelve directamente una lista de floats para un solo texto
            if isinstance(data, list) and len(data) > 0:
                # Si es lista de listas (batch), tomamos el primero
                if isinstance(data[0], list):
                    return data[0]
                # Si es lista de floats directamente
                return data
            return None
        print(f"Error HF: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"Excepción HF: {e}")
        return None

def search_relevant_context(text, top_k=3):
    """Busca memoria relevante en Pinecone."""
    vector = generate_embedding(text)
    if not vector:
        return []

    try:
        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        matches = []
        for match in results['matches']:
            if match['score'] > 0.3: # Filtro de relevancia
                meta = match['metadata']
                matches.append(f"[{meta.get('fecha', 'N/A')}] {meta.get('nombre', 'Evento')}: {meta.get('texto', '')}")
        return matches
    except Exception as e:
        print(f"Pinecone Error: {e}")
        return []

def save_memory(text, metadata):
    """Guarda un nuevo vector en Pinecone."""
    vector = generate_embedding(text)
    if not vector:
        return False
        
    try:
        # ID único basado en timestamp + uuid
        import time
        import uuid
        unique_id = f"evt_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        
        # Determinar días de anticipación para recordatorio
        reminder_days = metadata.get("reminder_days_before", "1")
        if not reminder_days: reminder_days = "1"
        
        # Sanitizar metadata para evitar nulls
        nombre = metadata.get("nombre") or "Recordatorio"
        fecha = metadata.get("fecha") or ""
        hora = metadata.get("hora") or ""
        user_phone = metadata.get("user_phone") or ""
        
        index.upsert(vectors=[
            (unique_id, vector, {
                "texto": text,
                "nombre": nombre,
                "fecha": fecha,
                "hora": hora,
                "user_phone": user_phone,
                "reminder_sent": "false",
                "reminder_days_before": str(reminder_days),
                "created_at": str(time.time())
            })
        ])
        return True
    except Exception as e:
        print(f"Pinecone Save Error: {e}")
        return False

def delete_all_memories():
    """Borra TODOS los vectores del índice Pinecone."""
    try:
        index.delete(delete_all=True)
        return True
    except Exception as e:
        print(f"Pinecone Delete All Error: {e}")
        return False

def get_all_active_events(limit=100):
    """Recupera todos los eventos activos (recordatorio no enviado o futuros)."""
    try:
        # Vector dummy
        results = index.query(
            vector=[0.0] * 384,
            top_k=limit,
            include_metadata=True,
            filter={"reminder_sent": {"$eq": "false"}} 
        )
        return results.get('matches', [])
    except Exception as e:
        print(f"Pinecone Fetch Error: {e}")
        return []

def delete_event_by_id(event_id):
    """Borra un evento específico por ID."""
    try:
        index.delete(ids=[event_id])
        return True
    except Exception as e:
        print(f"Pinecone Delete ID Error: {e}")
        return False

def find_best_match(text, threshold=0.7):
    """Busca el mejor evento coincidente y devuelve su ID y metadata."""
    vector = generate_embedding(text)
    if not vector:
        return None
        
    try:
        results = index.query(
            vector=vector,
            top_k=1,
            include_metadata=True
        )
        if results['matches'] and results['matches'][0]['score'] > threshold:
            return results['matches'][0]
        return None
    except Exception as e:
        print(f"Pinecone Search Error: {e}")
        return None
