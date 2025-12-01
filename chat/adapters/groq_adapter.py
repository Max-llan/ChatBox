"""
Patrón Adapter para la API de GroqCloud
Abstrae la comunicación con servicios externos de IA
ISO 12207: Diseño modular y mantenible
"""
from groq import Groq
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class GroqCloudAdapter:
    """
    Adapter para la API de GroqCloud
    Encapsula la lógica de comunicación con servicios de IA externos
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY no encontrada en variables de entorno")
        
        self.client = Groq(api_key=self.api_key)
        logger.info("GroqCloudAdapter inicializado correctamente")
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> Optional[str]:
        """
        Realiza una consulta al modelo de chat
        
        Args:
            messages: Lista de mensajes en formato [{"role": "user", "content": "..."}]
            model: Modelo a utilizar
            temperature: Creatividad de la respuesta (0-2)
            max_tokens: Tokens máximos de respuesta
            
        Returns:
            Respuesta del modelo o None en caso de error
        """
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=False,
                stop=None
            )
            
            response = completion.choices[0].message.content
            logger.info(f"Chat completion exitoso: {len(response)} caracteres")
            return response
            
        except Exception as e:
            logger.error(f"Error en chat_completion: {str(e)}")
            raise
    
    def transcribe_audio(
        self, 
        audio_file_data: bytes, 
        filename: str,
        language: str = "es",
        model: str = "whisper-large-v3"
    ) -> Optional[str]:
        """
        Transcribe audio a texto usando Whisper
        
        Args:
            audio_file_data: Datos binarios del archivo de audio
            filename: Nombre del archivo
            language: Idioma del audio
            model: Modelo de Whisper a utilizar
            
        Returns:
            Texto transcrito o None en caso de error
        """
        try:
            transcription = self.client.audio.transcriptions.create(
                file=(filename, audio_file_data),
                model=model,
                temperature=0,
                response_format="json",
                language=language
            )
            
            logger.info(f"Transcripción exitosa: {len(transcription.text)} caracteres")
            return transcription.text
            
        except Exception as e:
            logger.error(f"Error en transcribe_audio: {str(e)}")
            raise
    
    def analyze_emotion_context(
        self, 
        text: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, any]:
        """
        Analiza el texto para detectar emociones y estados emocionales
        Utiliza el LLM para análisis emocional profundo
        
        Args:
            text: Texto a analizar
            conversation_history: Historial de conversación para contexto
            
        Returns:
            Diccionario con análisis emocional
        """
        try:
            # Prompt especializado para análisis emocional
            system_prompt = {
                "role": "system",
                "content": """Eres un asistente experto en análisis emocional y salud mental.
                Analiza el texto del usuario y proporciona:
                1. Emoción principal detectada (alegría, tristeza, ansiedad, enojo, miedo, neutral)
                2. Intensidad emocional (escala 1-10)
                3. Indicadores de riesgo (si, no, moderado)
                4. Recomendaciones breves de apoyo
                
                Responde SOLO en formato JSON como este ejemplo:
                {
                    "emotion": "ansiedad",
                    "intensity": 7,
                    "risk_level": "moderado",
                    "keywords": ["preocupado", "nervioso"],
                    "recommendation": "Considera técnicas de respiración profunda"
                }"""
            }
            
            messages = [system_prompt]
            if conversation_history:
                messages.extend(conversation_history[-5:])  # Últimos 5 mensajes para contexto
            
            messages.append({
                "role": "user",
                "content": f"Analiza este texto: '{text}'"
            })
            
            response = self.chat_completion(
                messages=messages,
                temperature=0.3,  # Baja temperatura para respuestas más consistentes
                max_tokens=500
            )
            
            # Intentar parsear la respuesta como JSON
            import json
            try:
                emotion_data = json.loads(response)
                logger.info(f"Análisis emocional completado: {emotion_data.get('emotion')}")
                return emotion_data
            except json.JSONDecodeError:
                # Si no es JSON válido, retornar análisis básico
                logger.warning("Respuesta no en formato JSON esperado")
                return {
                    "emotion": "neutral",
                    "intensity": 5,
                    "risk_level": "no",
                    "keywords": [],
                    "recommendation": response[:200]
                }
            
        except Exception as e:
            logger.error(f"Error en analyze_emotion_context: {str(e)}")
            raise
