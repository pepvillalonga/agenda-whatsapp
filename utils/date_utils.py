import datetime

def get_current_date_context():
    """Retorna fecha y hora actual en formato legible y ISO."""
    now = datetime.datetime.now()
    days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    day_str = days[now.weekday()]
    return {
        "iso": now.isoformat(),
        "human": f"{now.strftime('%Y-%m-%d')} ({day_str})",
        "day_name": day_str,
        "object": now
    }

def generate_calendar_reference(days=7):
    """Genera una lista de referencia para los próximos días."""
    context = get_current_date_context()
    now = context["object"]
    days_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    reference = []
    for i in range(days + 1):
        future_date = now + datetime.timedelta(days=i)
        day_str = days_names[future_date.weekday()]
        date_fmt = future_date.strftime('%Y-%m-%d')
        reference.append(f"- {date_fmt} ({day_str})")
        
    return "\n".join(reference)
