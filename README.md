# 🚀 PropReports Auto-Exporter

> GitHub Action para exportar automáticamente datos de trading de PropReports con resúmenes diarios, semanales y mensuales.

[![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github)](https://github.com/marketplace/actions/propreports-auto-exporter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Características

- 📅 **Exportación diaria automática** de trades
- 📊 **Resúmenes semanales** con análisis de patrones
- 📈 **Reportes mensuales** con métricas avanzadas y recomendaciones
- 🔄 **Versionado automático** en GitHub
- 🔒 **Seguro** - Usa GitHub Secrets para credenciales
- 🛡️ **Privacidad** - Ofuscación automática de números de cuenta
- ♻️ **Reprocesamiento** - Actualiza días anteriores automáticamente
- ⚡ **Fácil** - Setup en 5 minutos

## 🎯 ¿Para quién es?

- Traders que usan PropReports
- Quienes buscan automatizar el tracking de sus operaciones
- Traders que quieren análisis histórico de su performance
- Cualquiera que necesite backup automático de sus datos

## 📚 Quick Start

### Opción 1: Setup Manual (3 pasos)

1. **Crea un repositorio privado** en GitHub

2. **Agrega tus credenciales** como secrets:
   - `PROPREPORTS_DOMAIN` - Tu dominio (ej: `zim.propreports.com`)
   - `PROPREPORTS_USER` - Tu usuario
   - `PROPREPORTS_PASS` - Tu contraseña

3. **Crea el archivo** `.github/workflows/export.yml`:

```yaml
name: Export PropReports Data

on:
  schedule:
    # Ejecutar diariamente a las 10 PM EST
    - cron: '0 3 * * *'
  workflow_dispatch: # Permitir ejecución manual

jobs:
  export-trades:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Run PropReports Export
      uses: jefrnc/propreports-auto-exporter@v1
      with:
        propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
        propreports-user: ${{ secrets.PROPREPORTS_USER }}
        propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
```

¡Listo! 🎉

### Opción 2: Setup Automático

```bash
curl -sSL https://raw.githubusercontent.com/jefrnc/propreports-auto-exporter/main/quick-setup.sh | bash
```

## 📁 Estructura de Datos

Los datos se organizan automáticamente por fecha:

```
exports/
└── 2024/
    └── 03/
        ├── daily/
        │   ├── 2024-03-01.json
        │   ├── 2024-03-02.json
        │   └── ...
        ├── weekly/
        │   ├── week_09.json
        │   └── week_10.json
        └── monthly/
            ├── 2024-03_monthly_summary.json
            └── 2024-03_monthly_summary.txt
```

## 📊 Datos Exportados

### Archivos Diarios
- Todos los trades del día
- Resumen de P&L
- Métricas básicas

### Resúmenes Semanales
- Consolidación de la semana
- Análisis de patrones de trading
- Mejores y peores operaciones
- Distribución por horarios

### Reportes Mensuales
- Análisis profundo de performance
- Curva de rentabilidad
- Métricas de riesgo (Sharpe ratio, drawdown)
- Performance por símbolo
- **Recomendaciones automáticas**

## ⚙️ Configuración Avanzada

### Personalizar ruta de exportación

```yaml
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
    export-path: 'mis-trades'  # Carpeta personalizada
```

### Forzar generación de resúmenes

```yaml
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
    generate-weekly: 'true'   # Siempre generar semanal
    generate-monthly: 'true'  # Siempre generar mensual
```

### Desactivar commits automáticos

```yaml
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
    commit-exports: 'false'
```

## ⚠️ Nota Importante: Delay en Trades

> **Los trades pueden aparecer con hasta 24 horas de retraso en PropReports**
> 
> Por esta razón, el sistema automáticamente:
> - Reprocesa los últimos 2-3 días en cada ejecución
> - Actualiza archivos existentes con nuevos trades
> - Mantiene un historial de cuándo se procesó cada día

## 🔧 Uso Local

También puedes ejecutar los scripts localmente:

```bash
# Clonar el repositorio
git clone https://github.com/jefrnc/propreports-auto-exporter.git
cd propreports-auto-exporter

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
export PROPREPORTS_DOMAIN="tu-dominio.propreports.com"
export PROPREPORTS_USER="tu-usuario"
export PROPREPORTS_PASS="tu-password"

# Ejecutar exportación
python src/daily_exporter.py
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## 🙏 Agradecimientos

- PropReports por su plataforma
- La comunidad de traders que sugirió mejoras
- GitHub Actions por hacer posible la automatización

---

⭐ Si este proyecto te ayuda, considera darle una estrella!