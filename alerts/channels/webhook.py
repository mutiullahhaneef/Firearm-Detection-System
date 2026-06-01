def send_webhook(config, payload):
    if not config.get("enabled", False):
        return
    print(f"[WEBHOOK MOCK] POST {config.get('url')} - Payload: {payload}")
