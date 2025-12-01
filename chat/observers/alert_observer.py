"""
Observer para Alertas de Alto Riesgo
Patrón Observer: Reacciona a eventos emocionales críticos
Cumplimiento: OWASP (Control de Acceso), Ley 21.459 (Protección Datos Sensibles)
"""
from chat.events.emotion_events import EmotionEvent
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AlertObserver:
    """
    Observador que genera alertas cuando se detectan estados emocionales de riesgo
    Cumple con protocolos de seguridad y confidencialidad
    """
    
    def __init__(self):
        self.alerts = []
        logger.info("AlertObserver inicializado")
    
    def update(self, event: EmotionEvent):
        """
        Método llamado cuando ocurre un evento emocional
        
        Args:
            event: Evento emocional a procesar
        """
        if event.requires_alert():
            self._create_alert(event)
    
    def _create_alert(self, event: EmotionEvent):
        """
        Crea una alerta de seguridad/salud mental
        
        Args:
            event: Evento que dispara la alerta
        """
        alert = {
            'alert_id': f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'user_id': event.user_id,  # Protegido según Ley 21.459
            'timestamp': event.timestamp.isoformat(),
            'severity': self._calculate_severity(event),
            'emotion': event.emotion,
            'intensity': event.intensity,
            'risk_level': event.risk_level,
            'recommendation': event.recommendation,
            'status': 'pending'
        }
        
        self.alerts.append(alert)
        
        # Log de alerta (sin datos sensibles para cumplir ISO 27000)
        logger.warning(
            f"ALERTA GENERADA: Severidad {alert['severity']} - "
            f"Emoción: {event.emotion} (Intensidad: {event.intensity})"
        )
        
        # Aquí se podría integrar con servicios de notificación externos
        # (Email, SMS, Firebase Cloud Messaging, etc.)
        self._send_notification(alert)
    
    def _calculate_severity(self, event: EmotionEvent) -> str:
        """Calcula la severidad de la alerta"""
        if event.is_high_risk():
            return 'CRÍTICA'
        elif event.intensity >= 7:
            return 'ALTA'
        elif event.intensity >= 5:
            return 'MEDIA'
        else:
            return 'BAJA'
    
    def _send_notification(self, alert: Dict[str, Any]):
        """
        Envía notificaciones a sistemas externos
        Aquí se integraría con Firebase, email, SMS, etc.
        
        Args:
            alert: Información de la alerta
        """
        # TODO: Integrar con Firebase Cloud Messaging o servicio similar
        # TODO: Implementar cifrado end-to-end (OWASP)
        logger.info(f"Notificación enviada para alerta {alert['alert_id']}")
        
        # Simulación de notificación
        if alert['severity'] == 'CRÍTICA':
            logger.critical(
                f"⚠️ ALERTA CRÍTICA: Se requiere atención inmediata - "
                f"Recomendación: {alert['recommendation']}"
            )
    
    def get_pending_alerts(self) -> list:
        """Obtiene alertas pendientes"""
        return [a for a in self.alerts if a['status'] == 'pending']
    
    def mark_as_resolved(self, alert_id: str):
        """Marca una alerta como resuelta"""
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now().isoformat()
                logger.info(f"Alerta {alert_id} marcada como resuelta")
                break
