from datetime import datetime

def firebase_format_date(date):
    return f"research-{date}"
def current_date():
    return datetime.now().strftime("%Y%m%d")