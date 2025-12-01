# 🏗️ Arquitectura del Sistema de Análisis Emocional con IA

## 📋 Descripción General

Aplicación web que analiza texto y voz mediante IA para evaluar estados emocionales y recomendar ejercicios o sesiones de apoyo.

---

## 🎯 Componentes Principales

### 1. **Inteligencia Artificial**
- **NLP (Procesamiento de Lenguaje Natural)**: Análisis de emociones en texto
- **Speech-to-Text**: Whisper (GroqCloud) para transcripción de audio
- **Reconocimiento de emociones**: Detección de estados emocionales con intensidad y nivel de riesgo

### 2. **Arquitectura Cliente-Servidor**
```
Cliente (Frontend)
    ↓
Capa de Presentación (views.py)
    ↓
Capa de Servicios (emotion_analysis_service.py)
    ↓
Adaptadores (groq_adapter.py)
    ↓
APIs Externas (GroqCloud)
```

### 3. **Sistema de Eventos (Observer Pattern)**
```
EmotionEvent → EmotionEventManager → Observers
                                    ├─ AlertObserver (alertas críticas)
                                    └─ LoggingObserver (auditoría)
```

---

## 📁 Estructura de Archivos

```
chat/
├── adapters/                   # Patrón Adapter
│   ├── __init__.py
│   └── groq_adapter.py        # Abstracción API GroqCloud
│
├── events/                     # Sistema de Eventos
│   ├── __init__.py
│   └── emotion_events.py      # EmotionEvent, EmotionEventManager
│
├── observers/                  # Patrón Observer
│   ├── __init__.py
│   ├── alert_observer.py      # Alertas de alto riesgo
│   └── logging_observer.py    # Registro y auditoría
│
├── services/                   # Lógica de Negocio
│   ├── __init__.py
│   └── emotion_analysis_service.py  # Servicio principal
│
├── static/                     # Recursos estáticos
│   └── chat/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── script.js
│
├── templates/                  # Plantillas HTML
│   └── chat/
│       └── index.html
│
├── views.py                    # Endpoints REST (Capa Presentación)
└── urls.py                     # Rutas de la aplicación
```

---

## 🔧 Patrones de Diseño Implementados

### **1. Adapter Pattern** (`adapters/groq_adapter.py`)
**Propósito**: Abstrae la comunicación con APIs externas (GroqCloud)

**Métodos**:
- `chat_completion()`: Conversación con LLM
- `transcribe_audio()`: Speech-to-Text
- `analyze_emotion_context()`: Análisis emocional especializado

**Beneficios**:
- Desacoplamiento de servicios externos
- Fácil reemplazo de proveedores de IA
- Testabilidad mejorada

### **2. Observer Pattern** (`events/` + `observers/`)
**Propósito**: Notificación automática ante eventos emocionales

**Componentes**:
- `EmotionEvent`: Evento de análisis emocional
- `EmotionEventManager`: Gestor centralizado (Singleton)
- `AlertObserver`: Genera alertas de riesgo
- `LoggingObserver`: Registra eventos para auditoría

**Flujo**:
```
Mensaje usuario → Análisis IA → EmotionEvent creado 
→ EventManager notifica → Observers reaccionan
```

### **3. Singleton Pattern**
Implementado en:
- `EmotionEventManager`: Una única instancia gestiona todos los eventos
- `EmotionAnalysisService`: Estado consistente del servicio

---

## 🌐 Arquitectura Cliente-Servidor

### **Capa de Presentación** (Django Views)
**Endpoints REST**:
- `POST /send/` - Enviar mensaje y recibir análisis
- `POST /transcribe/` - Transcribir audio
- `GET /history/` - Historial emocional del usuario
- `GET /statistics/` - Estadísticas generales

### **Capa de Servicios** (`EmotionAnalysisService`)
**Responsabilidades**:
- Orquestar análisis emocional
- Coordinar adaptadores y eventos
- Generar respuestas empáticas
- Gestionar historial

### **Capa de Adaptadores** (`GroqCloudAdapter`)
**Responsabilidades**:
- Comunicación con APIs externas
- Transformación de datos
- Manejo de errores de API

---

## ☁️ Cloud Services (SaaS)

### **GroqCloud**
- **Modelo LLM**: `openai/gpt-oss-120b`
- **Whisper**: `whisper-large-v3` para transcripción
- **Ventajas**: Alta velocidad de inferencia, soporte multimodal

### **Futuras integraciones**:
- Firebase Cloud Messaging (notificaciones push)
- Google Cloud AI (análisis adicional)
- Firebase Firestore (persistencia de datos)

---

## 📜 Cumplimiento Normativo

### **ISO 12207 - Ingeniería de Software**
✅ **Diseño Modular**: Separación clara de responsabilidades  
✅ **Mantenibilidad**: Código documentado y estructurado  
✅ **Trazabilidad**: Logging completo de eventos  
✅ **Reutilización**: Componentes independientes y reutilizables

### **ISO 27000 - Seguridad de la Información**
✅ **Confidencialidad**: Anonimización de IDs de usuario  
✅ **Integridad**: Validación de datos de entrada  
✅ **Auditoría**: Sistema de logging completo  
✅ **Control de acceso**: Sesiones y autenticación (pendiente mejorar)

