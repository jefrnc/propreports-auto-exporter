#!/usr/bin/env python3
"""
Exportador avanzado de PropReports con reprocesamiento
Permite exportar y re-exportar múltiples días
"""

import os
import json
from datetime import datetime, timedelta
from propreports_exporter import PropReportsExporter
from daily_exporter import obfuscate_account, ensure_directory_structure

def export_date_range(start_date, end_date, force_update=False):
    """
    Exporta un rango de fechas, con opción de forzar actualización
    
    Args:
        start_date: Fecha inicial (datetime o string YYYY-MM-DD)
        end_date: Fecha final (datetime o string YYYY-MM-DD)
        force_update: Si True, sobrescribe archivos existentes
    """
    # Configuración
    DOMAIN = os.getenv('PROPREPORTS_DOMAIN', 'zim.propreports.com')
    USERNAME = os.getenv('PROPREPORTS_USER', 'ZIMDASE9C64')
    PASSWORD = os.getenv('PROPREPORTS_PASS', 'Xby6lDWqAs')
    
    # Convertir strings a datetime si es necesario
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Crear exportador
    exporter = PropReportsExporter(DOMAIN, USERNAME, PASSWORD)
    
    # Login
    if not exporter.login():
        print("❌ Error en login")
        return []
    
    exported_files = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Crear estructura de directorios para la fecha específica
        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        daily_dir = os.path.join("exports", year, month, "daily")
        
        # Asegurar que el directorio existe
        os.makedirs(daily_dir, exist_ok=True)
        
        filename = os.path.join(daily_dir, f"{date_str}.json")
        
        if os.path.exists(filename) and not force_update:
            print(f"⏭️  {date_str}: Archivo ya existe (usar force_update=True para sobrescribir)")
            current_date += timedelta(days=1)
            continue
        
        print(f"\n📅 Procesando {date_str}...")
        
        # Obtener trades del día
        html_content = exporter.get_trades_page(date_str, date_str)
        if html_content:
            trades = exporter.parse_trades_html(html_content)
            
            # Filtrar solo trades de ese día
            day_trades = [t for t in trades if t.get('date') == date_str]
            
            # Preparar datos
            daily_data = {
                'exportDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'account': obfuscate_account(USERNAME),
                'date': date_str,
                'trades': day_trades,
                'summary': {
                    'totalTrades': len(day_trades),
                    'totalPnL': round(sum(t.get('pnl', 0) for t in day_trades), 2),
                    'totalCommissions': round(sum(t.get('commission', 0) for t in day_trades), 2),
                    'netPnL': round(sum(t.get('net', t.get('pnl', 0) - t.get('commission', 0)) for t in day_trades), 2),
                    'winningTrades': len([t for t in day_trades if t.get('pnl', 0) > 0]),
                    'losingTrades': len([t for t in day_trades if t.get('pnl', 0) < 0]),
                    'symbols': list(set(t.get('symbol', '') for t in day_trades if t.get('symbol')))
                },
                'metadata': {
                    'reprocessed': os.path.exists(filename),
                    'processedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            # Guardar
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, indent=2, ensure_ascii=False)
            
            action = "♻️  Actualizado" if daily_data['metadata']['reprocessed'] else "✅ Creado"
            print(f"  {action}: {len(day_trades)} trades, P&L: ${daily_data['summary']['netPnL']}")
            exported_files.append(filename)
        else:
            # Si no hay trades, crear archivo vacío
            print(f"  ⚠️  No se encontraron trades para {date_str}")
            
            # Crear archivo vacío solo si no existe
            if not os.path.exists(filename):
                empty_data = {
                    'exportDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'account': obfuscate_account(USERNAME),
                    'date': date_str,
                    'trades': [],
                    'summary': {
                        'totalTrades': 0,
                        'totalPnL': 0,
                        'totalCommissions': 0,
                        'netPnL': 0,
                        'winningTrades': 0,
                        'losingTrades': 0,
                        'symbols': []
                    },
                    'metadata': {
                        'reprocessed': False,
                        'processedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'note': 'No trades found for this date'
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(empty_data, f, indent=2, ensure_ascii=False)
                
                exported_files.append(filename)
        
        current_date += timedelta(days=1)
    
    return exported_files

def reprocess_recent_days(days_back=3, force=True):
    """
    Reprocesa los últimos N días (útil para trades que aparecen con delay)
    
    Args:
        days_back: Número de días hacia atrás para reprocesar
        force: Si True, sobrescribe archivos existentes
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"🔄 Reprocesando últimos {days_back} días...")
    print(f"📅 Desde {start_date.strftime('%Y-%m-%d')} hasta {end_date.strftime('%Y-%m-%d')}")
    
    return export_date_range(start_date, end_date, force_update=force)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "reprocess":
            # Reprocesar últimos días
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            reprocess_recent_days(days)
        elif sys.argv[1] == "range":
            # Exportar rango específico
            if len(sys.argv) >= 4:
                start = sys.argv[2]
                end = sys.argv[3]
                force = len(sys.argv) > 4 and sys.argv[4] == "force"
                export_date_range(start, end, force_update=force)
            else:
                print("Uso: python advanced_exporter.py range YYYY-MM-DD YYYY-MM-DD [force]")
    else:
        # Por defecto, exportar hoy y reprocesar últimos 2 días
        print("🚀 Exportación con reprocesamiento automático")
        export_date_range(datetime.now(), datetime.now())  # Hoy
        reprocess_recent_days(2, force=True)  # Últimos 2 días