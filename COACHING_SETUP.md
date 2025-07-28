# 🤖 AI Trading Coach Setup

Este sistema proporciona análisis automatizado de performance usando OpenAI GPT-4 para generar insights y recomendaciones personalizadas sobre tu trading.

## 🚀 Características

### Análisis Mensual
- **Cuándo se ejecuta**: Día 2 de cada mes a las 9:00 AM UTC
- **Contenido**:
  - Análisis comparativo con el mes anterior
  - Fortalezas identificadas
  - Áreas de mejora
  - Insights clave sobre patrones
  - Recomendaciones accionables
  - Evaluación de gestión de riesgo
  - Objetivos para el próximo mes

### Análisis Semanal
- **Cuándo se ejecuta**: Cada lunes a las 10:00 AM UTC
- **Contenido**:
  - Resumen de performance semanal
  - Patrones diarios identificados
  - Mejoras rápidas (quick wins)
  - Señales de alerta
  - Enfoque para la próxima semana
  - Ajustes tácticos recomendados

## ⚙️ Configuración

### 1. Configurar API Key de OpenAI

En tu repositorio de GitHub, ve a **Settings > Secrets and variables > Actions** y agrega:

```
OPENAI_API_KEY = <tu-api-key-de-openai>
```

> ⚠️ **Importante**: Nunca compartas tu API key públicamente. Siempre úsala como secreto de GitHub.

### 2. Habilitar el Coaching

Agrega otro secreto para habilitar la funcionalidad:

```
ENABLE_COACHING = true
```

### 3. Verificar Permisos

Asegúrate de que las GitHub Actions tengan permisos para:
- Leer el repositorio
- Escribir en el repositorio (para commitear reportes)
- Crear issues (para notificaciones)

## 📊 Cómo Aparece en el Dashboard

Una vez configurado, verás una nueva sección **"AI Trading Coach"** al final de tu dashboard que incluye:

- 📊 **Monthly Performance Review**: Análisis detallado del mes con fortalezas, áreas de mejora y objetivos
- 📈 **Weekly Performance Review**: Revisión semanal con quick wins y ajustes tácticos

## 🔧 Uso Manual

También puedes ejecutar el coaching manualmente:

### Análisis Mensual Manual
```bash
cd src
python trading_coach.py monthly --year 2025 --month 7
```

### Análisis Semanal Manual
```bash
cd src
python trading_coach.py weekly --year 2025 --week 30
```

### Modo Automático
```bash
# Analiza el período más reciente automáticamente
python trading_coach.py monthly --auto
python trading_coach.py weekly --auto
```

## 💰 Consideraciones de Costo

Para optimizar el uso de créditos de OpenAI:

1. **Frecuencia inteligente**: Solo se ejecuta cuando hay datos nuevos
2. **Análisis eficiente**: Usa prompts optimizados para obtener máximo valor
3. **Control de activación**: Se puede habilitar/deshabilitar fácilmente
4. **Contexto relevante**: Solo analiza datos significativos

**Costo estimado**: ~$0.50-2.00 USD por mes (dependiendo del volumen de trades)

## 🚨 Solución de Problemas

### El coaching no aparece en el dashboard
1. Verifica que `ENABLE_COACHING = true`
2. Revisa que `OPENAI_API_KEY` esté configurado
3. Confirma que las GitHub Actions se ejecutaron correctamente

### Error en GitHub Actions
1. Revisa los logs de la action en la pestaña "Actions"
2. Verifica que todos los secretos estén configurados
3. Asegúrate de que el API key de OpenAI sea válido

### Datos de coaching no se actualizan
1. El coaching solo se ejecuta cuando hay datos nuevos de trading
2. Verifica que los datos mensuales/semanales existan
3. Ejecuta manualmente para probar: `python trading_coach.py monthly --auto`

## 📝 Estructura de Archivos

El sistema crea la siguiente estructura:

```
exports/
├── coaching/
│   ├── monthly/
│   │   └── 2025-07.json    # Reporte mensual
│   └── weekly/
│       └── 2025-W30.json   # Reporte semanal
```

## 🔄 Desactivar el Coaching

Para deshabilitar temporalmente:
1. Cambia `ENABLE_COACHING` a `false`
2. O elimina el secreto `ENABLE_COACHING`

Las GitHub Actions seguirán ejecutándose pero saltarán el análisis.

## 🎯 Personalización

El sistema analiza automáticamente:
- ✅ Win rate vs profit factor
- ✅ Gestión de riesgo y position sizing
- ✅ Frecuencia de trading y overtrading
- ✅ Aspectos psicológicos y disciplina
- ✅ Adaptabilidad a condiciones de mercado
- ✅ Eficiencia en comisiones
- ✅ Consistencia en performance

Los insights están diseñados para ser **específicos, accionables y constructivos**.