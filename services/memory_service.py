import os
import requests
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HF_API_URL = "https://router.huggingface.co/hf-inference/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

def generate_embedding(text):
    """Genera embeddings usando HuggingFace Inference API."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    try:
        response = requests.post(
            HF_API_URL, 
            headers=headers, 
            json={"inputs": [text], "options": {"wait_for_model": True}}
        )
        if response.status_code == 200:
            # La API devuelve una lista de float directamente o lista de listas
            data = response.json()
            # Si enviamos lista [text], nos devuelve [[embedding]]
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                return data[0]
            return data
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
        
        index.upsert(vectors=[
            (unique_id, vector, {
                "texto": text,
                "nombre": metadata.get("nombre", "Recordatorio"),
                "fecha": metadata.get("fecha", ""),
                "hora": metadata.get("hora", ""),
                "created_at": str(time.time())
            })
        ])
        return True
    except Exception as e:
        print(f"Pinecone Save Error: {e}")
        return False
