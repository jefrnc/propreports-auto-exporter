#!/usr/bin/env python3
"""
Genera datos JSON para cada mes individual
"""

import os
import json
from datetime import datetime

def load_json_file(filepath):
    """Carga un archivo JSON de forma segura"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error cargando {filepath}: {e}")
        return None

def generate_monthly_data():
    """Genera archivos JSON para cada mes con datos detallados"""
    year = datetime.now().year
    
    # Crear directorio para datos mensuales
    os.makedirs('docs/data/monthly', exist_ok=True)
    
    # Procesar cada mes
    for month in range(1, 13):
        month_trades = []
        month_data = {
            'month': month,
            'year': year,
            'trades': [],
            'dailyData': {},
            'summary': {
                'totalTrades': 0,
                'totalPnL': 0,
                'winRate': 0,
                'bestDay': None,
                'bestDayPnL': -float('inf'),
                'worstDay': None,
                'worstDayPnL': float('inf'),
                'tradingDays': 0
            }
        }
        
        # Recopilar todos los trades del mes
        for day in range(1, 32):
            try:
                date_str = f"{year}-{month:02d}-{day:02d}"
                daily_file = f"exports/daily/{date_str}.json"
                
                if os.path.exists(daily_file):
                    daily_data = load_json_file(daily_file)
                    if daily_data and daily_data.get('trades'):
                        # Guardar datos diarios
                        month_data['dailyData'][date_str] = {
                            'trades': len(daily_data['trades']),
                            'pnl': daily_data['summary']['netPnL'],
                            'winRate': daily_data['summary'].get('winRate', 0)
                        }
                        
                        # Agregar trades
                        month_trades.extend(daily_data['trades'])
                        
                        # Actualizar resumen
                        month_data['summary']['totalTrades'] += len(daily_data['trades'])
                        month_data['summary']['totalPnL'] += daily_data['summary']['netPnL']
                        month_data['summary']['tradingDays'] += 1
                        
                        # Best/worst day
                        if daily_data['summary']['netPnL'] > month_data['summary']['bestDayPnL']:
                            month_data['summary']['bestDayPnL'] = daily_data['summary']['netPnL']
                            month_data['summary']['bestDay'] = date_str
                        
                        if daily_data['summary']['netPnL'] < month_data['summary']['worstDayPnL']:
                            month_data['summary']['worstDayPnL'] = daily_data['summary']['netPnL']
                            month_data['summary']['worstDay'] = date_str
            except:
                continue
        
        # Calcular win rate
        if month_trades:
            winning_trades = [t for t in month_trades if (t.get('net', t.get('pnl', 0))) > 0]
            month_data['summary']['winRate'] = len(winning_trades) / len(month_trades) * 100
            
            # Ordenar trades por P&L
            sorted_trades = sorted(month_trades, key=lambda x: x.get('net', x.get('pnl', 0)), reverse=True)
            
            # Top 5 winners y losers
            month_data['topWinners'] = sorted_trades[:5] if len(sorted_trades) >= 5 else sorted_trades[:len([t for t in sorted_trades if t.get('net', t.get('pnl', 0)) > 0])]
            month_data['topLosers'] = sorted([t for t in sorted_trades if t.get('net', t.get('pnl', 0)) < 0], key=lambda x: x.get('net', x.get('pnl', 0)))[:5]
        
        # Guardar archivo del mes
        month_file = f"docs/data/monthly/{year}-{month:02d}.json"
        with open(month_file, 'w') as f:
            json.dump(month_data, f, indent=2)
        
        print(f"✅ Datos generados para {year}-{month:02d}")

if __name__ == "__main__":
    generate_monthly_data()