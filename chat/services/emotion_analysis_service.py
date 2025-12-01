"""
Servicio de Análisis Emocional
Capa de Negocio que orquesta el análisis de emociones
Arquitectura Cliente-Servidor: Este servicio actúa como intermediario
ISO 12207: Separación de responsabilidades
"""
from chat.adapters.groq_adapter import GroqCloudAdapter
from chat.events.emotion_events import EmotionEvent, EmotionEventManager
from chat.observers.alert_observer import AlertObserver
from chat.observers.logging_observer import LoggingObserver
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class EmotionAnalysisService:
    """
    Servicio principal para análisis emocional
    Coordina adaptadores, eventos y observadores
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton para mantener estado consistente"""
        if cls._instance is None:
            cls._instance = super(EmotionAnalysisService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Inicializar componentes
        self.groq_adapter = GroqCloudAdapter()
        self.event_manager = EmotionEventManager()
        
        # Registrar observadores (Patrón Observer)
        self.alert_observer = AlertObserver()
        self.logging_observer = LoggingObserver()
        
        self.event_manager.attach(self.alert_observer)
        self.event_manager.attach(self.logging_observer)
        
        self._initialized = True
        logger.info("EmotionAnalysisService inicializado correctamente")
    
    def analyze_text(
        self, 
        user_id: str, 
        text: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict:
        """
        Analiza texto y detecta emociones
        
        Args:
            user_id: Identificador del usuario
            text: Texto a analizar
            conversation_history: Historial de conversación para contexto
            
        Returns:
            Diccionario con análisis emocional y respuesta
        """
        try:
            # 1. Análisis emocional mediante IA
            emotion_data = self.groq_adapter.analyze_emotion_context(
                text=text,
                conversation_history=conversation_history
            )
            
            # 2. Crear evento emocional
            event = EmotionEvent(
                user_id=user_id,
                text=text,
                emotion_data=emotion_data
            )
            
            # 3. Notificar a observadores (genera alertas y logs)
            self.event_manager.notify(event)
            
            # 4. Generar respuesta del chatbot
            response = self._generate_empathetic_response(
                text=text,
                emotion_data=emotion_data,
                conversation_history=conversation_history
            )
            
            return {
                'success': True,
                'response': response,
                'emotion_analysis': {
                    'emotion': emotion_data.get('emotion'),
                    'intensity': emotion_data.get('intensity'),
                    'risk_level': emotion_data.get('risk_level'),
                    'recommendation': emotion_data.get('recommendation')
                },
                'alert_generated': event.requires_alert()
            }
            
        except Exception as e:
            logger.error(f"Error en analyze_text: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Lo siento, ocurrió un error al procesar tu mensaje.'
            }
    
    def analyze_audio(
        self,
        user_id: str,
        audio_data: bytes,
        filename: str
    ) -> Dict:
        """
        Transcribe audio y analiza emociones
        
        Args:
            user_id: Identificador del usuario
            audio_data: Datos binarios del audio
            filename: Nombre del archivo
            
        Returns:
            Diccionario con transcripción y análisis
        """
        try:
            # 1. Transcribir audio a texto
            transcription = self.groq_adapter.transcribe_audio(
                audio_file_data=audio_data,
                filename=filename
            )
            
            if not transcription:
                return {
                    'success': False,
                    'error': 'No se pudo transcribir el audio'
                }
            
            # 2. Analizar el texto transcrito
            analysis = self.analyze_text(
                user_id=user_id,
                text=transcription
            )
            
            # Agregar transcripción al resultado
            analysis['transcription'] = transcription
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en analyze_audio: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_empathetic_response(
        self,
        text: str,
        emotion_data: Dict,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Genera una respuesta empática basada en el estado emocional
        
        Args:
            text: Mensaje del usuario
            emotion_data: Datos del análisis emocional
            conversation_history: Historial de conversación
            
        Returns:
            Respuesta empática del asistente
        """
        # Construir prompt con contexto emocional
        system_prompt = {
            "role": "system",
            "content": f"""Eres un asistente de apoyo emocional empático y profesional.
            
El usuario está experimentando: {emotion_data.get('emotion')} 
con intensidad {emotion_data.get('intensity')}/10.

Lineamientos:
- Sé empático y comprensivo
- Valida sus emociones
- Ofrece apoyo constructivo
- Si detectas riesgo alto, sugiere buscar ayuda profesional
- Mantén un tono cálido pero profesional
- Respeta la confidencialidad (Ley 21.459)"""
        }
        
        messages = [system_prompt]
        
        if conversation_history:
            messages.extend(conversation_history[-5:])
        
        messages.append({
            "role": "user",
            "content": text
        })
        
        try:
            response = self.groq_adapter.chat_completion(
                messages=messages,
                temperature=0.7
            )
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta empática: {str(e)}")
            return emotion_data.get('recommendation', 
                'Estoy aquí para apoyarte. ¿Cómo te puedo ayudar?')
    
    def get_user_emotional_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Obtiene el historial emocional del usuario
        
        Args:
            user_id: Identificador del usuario
            limit: Número máximo de eventos
            
        Returns:
            Lista de eventos emocionales
        """
        events = self.event_manager.get_history(user_id=user_id, limit=limit)
        return [event.to_dict() for event in events]
    
    def get_pending_alerts(self) -> List[Dict]:
        """Obtiene alertas pendientes de revisión"""
        return self.alert_observer.get_pending_alerts()
    
    def get_statistics(self, days: int = 7) -> Dict:
        """Obtiene estadísticas de análisis emocional"""
        return self.logging_observer.get_statistics(days=days)
