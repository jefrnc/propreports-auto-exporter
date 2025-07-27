#!/usr/bin/env python3
"""
Generador de calendario de trading estilo GitHub contributions
"""

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

def load_json_file(filepath):
    """Carga un archivo JSON de forma segura"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def get_year_data(year):
    """Obtiene todos los datos de trading de un año"""
    daily_data = {}
    
    # Cargar todos los archivos diarios del año
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    current = start_date
    while current <= end_date:
        date_str = current.strftime('%Y-%m-%d')
        filepath = f"exports/daily/{date_str}.json"
        
        if os.path.exists(filepath):
            data = load_json_file(filepath)
            if data:
                daily_data[date_str] = {
                    'trades': data['summary']['totalTrades'],
                    'pnl': data['summary']['netPnL'],
                    'winRate': data['summary']['winningTrades'] / data['summary']['totalTrades'] if data['summary']['totalTrades'] > 0 else 0
                }
        
        current += timedelta(days=1)
    
    return daily_data

def generate_svg_calendar(year_data, year):
    """Genera un calendario SVG estilo GitHub contributions"""
    # Configuración
    cell_size = 11
    cell_gap = 2
    month_label_height = 20
    day_label_width = 30
    
    # Calcular dimensiones
    weeks = 53
    width = day_label_width + (weeks * (cell_size + cell_gap))
    height = month_label_height + (7 * (cell_size + cell_gap))
    
    # Iniciar SVG
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n'
    svg += '<style>\n'
    svg += '.day { stroke: #e1e4e8; stroke-width: 1px; }\n'
    svg += '.day:hover { stroke: #000; stroke-width: 2px; }\n'
    svg += '.month-label { font-size: 10px; fill: #586069; }\n'
    svg += '.day-label { font-size: 9px; fill: #586069; }\n'
    svg += '</style>\n'
    
    # Labels de días
    days = ['', 'Mon', '', 'Wed', '', 'Fri', '']
    for i, day in enumerate(days):
        if day:
            y = month_label_height + (i * (cell_size + cell_gap)) + 9
            svg += f'<text x="2" y="{y}" class="day-label">{day}</text>\n'
    
    # Labels de meses
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_positions = {}
    
    # Generar celdas del calendario
    start_date = datetime(year, 1, 1)
    start_weekday = start_date.weekday()
    
    for day_offset in range(366):  # Máximo días en un año
        current_date = start_date + timedelta(days=day_offset)
        if current_date.year != year:
            break
        
        date_str = current_date.strftime('%Y-%m-%d')
        week_num = (day_offset + start_weekday) // 7
        day_of_week = current_date.weekday()
        
        # Guardar posición del primer día de cada mes
        if current_date.day == 1:
            month_positions[current_date.month] = week_num
        
        x = day_label_width + (week_num * (cell_size + cell_gap))
        y = month_label_height + (day_of_week * (cell_size + cell_gap))
        
        # Determinar color basado en P&L
        data = year_data.get(date_str, {'trades': 0, 'pnl': 0})
        color = get_color_for_pnl(data['pnl'], data['trades'])
        
        # Tooltip con información
        tooltip = f"{date_str}: {data['trades']} trades, P&L: ${data['pnl']:.2f}"
        
        svg += f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
        svg += f'fill="{color}" class="day" data-date="{date_str}" '
        svg += f'data-trades="{data["trades"]}" data-pnl="{data["pnl"]:.2f}">\n'
        svg += f'<title>{tooltip}</title>\n'
        svg += '</rect>\n'
    
    # Agregar labels de meses
    for month, week in month_positions.items():
        x = day_label_width + (week * (cell_size + cell_gap))
        svg += f'<text x="{x}" y="12" class="month-label">{months[month-1]}</text>\n'
    
    svg += '</svg>'
    return svg

def get_color_for_pnl(pnl, trades):
    """Determina el color basado en P&L y cantidad de trades"""
    if trades == 0:
        return '#ebedf0'  # Gris - sin trades
    elif pnl > 100:
        return '#196127'  # Verde muy oscuro - gran ganancia
    elif pnl > 50:
        return '#239a3b'  # Verde oscuro
    elif pnl > 0:
        return '#7bc96f'  # Verde claro
    elif pnl == 0:
        return '#c6e48b'  # Verde muy claro - breakeven
    elif pnl > -50:
        return '#ffeb3b'  # Amarillo - pérdida pequeña
    elif pnl > -100:
        return '#ff9800'  # Naranja - pérdida moderada
    else:
        return '#f44336'  # Rojo - pérdida grande

def generate_markdown_calendar(year):
    """Genera calendario en formato Markdown con estadísticas"""
    year_data = get_year_data(year)
    
    # Generar SVG
    svg = generate_svg_calendar(year_data, year)
    
    # Calcular estadísticas
    stats = calculate_year_stats(year_data)
    
    # Generar Markdown
    markdown = f"## 📅 {year} Trading Calendar\n\n"
    markdown += f"![Trading Calendar](.github/assets/calendar-{year}.svg)\n\n"
    
    # Leyenda
    markdown += "### Legend\n"
    markdown += "🟩 Profit Day | 🟨 Break Even | 🟥 Loss Day | ⬜ No Trades\n\n"
    
    # Estadísticas anuales
    markdown += f"### 📊 {year} Statistics\n\n"
    markdown += "| Metric | Value |\n"
    markdown += "|--------|-------|\n"
    markdown += f"| **Total Trading Days** | {stats['trading_days']} |\n"
    markdown += f"| **Total Trades** | {stats['total_trades']:,} |\n"
    markdown += f"| **Total P&L** | ${stats['total_pnl']:,.2f} |\n"
    markdown += f"| **Win Rate** | {stats['win_rate']:.1f}% |\n"
    markdown += f"| **Profit Days** | {stats['profit_days']} ({stats['profit_days_pct']:.1f}%) |\n"
    markdown += f"| **Loss Days** | {stats['loss_days']} ({stats['loss_days_pct']:.1f}%) |\n"
    markdown += f"| **Best Day** | ${stats['best_day_pnl']:.2f} ({stats['best_day']}) |\n"
    markdown += f"| **Worst Day** | ${stats['worst_day_pnl']:.2f} ({stats['worst_day']}) |\n"
    markdown += f"| **Daily Average** | ${stats['daily_avg']:.2f} |\n"
    
    # Guardar SVG
    os.makedirs('.github/assets', exist_ok=True)
    with open(f'.github/assets/calendar-{year}.svg', 'w') as f:
        f.write(svg)
    
    return markdown, stats

def calculate_year_stats(year_data):
    """Calcula estadísticas del año"""
    total_trades = 0
    total_pnl = 0
    profit_days = 0
    loss_days = 0
    best_day = None
    worst_day = None
    best_pnl = -float('inf')
    worst_pnl = float('inf')
    
    for date, data in year_data.items():
        if data['trades'] > 0:
            total_trades += data['trades']
            total_pnl += data['pnl']
            
            if data['pnl'] > 0:
                profit_days += 1
            elif data['pnl'] < 0:
                loss_days += 1
            
            if data['pnl'] > best_pnl:
                best_pnl = data['pnl']
                best_day = date
            
            if data['pnl'] < worst_pnl:
                worst_pnl = data['pnl']
                worst_day = date
    
    trading_days = len([d for d in year_data.values() if d['trades'] > 0])
    
    return {
        'trading_days': trading_days,
        'total_trades': total_trades,
        'total_pnl': total_pnl,
        'win_rate': (profit_days / trading_days * 100) if trading_days > 0 else 0,
        'profit_days': profit_days,
        'profit_days_pct': (profit_days / trading_days * 100) if trading_days > 0 else 0,
        'loss_days': loss_days,
        'loss_days_pct': (loss_days / trading_days * 100) if trading_days > 0 else 0,
        'best_day': best_day or 'N/A',
        'best_day_pnl': best_pnl if best_pnl != -float('inf') else 0,
        'worst_day': worst_day or 'N/A',
        'worst_day_pnl': worst_pnl if worst_pnl != float('inf') else 0,
        'daily_avg': (total_pnl / trading_days) if trading_days > 0 else 0
    }

def generate_monthly_breakdown(year):
    """Genera tabla con breakdown mensual"""
    monthly_stats = []
    
    for month in range(1, 13):
        month_file = f"exports/monthly/{year}-{month:02d}.json"
        if os.path.exists(month_file):
            data = load_json_file(month_file)
            if data:
                monthly_stats.append({
                    'month': data['monthName'],
                    'trades': data['overview']['totalTrades'],
                    'pnl': data['overview']['netPnL'],
                    'winRate': data['overview']['winRate'] * 100
                })
    
    if not monthly_stats:
        return ""
    
    markdown = "\n### 📈 Monthly Breakdown\n\n"
    markdown += "| Month | Trades | P&L | Win Rate |\n"
    markdown += "|-------|--------|-----|----------|\n"
    
    for stats in monthly_stats:
        pnl_formatted = f"${stats['pnl']:+,.2f}" if stats['pnl'] != 0 else "$0.00"
        markdown += f"| {stats['month']} | {stats['trades']} | **{pnl_formatted}** | {stats['winRate']:.1f}% |\n"
    
    return markdown

def update_readme_with_calendar(calendar_content):
    """Actualiza el README con el calendario"""
    readme_path = "README.md"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar marcadores para calendario
    start_marker = "<!-- CALENDAR_START -->"
    end_marker = "<!-- CALENDAR_END -->"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        new_content = (
            content[:start_idx + len(start_marker)] + 
            "\n" + calendar_content + "\n" +
            content[end_idx:]
        )
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ README actualizado con calendario")
        return True
    else:
        print("⚠️  No se encontraron marcadores CALENDAR en el README")
        return False

if __name__ == "__main__":
    year = datetime.now().year
    
    # Generar calendario y estadísticas
    calendar_md, stats = generate_markdown_calendar(year)
    
    # Agregar breakdown mensual
    monthly_breakdown = generate_monthly_breakdown(year)
    full_content = calendar_md + monthly_breakdown
    
    print(full_content)
    
    # Actualizar README
    update_readme_with_calendar(full_content)