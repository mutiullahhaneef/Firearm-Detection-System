def send_sms(config, message):
    if not config.get("enabled", False):
        return
    print(f"[SMS MOCK] To {config.get('to_number')}: {message}")