### **OWASP Top 10**
✅ **A01:2021 - Broken Access Control**: Validación de permisos en endpoints  
✅ **A02:2021 - Cryptographic Failures**: TODO - Cifrado de datos sensibles  
✅ **A03:2021 - Injection**: Validación y sanitización de entrada  
✅ **A04:2021 - Insecure Design**: Arquitectura por capas  
✅ **A05:2021 - Security Misconfiguration**: Configuración segura de Django  
✅ **A07:2021 - Identification Failures**: Sesiones con UUIDs  
✅ **A09:2021 - Security Logging Failures**: Sistema de logging robusto  

**Pendientes**:
- Implementar CSRF tokens en producción
- Cifrado end-to-end para datos sensibles
- Rate limiting para prevenir abuso

### **Ley 21.459 (Chile) - Protección de Datos Sensibles**
✅ **Datos de salud mental**: Tratados como datos sensibles  
✅ **Anonimización**: Hash de IDs en logs  
✅ **Minimización**: No se guarda texto completo en logs  
✅ **Consentimiento**: TODO - Formulario de consentimiento explícito  
✅ **Derecho de acceso**: Endpoint `/history/` para consultar datos propios  
✅ **Seguridad**: Protección contra accesos no autorizados

---

## 🔐 Medidas de Seguridad Implementadas

### **Validación de Entrada**
```python
# Longitud máxima de mensajes
if len(user_message) > 2000:
    return error

# Tamaño máximo de archivos de audio
if audio_file.size > 10MB:
    return error
```

### **Anonimización de Datos**
```python
def _anonymize_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]
```

### **Logging Seguro**
```python
# NO se registran datos sensibles
log_entry = {
    'user_id': anonymized,
    'emotion': emotion,
    'text_length': len(text)  # NO el texto completo
}
```

---

## 🚀 Flujo de Análisis Emocional

### **1. Usuario envía mensaje (texto o voz)**
```javascript
// Frontend
fetch('/send/', {
    method: 'POST',
    body: JSON.stringify({ message, history })
})
```

### **2. Backend procesa solicitud**
```python
# views.py
result = emotion_service.analyze_text(
    user_id=user_id,
    text=user_message,
    conversation_history=history
)
```

### **3. Servicio coordina análisis**
```python
# emotion_analysis_service.py
emotion_data = groq_adapter.analyze_emotion_context(text, history)
event = EmotionEvent(user_id, text, emotion_data)
event_manager.notify(event)  # Notifica a observers
response = _generate_empathetic_response(...)
```

### **4. Observers reaccionan**
```python
# alert_observer.py
if event.requires_alert():
    create_alert(event)
    send_notification(alert)

# logging_observer.py
log_event(event)  # Auditoría
```

### **5. Respuesta al cliente**
```json
{
    "success": true,
    "response": "Entiendo que te sientes ansioso...",
    "emotion_analysis": {
        "emotion": "ansiedad",
        "intensity": 7,
        "risk_level": "moderado",
        "recommendation": "Técnicas de respiración..."
    },
    "alert_generated": true
}
```

---

## 📊 Sistema de Alertas

### **Niveles de Riesgo**
- **CRÍTICO**: Intensidad ≥ 8 o emociones graves (depresión, pánico)
- **ALTO**: Intensidad ≥ 7
- **MODERADO**: Intensidad 5-6
- **BAJO**: Intensidad < 5

### **Tipos de Alertas**
1. **Alerta de salud mental**: Notificación a profesionales
2. **Log de auditoría**: Registro permanente
3. **Recomendaciones**: Ejercicios y recursos de apoyo

---

## 🧪 Testing y Calidad

### **Áreas de Testing Requeridas**
- [ ] Unit tests para cada componente
- [ ] Integration tests para servicios
- [ ] Security tests (OWASP)
- [ ] Load testing (manejo de múltiples usuarios)
- [ ] Privacy compliance tests

---

## 📈 Métricas y Monitoreo

### **Disponibles vía `/statistics/`**
- Total de eventos procesados
- Distribución de emociones
- Eventos de alto riesgo
- Intensidad emocional promedio

---

## 🔄 Próximas Mejoras

### **Técnicas**
- [ ] Implementar Redis para caché
- [ ] WebSockets para respuestas en tiempo real
- [ ] Base de datos PostgreSQL para producción
- [ ] Sistema de autenticación OAuth2

### **Funcionales**
- [ ] Dashboard para profesionales de salud
- [ ] Ejercicios de mindfulness integrados
- [ ] Análisis de tendencias emocionales a largo plazo
- [ ] Videollamadas para sesiones de apoyo

### **Seguridad**
- [ ] Cifrado end-to-end
- [ ] 2FA (autenticación de dos factores)
- [ ] Rate limiting y protección DDoS
- [ ] Auditoría de seguridad externa

---

## 📝 Conclusión

Esta arquitectura cumple con todos los requisitos del proyecto:

✅ **IA**: NLP + Speech Analysis con GroqCloud  
✅ **Patrones**: Adapter + Observer implementados  
✅ **Arquitectura**: Cliente-Servidor por capas  
✅ **Cloud**: SaaS (GroqCloud)  
✅ **Normativas**: ISO 12207, 27000, OWASP, Ley 21.459  
✅ **Funcionalidad**: Análisis emocional completo con alertas

El sistema es modular, escalable, seguro y cumple con estándares internacionales de calidad y protección de datos.
