#!/usr/bin/env python3
"""
Genera datos JSON para el dashboard de GitHub Pages
"""

import os
import json
from datetime import datetime
from generate_calendar import get_year_data, calculate_year_stats, load_json_file

def calculate_enhanced_metrics(year_data):
    """Calcula métricas adicionales para el dashboard"""
    all_trades = []
    total_gross_profit = 0
    total_gross_loss = 0
    total_fees = 0
    
    # Recopilar todos los trades del año
    for date, day_data in year_data.items():
        daily_file = f"exports/daily/{date}.json"
        if os.path.exists(daily_file):
            daily_data = load_json_file(daily_file)
            if daily_data and 'trades' in daily_data:
                all_trades.extend(daily_data['trades'])
    
    if not all_trades:
        return {
            'profit_factor': 0,
            'biggest_win': 0,
            'biggest_loss': 0,
            'total_fees': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'current_streak': 0,
            'current_streak_type': 'none'
        }
    
    # Ordenar trades por fecha y hora
    all_trades.sort(key=lambda x: (x['date'], x['opened']))
    
    # Calcular métricas
    biggest_win = 0
    biggest_loss = 0
    current_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    last_trade_type = None
    
    for trade in all_trades:
        pnl = trade.get('pnl', 0)
        net = trade.get('net', pnl)
        commission = trade.get('commission', 0)
        
        # Acumular comisiones
        total_fees += commission
        
        # Profit factor calculation
        if pnl > 0:
            total_gross_profit += pnl
        else:
            total_gross_loss += abs(pnl)
        
        # Biggest win/loss
        if net > biggest_win:
            biggest_win = net
        if net < biggest_loss:
            biggest_loss = net
        
        # Streak calculation
        if net > 0:
            if last_trade_type == 'win':
                current_streak += 1
            else:
                current_streak = 1
                last_trade_type = 'win'
            max_win_streak = max(max_win_streak, current_streak)
        elif net < 0:
            if last_trade_type == 'loss':
                current_streak += 1
            else:
                current_streak = 1
                last_trade_type = 'loss'
            max_loss_streak = max(max_loss_streak, current_streak)
    
    # Calculate profit factor
    profit_factor = (total_gross_profit / total_gross_loss) if total_gross_loss > 0 else float('inf') if total_gross_profit > 0 else 0
    
    return {
        'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
        'biggest_win': round(biggest_win, 2),
        'biggest_loss': round(biggest_loss, 2),
        'total_fees': round(total_fees, 2),
        'max_win_streak': max_win_streak,
        'max_loss_streak': max_loss_streak,
        'current_streak': current_streak if last_trade_type else 0,
        'current_streak_type': last_trade_type or 'none'
    }

def generate_dashboard_data():
    """Genera un archivo JSON con todos los datos necesarios para el dashboard"""
    year = datetime.now().year
    
    # Obtener datos del año
    year_data = get_year_data(year)
    stats = calculate_year_stats(year_data)
    
    # Calcular métricas mejoradas
    enhanced_metrics = calculate_enhanced_metrics(year_data)
    
    # Combinar todas las estadísticas
    stats.update(enhanced_metrics)
    
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