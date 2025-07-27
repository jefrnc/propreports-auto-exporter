#!/usr/bin/env python3
"""
Genera datos JSON para el dashboard de GitHub Pages
"""

import os
import json
from datetime import datetime
from generate_calendar import get_year_data, calculate_year_stats, load_json_file

def generate_dashboard_data():
    """Genera un archivo JSON con todos los datos necesarios para el dashboard"""
    year = datetime.now().year
    
    # Obtener datos del año
    year_data = get_year_data(year)
    stats = calculate_year_stats(year_data)
    
    # Cargar resúmenes mensuales
    monthly_data = []
    for month in range(1, 13):
        month_file = f"exports/monthly/{year}-{month:02d}.json"
        if os.path.exists(month_file):
            data = load_json_file(month_file)
            if data:
                monthly_data.append({
                    'month': month,
                    'monthName': data['monthName'],
                    'trades': data['overview']['totalTrades'],
                    'pnl': data['overview']['netPnL'],
                    'winRate': data['overview']['winRate']
                })
    
    # Cargar resúmenes semanales
    weekly_data = []
    for week in range(1, 54):
        week_file = f"exports/weekly/{year}-W{week:02d}.json"
        if os.path.exists(week_file):
            data = load_json_file(week_file)
            if data:
                weekly_data.append({
                    'week': week,
                    'period': data['weekPeriod'],
                    'trades': data['summary']['totalTrades'],
                    'pnl': data['summary']['netPnL'],
                    'winRate': data['summary']['winRate']
                })
    
    # Crear objeto de datos completo
    dashboard_data = {
        'lastUpdate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'year': year,
        'yearData': year_data,
        'yearStats': stats,
        'monthlyData': monthly_data,
        'weeklyData': weekly_data
    }
    
    # Guardar en docs para GitHub Pages
    os.makedirs('docs', exist_ok=True)
    with open('docs/dashboard-data.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print("✅ Dashboard data generado en docs/dashboard-data.json")

if __name__ == "__main__":
    generate_dashboard_data()