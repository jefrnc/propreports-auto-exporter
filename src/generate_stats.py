#!/usr/bin/env python3
"""
Generador de estadísticas dinámicas para el README
"""

import os
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict

def load_json_file(filepath):
    """Carga un archivo JSON de forma segura"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def get_current_week_stats():
    """Obtiene estadísticas de la semana actual"""
    today = datetime.now()
    week_num = today.isocalendar()[1]
    year = today.year
    
    # Buscar archivo de la semana actual
    weekly_file = f"exports/weekly/{year}-W{week_num:02d}.json"
    
    if os.path.exists(weekly_file):
        data = load_json_file(weekly_file)
        if data:
            return {
                'period': f"Week {week_num}",
                'trades': data['summary']['totalTrades'],
                'pnl': data['summary']['netPnL'],
                'winRate': f"{data['summary']['winRate']*100:.1f}%"
            }
    
    # Si no existe, calcular desde archivos diarios
    monday = today - timedelta(days=today.weekday())
    stats = calculate_period_stats(monday, today)
    stats['period'] = f"Week {week_num} (partial)"
    return stats

def get_last_week_stats():
    """Obtiene estadísticas de la semana anterior"""
    today = datetime.now()
    last_monday = today - timedelta(days=today.weekday() + 7)
    week_num = last_monday.isocalendar()[1]
    year = last_monday.year
    
    weekly_file = f"exports/weekly/{year}-W{week_num:02d}.json"
    
    if os.path.exists(weekly_file):
        data = load_json_file(weekly_file)
        if data:
            return {
                'period': f"Week {week_num}",
                'trades': data['summary']['totalTrades'],
                'pnl': data['summary']['netPnL'],
                'winRate': f"{data['summary']['winRate']*100:.1f}%"
            }
    
    return {'period': f"Week {week_num}", 'trades': 0, 'pnl': 0, 'winRate': "0%"}

def get_current_month_stats():
    """Obtiene estadísticas del mes actual"""
    today = datetime.now()
    month = today.month
    year = today.year
    
    # Calcular desde archivos diarios
    first_day = datetime(year, month, 1)
    stats = calculate_period_stats(first_day, today)
    stats['period'] = f"{today.strftime('%B')} (partial)"
    return stats

def get_last_month_stats():
    """Obtiene estadísticas del mes anterior"""
    today = datetime.now()
    if today.month == 1:
        month = 12
        year = today.year - 1
    else:
        month = today.month - 1
        year = today.year
    
    monthly_file = f"exports/monthly/{year}-{month:02d}.json"
    
    if os.path.exists(monthly_file):
        data = load_json_file(monthly_file)
        if data:
            return {
                'period': data['monthName'],
                'trades': data['overview']['totalTrades'],
                'pnl': data['overview']['netPnL'],
                'winRate': f"{data['overview']['winRate']*100:.1f}%"
            }
    
    return {'period': datetime(year, month, 1).strftime('%B'), 'trades': 0, 'pnl': 0, 'winRate': "0%"}

def calculate_period_stats(start_date, end_date):
    """Calcula estadísticas para un período desde archivos diarios"""
    total_trades = 0
    total_pnl = 0
    winning_trades = 0
    
    current = start_date
    while current <= end_date:
        daily_file = f"exports/daily/{current.strftime('%Y-%m-%d')}.json"
        if os.path.exists(daily_file):
            data = load_json_file(daily_file)
            if data and data.get('trades'):
                total_trades += len(data['trades'])
                total_pnl += data['summary']['netPnL']
                winning_trades += data['summary']['winningTrades']
        current += timedelta(days=1)
    
    win_rate = f"{(winning_trades/total_trades*100):.1f}%" if total_trades > 0 else "0%"
    
    return {
        'trades': total_trades,
        'pnl': round(total_pnl, 2),
        'winRate': win_rate
    }

def calculate_yearly_projection():
    """Calcula proyección anual basada en el rendimiento hasta ahora"""
    # Obtener todos los archivos mensuales del año actual
    year = datetime.now().year
    monthly_files = sorted(glob.glob(f"exports/monthly/{year}-*.json"))
    
    total_pnl = 0
    total_trades = 0
    months_with_data = 0
    
    for file in monthly_files:
        data = load_json_file(file)
        if data:
            total_pnl += data['overview']['netPnL']
            total_trades += data['overview']['totalTrades']
            months_with_data += 1
    
    # Agregar mes actual
    current_month_stats = get_current_month_stats()
    total_pnl += current_month_stats['pnl']
    total_trades += current_month_stats['trades']
    
    # Calcular días transcurridos vs días totales del año
    today = datetime.now()
    days_passed = (today - datetime(year, 1, 1)).days + 1
    days_in_year = 365 + (1 if year % 4 == 0 else 0)
    
    # Proyección
    if days_passed > 0:
        daily_avg_pnl = total_pnl / days_passed
        daily_avg_trades = total_trades / days_passed
        
        projected_pnl = daily_avg_pnl * days_in_year
        projected_trades = int(daily_avg_trades * days_in_year)
        
        return {
            'actual_pnl': round(total_pnl, 2),
            'projected_pnl': round(projected_pnl, 2),
            'actual_trades': total_trades,
            'projected_trades': projected_trades,
            'days_remaining': days_in_year - days_passed
        }
    
    return None

def format_pnl(value):
    """Formatea P&L con color"""
    if value > 0:
        return f"**+${value:,.2f}**"
    elif value < 0:
        return f"**-${abs(value):,.2f}**"
    else:
        return f"${value:,.2f}"

def generate_stats_table():
    """Genera la tabla de estadísticas en formato Markdown"""
    # Obtener todas las estadísticas
    current_week = get_current_week_stats()
    last_week = get_last_week_stats()
    current_month = get_current_month_stats()
    last_month = get_last_month_stats()
    yearly = calculate_yearly_projection()
    
    # Generar tabla
    table = "### 📊 Live Trading Statistics\n\n"
    table += "| Period | Trades | P&L | Win Rate |\n"
    table += "|--------|--------|-----|----------|\n"
    
    # Semanas
    table += f"| **{current_week['period']}** | {current_week['trades']} | {format_pnl(current_week['pnl'])} | {current_week['winRate']} |\n"
    table += f"| {last_week['period']} | {last_week['trades']} | {format_pnl(last_week['pnl'])} | {last_week['winRate']} |\n"
    
    # Meses
    table += f"| **{current_month['period']}** | {current_month['trades']} | {format_pnl(current_month['pnl'])} | {current_month['winRate']} |\n"
    table += f"| {last_month['period']} | {last_month['trades']} | {format_pnl(last_month['pnl'])} | {last_month['winRate']} |\n"
    
    # Proyección anual
    if yearly:
        table += "\n#### 📈 Yearly Projection\n\n"
        table += "| Metric | Actual YTD | Projected EOY |\n"
        table += "|--------|------------|---------------|\n"
        table += f"| **Trades** | {yearly['actual_trades']:,} | {yearly['projected_trades']:,} |\n"
        table += f"| **P&L** | {format_pnl(yearly['actual_pnl'])} | {format_pnl(yearly['projected_pnl'])} |\n"
        table += f"\n*Based on current performance with {yearly['days_remaining']} days remaining*\n"
    
    table += f"\n*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC*"
    
    return table

def update_readme(stats_table):
    """Actualiza el README con las estadísticas"""
    readme_path = "README.md"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar los marcadores
    start_marker = "<!-- STATS_START -->"
    end_marker = "<!-- STATS_END -->"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # Reemplazar contenido entre marcadores
        new_content = (
            content[:start_idx + len(start_marker)] + 
            "\n" + stats_table + "\n" +
            content[end_idx:]
        )
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ README actualizado con estadísticas")
        return True
    else:
        print("⚠️  No se encontraron marcadores STATS en el README")
        return False

if __name__ == "__main__":
    # Cambiar al directorio base si es necesario
    if not os.path.exists("exports"):
        print("❌ No se encontró el directorio exports")
        exit(1)
    
    # Generar estadísticas
    stats_table = generate_stats_table()
    print("\n📊 Estadísticas generadas:")
    print(stats_table)
    
    # Actualizar README con estadísticas
    update_readme(stats_table)
    
    # También generar calendario
    try:
        from generate_calendar import generate_markdown_calendar, generate_monthly_breakdown, update_readme_with_calendar
        
        year = datetime.now().year
        calendar_md, stats = generate_markdown_calendar(year)
        monthly_breakdown = generate_monthly_breakdown(year)
        full_calendar = calendar_md + monthly_breakdown
        
        print("\n📅 Calendario generado")
        update_readme_with_calendar(full_calendar)
    except Exception as e:
        print(f"⚠️  Error generando calendario: {e}")