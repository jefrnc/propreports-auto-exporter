# ❓ Frequently Asked Questions

## General

### ¿Es seguro usar esta Action?
Sí, tus credenciales se almacenan como GitHub Secrets encriptados y nunca se exponen en logs o commits.

### ¿Cuánto cuesta?
¡Es gratis! GitHub Actions ofrece:
- Repos públicos: Ilimitado
- Repos privados: 2,000 minutos/mes gratis

### ¿Funciona con cualquier PropReports?
Sí, solo necesitas ajustar el dominio en la configuración.

## Configuración

### ¿Cómo agrego los secrets?
1. Ve a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Agrega: PROPREPORTS_DOMAIN, PROPREPORTS_USER, PROPREPORTS_PASS

### ¿Puedo cambiar el horario de ejecución?
Sí, modifica el cron en tu workflow:
```yaml
schedule:
  - cron: '0 14 * * *'  # 2 PM UTC
```

[Cron expression generator](https://crontab.guru/)

### ¿Cómo ejecuto la exportación manualmente?
1. Ve a Actions en tu repo
2. Selecciona el workflow
3. Click "Run workflow"

## Problemas comunes

### Error: "Login failed"
- Verifica que los secrets estén configurados correctamente
- Confirma que puedes acceder manualmente a PropReports
- Revisa que el dominio sea correcto

### No se generan resúmenes semanales/mensuales
- Los semanales se generan automáticamente los domingos
- Los mensuales el último día del mes
- Puedes forzarlos con `generate-weekly: 'true'`

### Error: "No trades found"
- Es normal si no hay trades ese día
- El archivo se creará vacío para mantener el registro

### ¿Por qué faltan algunos trades?
**Los trades pueden aparecer con hasta 24 horas de retraso en PropReports.** Por esto:
- El sistema reprocesa automáticamente los últimos 2-3 días
- Los archivos se actualizan con nuevos trades cuando aparecen
- Puedes ajustar con `reprocess-days: '3'` para más días

### ¿Cómo funciona la ofuscación de cuentas?
Por defecto, los números de cuenta se ofuscan mostrando solo los primeros y últimos 2 caracteres:
- `ZIMDASE9C64` → `ZI*******64`
- Puedes desactivarlo con `obfuscate-account: 'false'`

## Personalización

### ¿Puedo cambiar el formato de exportación?
Actualmente exporta en JSON. Para otros formatos, puedes:
1. Fork el repositorio
2. Modificar los scripts en `src/`
3. Usar tu fork en la Action

### ¿Puedo agregar notificaciones?
Sí, puedes agregar steps adicionales:
```yaml
- name: Send notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
```

### ¿Cómo excluyo ciertos días?
Puedes modificar el cron o agregar condiciones:
```yaml
- name: Check if weekend
  run: |
    if [[ $(date +%u) -gt 5 ]]; then
      echo "Weekend, skipping"
      exit 0
    fi
```

## Datos

### ¿Dónde se guardan los datos?
En la carpeta `exports/` (o la que configures) de tu repositorio.

### ¿Puedo cambiar la estructura de carpetas?
La estructura año/mes/tipo está hardcodeada pero puedes modificarla en un fork.

### ¿Qué pasa si hay un error durante la exportación?
- La Action marcará el run como fallido
- Recibirás una notificación por email (si está habilitado)
- Los datos anteriores no se afectan

## Avanzado

### ¿Puedo usar múltiples cuentas?
No directamente, pero puedes:
1. Crear múltiples workflows
2. Usar diferentes secrets para cada cuenta
3. Exportar a diferentes carpetas

### ¿Cómo contribuyo al proyecto?
1. Fork el repositorio
2. Crea una rama para tu feature
3. Envía un Pull Request
4. ¡Gracias! 🙏

### ¿Puedo usar esto en mi empresa?
Sí, la licencia MIT lo permite. Considera:
- Hacer un fork privado
- Personalizar según necesidades
- Contribuir mejoras generales al proyecto