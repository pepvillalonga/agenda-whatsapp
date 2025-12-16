try:
    from main import app
    from services.memory_service import get_all_active_events
    from services.llm_service import process_message
    from services.reminder_service import get_upcoming_reminders
    print("✅ Imports OK")
except Exception as e:
    print(f"❌ Import Error: {e}")
    exit(1)

print("✅ Integrity Check Passed")
