"""
Test rápido del prompt del LLM para recordatorios.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_service import process_message

print("=" * 60)
print("TEST DEL LLM - Extracción de días de recordatorio")
print("=" * 60)

test_cases = [
    ("Tengo cita con el dentista el martes a las 10", "Sin mención de recordatorio"),
    ("Recuérdame que tengo médico el viernes, avísame el día anterior", "1 día antes"),
    ("Tengo reunión el lunes, avísame con 2 días de antelación", "2 días antes"),
    ("Cumpleaños de mamá el 25, recuérdame 3 días antes", "3 días antes"),
]

for msg, expected in test_cases:
    print(f"\n📝 Input: '{msg}'")
    print(f"   Esperado: {expected}")
    
    try:
        result = process_message(msg, [])
        print(f"   Acción: {result.get('action')}")
        
        data = result.get('data')
        if data:
            reminder_days = data.get('reminder_days_before', 'N/A')
            print(f"   reminder_days_before: {reminder_days}")
            print(f"   Respuesta: {result.get('response_text', '')[:80]}...")
        else:
            print(f"   Respuesta: {result.get('response_text', '')[:80]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
