#!/usr/bin/env python3
"""
Generador de resúmenes semanales de PropReports
Consolida los datos diarios en un resumen semanal
"""

import os
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict

def get_week_dates(date=None):
    """Obtiene las fechas de inicio y fin de la semana"""
    if date is None:
        date = datetime.now()
    elif isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d')
    
    # Inicio de semana (lunes)
    start_of_week = date - timedelta(days=date.weekday())
    # Fin de semana (domingo)
    end_of_week = start_of_week + timedelta(days=6)
    
    return start_of_week, end_of_week

def load_daily_files(week_start, week_end):
    """Carga todos los archivos diarios de la semana"""
    year = week_start.strftime('%Y')
    month = week_start.strftime('%m')
    
    daily_dir = f"exports/{year}/{month}/daily"
    daily_data = []
    
    # Iterar por cada día de la semana
    current_date = week_start
    while current_date <= week_end:
        date_str = current_date.strftime('%Y-%m-%d')
        file_path = os.path.join(daily_dir, f"{date_str}.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                daily_data.append(data)
        
        current_date += timedelta(days=1)
    
    return daily_data

def analyze_trading_patterns(trades):
    """Analiza patrones de trading"""
    patterns = {
        'by_hour': defaultdict(lambda: {'count': 0, 'pnl': 0}),
        'by_symbol': defaultdict(lambda: {'count': 0, 'pnl': 0, 'win_rate': 0}),
        'by_duration': defaultdict(lambda: {'count': 0, 'pnl': 0}),
        'consecutive_wins': 0,
        'consecutive_losses': 0,
        'max_consecutive_wins': 0,
        'max_consecutive_losses': 0
    }
    
    current_streak = 0
    streak_type = None
    
    for trade in trades:
        # Por hora del día
        if trade.get('opened'):
            try:
                # Manejar diferentes formatos de fecha/hora
                opened = trade['opened']
                if ' ' in opened:
                    time_part = opened.split(' ')[1]
                else:
                    time_part = opened
                
                if ':' in time_part:
                    hour = time_part.split(':')[0]
                    patterns['by_hour'][hour]['count'] += 1
                    patterns['by_hour'][hour]['pnl'] += trade.get('pnl', 0)
            except:
                pass  # Ignorar si no se puede parsear
        
        # Por símbolo
        symbol = trade.get('symbol', 'UNKNOWN')
        patterns['by_symbol'][symbol]['count'] += 1
        patterns['by_symbol'][symbol]['pnl'] += trade.get('pnl', 0)
        
        # Por duración de trade
        if trade.get('held'):
            duration_parts = trade['held'].split(':')
            if len(duration_parts) >= 2:
                minutes = int(duration_parts[0]) * 60 + int(duration_parts[1])
                if minutes < 5:
                    duration_category = '<5min'
                elif minutes < 15:
                    duration_category = '5-15min'
                elif minutes < 60:
                    duration_category = '15-60min'
                else:
                    duration_category = '>60min'
                
                patterns['by_duration'][duration_category]['count'] += 1
                patterns['by_duration'][duration_category]['pnl'] += trade.get('pnl', 0)
        
        # Rachas de wins/losses
        pnl = trade.get('pnl', 0)
        if pnl > 0:
            if streak_type == 'win':
                current_streak += 1
            else:
                current_streak = 1
                streak_type = 'win'
            patterns['max_consecutive_wins'] = max(patterns['max_consecutive_wins'], current_streak)
        elif pnl < 0:
            if streak_type == 'loss':
                current_streak += 1
            else:
                current_streak = 1
                streak_type = 'loss'
            patterns['max_consecutive_losses'] = max(patterns['max_consecutive_losses'], current_streak)
    
    # Calcular win rates por símbolo
    for symbol, data in patterns['by_symbol'].items():
        symbol_trades = [t for t in trades if t.get('symbol') == symbol]
        wins = len([t for t in symbol_trades if t.get('pnl', 0) > 0])
        data['win_rate'] = round(wins / len(symbol_trades), 4) if symbol_trades else 0
    
    return patterns

def generate_weekly_summary(week_date=None):
    """Genera resumen semanal consolidando datos diarios"""
    # Obtener fechas de la semana
    week_start, week_end = get_week_dates(week_date)
    week_str = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"
    
    print(f"📅 Generando resumen semanal: {week_str}")
    
    # Cargar archivos diarios
    daily_data = load_daily_files(week_start, week_end)
    
    if not daily_data:
        print("⚠️  No hay datos para esta semana")
        return None
    
    # Consolidar todos los trades
    all_trades = []
    daily_summaries = []
    
    for day_data in daily_data:
        all_trades.extend(day_data.get('trades', []))
        daily_summaries.append({
            'date': day_data.get('date'),
            'trades': day_data.get('summary', {}).get('totalTrades', 0),
            'pnl': day_data.get('summary', {}).get('netPnL', 0),
            'symbols': day_data.get('summary', {}).get('symbols', [])
        })
    
    # Calcular estadísticas semanales
    total_pnl = sum(t.get('pnl', 0) for t in all_trades)
    total_commissions = sum(t.get('commission', 0) for t in all_trades)
    winning_trades = [t for t in all_trades if t.get('pnl', 0) > 0]
    losing_trades = [t for t in all_trades if t.get('pnl', 0) < 0]
    
    # Mejores y peores trades
    best_trade = max(all_trades, key=lambda x: x.get('pnl', 0)) if all_trades else None
    worst_trade = min(all_trades, key=lambda x: x.get('pnl', 0)) if all_trades else None
    
    # Días más rentables
    best_day = max(daily_summaries, key=lambda x: x['pnl']) if daily_summaries else None
    worst_day = min(daily_summaries, key=lambda x: x['pnl']) if daily_summaries else None
    
    # Analizar patrones
    patterns = analyze_trading_patterns(all_trades)
    
    # Estructura del resumen semanal
    weekly_summary = {
        'generateDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'weekPeriod': week_str,
        'weekNumber': week_start.isocalendar()[1],
        'year': week_start.year,
        'account': daily_data[0].get('account') if daily_data else 'UNKNOWN',
        'summary': {
            'totalTradingDays': len(daily_data),
            'totalTrades': len(all_trades),
            'grossPnL': round(total_pnl, 2),
            'totalCommissions': round(total_commissions, 2),
            'netPnL': round(total_pnl - total_commissions, 2),
            'avgDailyPnL': round((total_pnl - total_commissions) / len(daily_data), 2) if daily_data else 0,
            'avgTradePerDay': round(len(all_trades) / len(daily_data), 2) if daily_data else 0,
            'winningTrades': len(winning_trades),
            'losingTrades': len(losing_trades),
            'winRate': round(len(winning_trades) / len(all_trades), 4) if all_trades else 0,
            'avgWin': round(sum(t['pnl'] for t in winning_trades) / len(winning_trades), 2) if winning_trades else 0,
            'avgLoss': round(sum(t['pnl'] for t in losing_trades) / len(losing_trades), 2) if losing_trades else 0,
            'profitFactor': round(abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)), 2) if losing_trades and sum(t['pnl'] for t in losing_trades) != 0 else 0
        },
        'extremes': {
            'bestTrade': {
                'date': best_trade.get('date', ''),
                'symbol': best_trade.get('symbol', ''),
                'pnl': best_trade.get('pnl', 0)
            } if best_trade else None,
            'worstTrade': {
                'date': worst_trade.get('date', ''),
                'symbol': worst_trade.get('symbol', ''),
                'pnl': worst_trade.get('pnl', 0)
            } if worst_trade else None,
            'bestDay': best_day,
            'worstDay': worst_day
        },
        'patterns': {
            'maxConsecutiveWins': patterns['max_consecutive_wins'],
            'maxConsecutiveLosses': patterns['max_consecutive_losses'],
            'topSymbols': sorted(
                [(symbol, data) for symbol, data in patterns['by_symbol'].items()],
                key=lambda x: x[1]['pnl'],
                reverse=True
            )[:5],
            'tradingHours': dict(patterns['by_hour']),
            'tradeDurations': dict(patterns['by_duration'])
        },
        'dailyBreakdown': daily_summaries
    }
    
    # Guardar resumen semanal
    year = week_start.strftime('%Y')
    month = week_start.strftime('%m')
    weekly_dir = f"exports/{year}/{month}/weekly"
    os.makedirs(weekly_dir, exist_ok=True)
    
    # Nombre del archivo: week_XX.json
    week_num = week_start.isocalendar()[1]
    filename = os.path.join(weekly_dir, f"week_{week_num:02d}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(weekly_summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Resumen semanal generado: {filename}")
    print(f"📊 Resumen: {weekly_summary['summary']['totalTrades']} trades, "
          f"P&L neto: ${weekly_summary['summary']['netPnL']}, "
          f"Win rate: {weekly_summary['summary']['winRate']*100:.1f}%")
    
    return filename

if __name__ == "__main__":
    # Generar resumen de la semana actual
    generate_weekly_summary()