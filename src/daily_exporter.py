#!/usr/bin/env python3
"""
Exportador diario de PropReports
Exporta solo los trades del día actual
"""

import os
import json
from datetime import datetime, timedelta
from propreports_exporter import PropReportsExporter

def obfuscate_account(account_name):
    """Ofusca el nombre de cuenta para mayor seguridad"""
    if not account_name or len(account_name) < 4:
        return "****"
    
    # Mostrar primeros 2 y últimos 2 caracteres
    visible_start = 2
    visible_end = 2
    
    if len(account_name) <= visible_start + visible_end:
        return account_name[0] + "*" * (len(account_name) - 2) + account_name[-1]
    
    return account_name[:visible_start] + "*" * (len(account_name) - visible_start - visible_end) + account_name[-visible_end:]

def ensure_directory_structure():
    """Crea la estructura de directorios para organizar exports"""
    base_dir = "exports"
    year = datetime.now().strftime('%Y')
    month = datetime.now().strftime('%m')
    
    # Estructura: exports/2025/07/daily/
    directories = [
        base_dir,
        os.path.join(base_dir, year),
        os.path.join(base_dir, year, month),
        os.path.join(base_dir, year, month, "daily"),
        os.path.join(base_dir, year, month, "weekly"),
        os.path.join(base_dir, year, month, "monthly")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    return os.path.join(base_dir, year, month)

def export_daily_trades():
    """Exporta trades del día actual"""
    # Configuración
    DOMAIN = os.getenv('PROPREPORTS_DOMAIN', 'zim.propreports.com')
    USERNAME = os.getenv('PROPREPORTS_USER', 'ZIMDASE9C64')
    PASSWORD = os.getenv('PROPREPORTS_PASS', 'Xby6lDWqAs')
    
    # Crear exportador
    exporter = PropReportsExporter(DOMAIN, USERNAME, PASSWORD)
    
    # Login
    if not exporter.login():
        print("❌ Error en login")
        return None
    
    # Obtener trades de hoy
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Exportando trades del día: {today}")
    
    # Obtener HTML de trades
    html_content = exporter.get_trades_page(yesterday, today)
    if not html_content:
        print("❌ Error obteniendo trades")
        return None
    
    # Parsear trades
    trades = exporter.parse_trades_html(html_content)
    
    # Filtrar solo trades de hoy (por si acaso)
    todays_trades = [t for t in trades if t.get('date') == today]
    
    if not todays_trades:
        print(f"⚠️  No hay trades para el día {today}")
        # Aún así guardar archivo vacío para mantener registro
        todays_trades = []
    
    # Preparar estructura de datos
    daily_data = {
        'exportDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'account': obfuscate_account(USERNAME),
        'account_raw': USERNAME,  # Solo para uso interno, no se mostrará
        'date': today,
        'trades': todays_trades,
        'summary': {
            'totalTrades': len(todays_trades),
            'totalPnL': round(sum(t.get('pnl', 0) for t in todays_trades), 2),
            'totalCommissions': round(sum(t.get('commission', 0) for t in todays_trades), 2),
            'netPnL': round(sum(t.get('net', t.get('pnl', 0) - t.get('commission', 0)) for t in todays_trades), 2),
            'winningTrades': len([t for t in todays_trades if t.get('pnl', 0) > 0]),
            'losingTrades': len([t for t in todays_trades if t.get('pnl', 0) < 0]),
            'symbols': list(set(t.get('symbol', '') for t in todays_trades if t.get('symbol')))
        }
    }
    
    # Guardar en estructura de carpetas
    month_dir = ensure_directory_structure()
    daily_dir = os.path.join(month_dir, "daily")
    
    # Nombre del archivo: YYYY-MM-DD.json
    filename = os.path.join(daily_dir, f"{today}.json")
    
    # Guardar JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exportación diaria completada: {filename}")
    print(f"📊 Resumen: {daily_data['summary']['totalTrades']} trades, "
          f"P&L: ${daily_data['summary']['netPnL']}")
    
    return filename

if __name__ == "__main__":
    export_daily_trades()