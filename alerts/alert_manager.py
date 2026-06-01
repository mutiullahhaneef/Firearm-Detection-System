import time
import yaml
from pathlib import Path
from .incident_logger import IncidentLogger
from .channels import twilio_sms, email_alert, webhook

class AlertManager:
    def __init__(self, config_path="configs/alert_config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.enabled = self.config.get("enabled", True)
        self.gate = self.config.get("confidence_gate", 0.55)
        self.cooldown = self.config.get("cooldown_seconds", 60)
        
        self.logger = IncidentLogger(self.config.get("incident_logging", {}))
        self.last_alerts = {}
        
    def process_detections(self, source_name, detections):
        if not self.enabled or not detections:
            return
            
        max_conf = max([d["confidence"] for d in detections])
        if max_conf < self.gate:
            return
            
        now = time.time()
        if source_name in self.last_alerts:
            if now - self.last_alerts[source_name] < self.cooldown:
                print(f"[AlertManager] Skipped alert for {source_name} (cooldown)")
                return
                
        self.last_alerts[source_name] = now
        self.logger.log_incident(source_name, max_conf)
        
        msg = f"FIREARM DETECTED in {source_name} (conf: {max_conf:.2f})"
        
        channels = self.config.get("channels", {})
        twilio_sms.send_sms(channels.get("sms", {}), msg)
        email_alert.send_email(channels.get("email", {}), "SECURITY ALERT", msg)
        webhook.send_webhook(channels.get("webhook", {}), {"source": source_name, "conf": max_conf})
        print(f"🚨 ALERT DISPATCHED: {msg}")
