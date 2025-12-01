"""
Sistema de Eventos para Análisis Emocional
Patrón Observer: Notifica a observadores sobre cambios emocionales
ISO 12207: Arquitectura orientada a eventos
"""
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EmotionEvent:
    """
    Representa un evento de análisis emocional
    """
    def __init__(
        self, 
        user_id: str,
        text: str,
        emotion_data: Dict[str, Any],
        timestamp: datetime = None
    ):
        self.user_id = user_id
        self.text = text
        self.emotion = emotion_data.get('emotion', 'neutral')
        self.intensity = emotion_data.get('intensity', 5)
        self.risk_level = emotion_data.get('risk_level', 'no')
        self.keywords = emotion_data.get('keywords', [])
        self.recommendation = emotion_data.get('recommendation', '')
        self.timestamp = timestamp or datetime.now()
        
    def is_high_risk(self) -> bool:
        """Determina si el evento representa un riesgo alto"""
        return (
            self.risk_level in ['si', 'alto', 'crítico'] or 
            self.intensity >= 8 or
            self.emotion in ['depresión', 'pánico', 'crisis']
        )
    
    def requires_alert(self) -> bool:
        """Determina si se debe enviar una alerta"""
        return self.is_high_risk() or self.intensity >= 7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario"""
        return {
            'user_id': self.user_id,
            'text': self.text,
            'emotion': self.emotion,
            'intensity': self.intensity,
            'risk_level': self.risk_level,
            'keywords': self.keywords,
            'recommendation': self.recommendation,
            'timestamp': self.timestamp.isoformat(),
            'high_risk': self.is_high_risk()
        }


class EmotionEventManager:
    """
    Gestor de eventos emocionales
    Implementa el patrón Observer para notificar a los observadores
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton para asegurar una única instancia"""
        if cls._instance is None:
            cls._instance = super(EmotionEventManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._observers = []
        self._event_history = []
        self._initialized = True
        logger.info("EmotionEventManager inicializado")
    
    def attach(self, observer):
        """
        Registra un observador
        
        Args:
            observer: Objeto observador con método update(event)
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Observador {observer.__class__.__name__} registrado")
    
    def detach(self, observer):
        """
        Desregistra un observador
        
        Args:
            observer: Objeto observador a desregistrar
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Observador {observer.__class__.__name__} desregistrado")
    
    def notify(self, event: EmotionEvent):
        """
        Notifica a todos los observadores sobre un nuevo evento
        
        Args:
            event: Evento emocional a notificar
        """
        logger.info(f"Notificando evento: {event.emotion} (intensidad: {event.intensity})")
        
        # Guardar en historial
        self._event_history.append(event)
        
        # Notificar a observadores
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                logger.error(f"Error al notificar a {observer.__class__.__name__}: {str(e)}")
    
    def get_history(self, user_id: str = None, limit: int = 10) -> list:
        """
        Obtiene el historial de eventos
        
        Args:
            user_id: Filtrar por usuario específico
            limit: Número máximo de eventos a retornar
            
        Returns:
            Lista de eventos
        """
        events = self._event_history
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        return events[-limit:] if limit else events
    
    def get_risk_events(self, user_id: str = None) -> list:
        """
        Obtiene eventos de alto riesgo
        
        Args:
            user_id: Filtrar por usuario específico
            
        Returns:
            Lista de eventos de alto riesgo
        """
        events = self.get_history(user_id, limit=None)
        return [e for e in events if e.is_high_risk()]
