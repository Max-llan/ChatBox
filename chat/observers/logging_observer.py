"""
Observer para Logging de Eventos Emocionales
Patrón Observer: Registra todos los eventos para auditoría
Cumplimiento: ISO 27000 (Seguridad de la Información), ISO 12207 (Trazabilidad)
"""
from chat.events.emotion_events import EmotionEvent
import logging
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class LoggingObserver:
    """
    Observador que registra todos los eventos emocionales
    Cumple con requisitos de auditoría y trazabilidad
    """
    
    def __init__(self, log_file: str = "emotion_events.log"):
        self.log_file = Path(log_file)
        self._ensure_log_file()
        logger.info(f"LoggingObserver inicializado - Log: {self.log_file}")
    
    def _ensure_log_file(self):
        """Crea el archivo de log si no existe"""
        if not self.log_file.exists():
            self.log_file.touch()
    
    def update(self, event: EmotionEvent):
        """
        Registra el evento en el archivo de log
        
        Args:
            event: Evento emocional a registrar
        """
        self._log_event(event)
    
    def _log_event(self, event: EmotionEvent):
        """
        Escribe el evento en el archivo de log
        Formato: JSON por línea para facilitar análisis posterior
        
        Args:
            event: Evento a registrar
        """
        log_entry = {
            'timestamp': event.timestamp.isoformat(),
            'user_id': self._anonymize_user_id(event.user_id),  # Protección Ley 21.459
            'emotion': event.emotion,
            'intensity': event.intensity,
            'risk_level': event.risk_level,
            'keywords': event.keywords,
            'high_risk': event.is_high_risk(),
            # NO se guarda el texto completo para proteger privacidad
            'text_length': len(event.text)
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            logger.debug(f"Evento registrado: {event.emotion} - Usuario: {log_entry['user_id']}")
            
        except Exception as e:
            logger.error(f"Error al escribir log: {str(e)}")
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """
        Anonimiza el ID de usuario para cumplir con protección de datos
        
        Args:
            user_id: ID original del usuario
            
        Returns:
            ID anonimizado
        """
        import hashlib
        # Hash del user_id para mantener consistencia pero proteger identidad
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def get_statistics(self, days: int = 7) -> dict:
        """
        Obtiene estadísticas de eventos registrados
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con estadísticas
        """
        from datetime import timedelta
        
        stats = {
            'total_events': 0,
            'high_risk_events': 0,
            'emotions_distribution': {},
            'average_intensity': 0
        }
        
        cutoff_date = datetime.now() - timedelta(days=days)
        intensities = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_time = datetime.fromisoformat(event['timestamp'])
                        
                        if event_time >= cutoff_date:
                            stats['total_events'] += 1
                            
                            if event.get('high_risk'):
                                stats['high_risk_events'] += 1
                            
                            emotion = event['emotion']
                            stats['emotions_distribution'][emotion] = \
                                stats['emotions_distribution'].get(emotion, 0) + 1
                            
                            intensities.append(event['intensity'])
                    
                    except json.JSONDecodeError:
                        continue
            
            if intensities:
                stats['average_intensity'] = sum(intensities) / len(intensities)
        
        except FileNotFoundError:
            logger.warning("Archivo de log no encontrado")
        
        return stats
