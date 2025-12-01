"""
Vistas de Django - Capa de Presentación
Arquitectura Cliente-Servidor: Endpoints REST para el cliente
OWASP: Protección CSRF, validación de entrada, manejo de errores seguro
ISO 12207: Separación de capas (Presentación -> Servicio -> Adaptador)
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)

# Inicialización perezosa del servicio
_emotion_service = None

def get_emotion_service():
    """Obtiene la instancia del servicio (lazy initialization)"""
    global _emotion_service
    if _emotion_service is None:
        from chat.services.emotion_analysis_service import EmotionAnalysisService
        _emotion_service = EmotionAnalysisService()
    return _emotion_service


def index(request):
    """
    Vista principal del chatbox
    Renderiza la interfaz de usuario
    """
    return render(request, 'chat/index.html')


@csrf_exempt  # TODO: Implementar CSRF token en producción (OWASP)
@require_http_methods(["POST"])
def send_message(request):
    """
    Endpoint para enviar mensajes y recibir análisis emocional
    
    Seguridad OWASP:
    - Validación de entrada
    - Sanitización de datos
    - Manejo seguro de errores
    
    Cumplimiento Ley 21.459:
    - Datos sensibles protegidos
    - No se almacena información personal sin consentimiento
    """
    try:
        # Validar y parsear datos de entrada
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        # Validación de entrada (OWASP)
        if not user_message:
            return JsonResponse({
                'error': 'Mensaje vacío',
                'success': False
            }, status=400)
        
        if len(user_message) > 2000:
            return JsonResponse({
                'error': 'Mensaje demasiado largo (máximo 2000 caracteres)',
                'success': False
            }, status=400)
        
        # Obtener ID de usuario (en producción usar autenticación real)
        user_id = request.session.get('user_id', 'anonymous')
        if 'user_id' not in request.session:
            import uuid
            request.session['user_id'] = str(uuid.uuid4())
            user_id = request.session['user_id']
        
        # Obtener historial de conversación
        conversation_history = data.get('history', [])
        
        # Obtener servicio
        emotion_service = get_emotion_service()
        
        # Análisis emocional completo mediante servicio
        result = emotion_service.analyze_text(
            user_id=user_id,
            text=user_message,
            conversation_history=conversation_history
        )
        
        if not result.get('success'):
            return JsonResponse({
                'error': result.get('error', 'Error desconocido'),
                'success': False
            }, status=500)
        
        # Respuesta exitosa con análisis emocional
        response_data = {
            'response': result['response'],
            'success': True,
            'emotion_analysis': result.get('emotion_analysis', {}),
            'alert_generated': result.get('alert_generated', False)
        }
        
        # Log de actividad (sin datos sensibles - ISO 27000)
        logger.info(
            f"Mensaje procesado - Emoción: {result['emotion_analysis'].get('emotion')} - "
            f"Alerta: {result.get('alert_generated')}"
        )
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        logger.warning("Request con JSON inválido")
        return JsonResponse({
            'error': 'Formato de datos inválido',
            'success': False
        }, status=400)
        
    except Exception as e:
        # Manejo seguro de errores (no exponer detalles internos - OWASP)
        logger.error(f"Error en send_message: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Error interno del servidor',
            'success': False
        }, status=500)


@csrf_exempt  # TODO: Implementar CSRF token en producción (OWASP)
@require_http_methods(["POST"])
def transcribe_audio(request):
    """
    Endpoint para transcribir audio y analizar emociones
    
    Speech-to-Text + Análisis Emocional integrado
    Cumplimiento: Ley 21.459 (protección de datos de voz)
    """
    try:
        # Validar archivo de audio
        if 'audio' not in request.FILES:
            return JsonResponse({
                'error': 'No se recibió archivo de audio',
                'success': False
            }, status=400)
        
        audio_file = request.FILES['audio']
        
        # Validar tamaño del archivo (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if audio_file.size > max_size:
            return JsonResponse({
                'error': 'Archivo de audio demasiado grande (máximo 10MB)',
                'success': False
            }, status=400)
        
        # Obtener ID de usuario
        user_id = request.session.get('user_id', 'anonymous')
        if 'user_id' not in request.session:
            import uuid
            request.session['user_id'] = str(uuid.uuid4())
            user_id = request.session['user_id']
        
        # Obtener servicio
        emotion_service = get_emotion_service()
        
        # Procesar audio mediante servicio
        result = emotion_service.analyze_audio(
            user_id=user_id,
            audio_data=audio_file.read(),
            filename=audio_file.name
        )
        
        if not result.get('success'):
            return JsonResponse({
                'error': result.get('error', 'Error al procesar audio'),
                'success': False
            }, status=500)
        
        # Respuesta con transcripción
        response_data = {
            'transcription': result.get('transcription', ''),
            'success': True
        }
        
        logger.info(f"Audio transcrito exitosamente - Usuario: {user_id[:8]}...")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error en transcribe_audio: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Error al procesar el audio',
            'success': False
        }, status=500)


@require_http_methods(["GET"])
def get_emotional_history(request):
    """
    Endpoint para obtener historial emocional del usuario
    
    Requiere autenticación en producción
    Cumplimiento: Ley 21.459 (acceso a datos personales)
    """
    try:
        user_id = request.session.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'error': 'Usuario no identificado',
                'success': False
            }, status=401)
        
        limit = int(request.GET.get('limit', 10))
        
        emotion_service = get_emotion_service()
        history = emotion_service.get_user_emotional_history(
            user_id=user_id,
            limit=limit
        )
        
        return JsonResponse({
            'history': history,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error en get_emotional_history: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener historial',
            'success': False
        }, status=500)


@require_http_methods(["GET"])
def get_statistics(request):
    """
    Endpoint para obtener estadísticas de análisis emocional
    
    Solo para administradores/profesionales autorizados
    """
    try:
        # TODO: Verificar permisos de administrador
        
        days = int(request.GET.get('days', 7))
        
        emotion_service = get_emotion_service()
        stats = emotion_service.get_statistics(days=days)
        
        return JsonResponse({
            'statistics': stats,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error en get_statistics: {str(e)}")
        return JsonResponse({
            'error': 'Error al obtener estadísticas',
            'success': False
        }, status=500)
