def send_email(config, subject, message):
    if not config.get("enabled", False):
        return
    print(f"[EMAIL MOCK] To {config.get('to_addr')} | {subject}: {message}")
