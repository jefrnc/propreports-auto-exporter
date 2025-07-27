#!/usr/bin/env python3
"""
Generador de resúmenes mensuales de PropReports
Consolida todos los datos del mes para análisis profundo
"""

import os
import json
import calendar
from datetime import datetime, timedelta
from collections import defaultdict
import glob

def load_weekly_summaries(year, month):
    """Carga todos los resúmenes semanales del mes"""
    base_dir = os.getenv('EXPORT_OUTPUT_DIR', 'exports')
    weekly_dir = os.path.join(base_dir, "weekly")
    
    # Buscar archivos semanales del mes específico
    weekly_files = []
    for week in range(1, 54):  # Posibles semanas del año
        filename = os.path.join(weekly_dir, f"{year}-W{week:02d}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Verificar si la semana pertenece al mes
                week_period = data.get('weekPeriod', '')
                if f"{year}-{month:02d}" in week_period:
                    weekly_files.append(data)
    
    return weekly_files

def load_all_daily_files(year, month):
    """Carga todos los archivos diarios del mes"""
    base_dir = os.getenv('EXPORT_OUTPUT_DIR', 'exports')
    daily_dir = os.path.join(base_dir, "daily")
    
    all_trades = []
    daily_summaries = []
    
    # Obtener primer y último día del mes
    first_day = 1
    last_day = calendar.monthrange(year, month)[1]
    
    for day in range(first_day, last_day + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        file_path = os.path.join(daily_dir, f"{date_str}.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_trades.extend(data.get('trades', []))
                daily_summaries.append({
                    'date': data.get('date'),
                    'trades': data.get('summary', {}).get('totalTrades', 0),
                    'pnl': data.get('summary', {}).get('netPnL', 0)
                })
    
    return all_trades, daily_summaries

def analyze_monthly_performance(trades, daily_summaries):
    """Análisis profundo del desempeño mensual"""
    analysis = {
        'profitability_curve': [],
        'drawdown_analysis': {},
        'consistency_metrics': {},
        'symbol_performance': defaultdict(lambda: {
            'trades': 0, 'pnl': 0, 'wins': 0, 'losses': 0,
            'avg_win': 0, 'avg_loss': 0, 'win_rate': 0
        }),
        'time_analysis': defaultdict(lambda: {'trades': 0, 'pnl': 0}),
        'risk_metrics': {}
    }
    
    # Curva de rentabilidad acumulada
    cumulative_pnl = 0
    peak_pnl = 0
    max_drawdown = 0
    drawdowns = []
    
    for day in sorted(daily_summaries, key=lambda x: x['date']):
        cumulative_pnl += day['pnl']
        analysis['profitability_curve'].append({
            'date': day['date'],
            'daily_pnl': day['pnl'],
            'cumulative_pnl': round(cumulative_pnl, 2)
        })
        
        # Calcular drawdown
        if cumulative_pnl > peak_pnl:
            peak_pnl = cumulative_pnl
        else:
            current_drawdown = peak_pnl - cumulative_pnl
            if current_drawdown > max_drawdown:
                max_drawdown = current_drawdown
    
    analysis['drawdown_analysis'] = {
        'max_drawdown': round(max_drawdown, 2),
        'max_drawdown_percent': round((max_drawdown / peak_pnl * 100), 2) if peak_pnl > 0 else 0
    }
    
    # Análisis por símbolo
    symbol_trades = defaultdict(list)
    for trade in trades:
        symbol = trade.get('symbol', 'UNKNOWN')
        symbol_trades[symbol].append(trade)
    
    for symbol, trades_list in symbol_trades.items():
        wins = [t for t in trades_list if t.get('pnl', 0) > 0]
        losses = [t for t in trades_list if t.get('pnl', 0) < 0]
        
        analysis['symbol_performance'][symbol] = {
            'trades': len(trades_list),
            'pnl': round(sum(t.get('pnl', 0) for t in trades_list), 2),
            'wins': len(wins),
            'losses': len(losses),
            'avg_win': round(sum(t['pnl'] for t in wins) / len(wins), 2) if wins else 0,
            'avg_loss': round(sum(t['pnl'] for t in losses) / len(losses), 2) if losses else 0,
            'win_rate': round(len(wins) / len(trades_list), 4) if trades_list else 0,
            'expectancy': round((len(wins) / len(trades_list) * (sum(t['pnl'] for t in wins) / len(wins)) + 
                                len(losses) / len(trades_list) * (sum(t['pnl'] for t in losses) / len(losses))), 2) if trades_list and wins and losses else 0
        }
    
    # Métricas de consistencia
    profitable_days = len([d for d in daily_summaries if d['pnl'] > 0])
    losing_days = len([d for d in daily_summaries if d['pnl'] < 0])
    
    analysis['consistency_metrics'] = {
        'profitable_days': profitable_days,
        'losing_days': losing_days,
        'win_rate_days': round(profitable_days / len(daily_summaries), 4) if daily_summaries else 0,
        'avg_winning_day': round(sum(d['pnl'] for d in daily_summaries if d['pnl'] > 0) / profitable_days, 2) if profitable_days else 0,
        'avg_losing_day': round(sum(d['pnl'] for d in daily_summaries if d['pnl'] < 0) / losing_days, 2) if losing_days else 0
    }
    
    # Métricas de riesgo
    all_pnls = [t.get('pnl', 0) for t in trades]
    if all_pnls:
        analysis['risk_metrics'] = {
            'sharpe_ratio': calculate_sharpe_ratio(all_pnls),
            'max_consecutive_losses': calculate_max_consecutive_losses(trades),
            'risk_reward_ratio': abs(analysis['consistency_metrics']['avg_winning_day'] / 
                                   analysis['consistency_metrics']['avg_losing_day']) if analysis['consistency_metrics']['avg_losing_day'] != 0 else 0
        }
    
    return analysis

def calculate_sharpe_ratio(returns, risk_free_rate=0):
    """Calcula el Sharpe Ratio"""
    if not returns or len(returns) < 2:
        return 0
    
    try:
        import numpy as np
        returns_array = np.array(returns)
        avg_return = np.mean(returns_array)
        std_dev = np.std(returns_array)
        
        if std_dev == 0:
            return 0
        
        sharpe = (avg_return - risk_free_rate) / std_dev
        return round(sharpe * np.sqrt(252), 2)  # Anualizado
    except ImportError:
        # Si no está numpy, calcular manualmente
        avg_return = sum(returns) / len(returns)
        variance = sum((x - avg_return) ** 2 for x in returns) / len(returns)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return 0
        
        sharpe = (avg_return - risk_free_rate) / std_dev
        return round(sharpe * (252 ** 0.5), 2)  # Anualizado

def calculate_max_consecutive_losses(trades):
    """Calcula la máxima racha de pérdidas consecutivas"""
    max_losses = 0
    current_losses = 0
    
    for trade in trades:
        if trade.get('pnl', 0) < 0:
            current_losses += 1
            max_losses = max(max_losses, current_losses)
        else:
            current_losses = 0
    
    return max_losses

def generate_monthly_summary(year=None, month=None):
    """Genera resumen mensual completo"""
    # Si no se especifica, usar el mes actual
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    month_name = calendar.month_name[month]
    print(f"📅 Generando resumen mensual: {month_name} {year}")
    
    # Cargar resúmenes semanales
    weekly_summaries = load_weekly_summaries(year, month)
    
    # Cargar todos los trades diarios
    all_trades, daily_summaries = load_all_daily_files(year, month)
    
    if not all_trades:
        print("⚠️  No hay datos para este mes")
        return None
    
    # Análisis profundo
    performance_analysis = analyze_monthly_performance(all_trades, daily_summaries)
    
    # Calcular totales del mes
    total_pnl = sum(t.get('pnl', 0) for t in all_trades)
    total_commissions = sum(t.get('commission', 0) for t in all_trades)
    winning_trades = [t for t in all_trades if t.get('pnl', 0) > 0]
    losing_trades = [t for t in all_trades if t.get('pnl', 0) < 0]
    
    # Estructura del resumen mensual
    monthly_summary = {
        'generateDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'month': month,
        'monthName': month_name,
        'year': year,
        'account': all_trades[0].get('account', 'UNKNOWN') if all_trades else 'UNKNOWN',
        'overview': {
            'totalTradingDays': len(daily_summaries),
            'totalTrades': len(all_trades),
            'grossPnL': round(total_pnl, 2),
            'totalCommissions': round(total_commissions, 2),
            'netPnL': round(total_pnl - total_commissions, 2),
            'avgDailyPnL': round((total_pnl - total_commissions) / len(daily_summaries), 2) if daily_summaries else 0,
            'winningTrades': len(winning_trades),
            'losingTrades': len(losing_trades),
            'winRate': round(len(winning_trades) / len(all_trades), 4) if all_trades else 0,
            'avgWin': round(sum(t['pnl'] for t in winning_trades) / len(winning_trades), 2) if winning_trades else 0,
            'avgLoss': round(sum(t['pnl'] for t in losing_trades) / len(losing_trades), 2) if losing_trades else 0,
            'profitFactor': round(abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)), 2) if losing_trades and sum(t['pnl'] for t in losing_trades) != 0 else 0,
            'expectancy': round((len(winning_trades) / len(all_trades) * (sum(t['pnl'] for t in winning_trades) / len(winning_trades)) + 
                                len(losing_trades) / len(all_trades) * (sum(t['pnl'] for t in losing_trades) / len(losing_trades))), 2) if all_trades and winning_trades and losing_trades else 0
        },
        'performanceAnalysis': performance_analysis,
        'weeklyBreakdown': [
            {
                'week': ws.get('weekNumber'),
                'period': ws.get('weekPeriod'),
                'trades': ws.get('summary', {}).get('totalTrades', 0),
                'netPnL': ws.get('summary', {}).get('netPnL', 0),
                'winRate': ws.get('summary', {}).get('winRate', 0)
            } for ws in weekly_summaries
        ],
        'recommendations': []  # Se llenarán después
    }
    
    # Generar recomendaciones
    monthly_summary['recommendations'] = generate_recommendations(performance_analysis, monthly_summary)
    
    # Guardar resumen mensual
    base_dir = os.getenv('EXPORT_OUTPUT_DIR', 'exports')
    monthly_dir = os.path.join(base_dir, "monthly")
    os.makedirs(monthly_dir, exist_ok=True)
    
    filename = os.path.join(monthly_dir, f"{year}-{month:02d}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(monthly_summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Resumen mensual generado: {filename}")
    print(f"📊 Resumen del mes: {monthly_summary['overview']['totalTrades']} trades, "
          f"P&L neto: ${monthly_summary['overview']['netPnL']}, "
          f"Win rate: {monthly_summary['overview']['winRate']*100:.1f}%")
    print(f"📉 Max Drawdown: ${performance_analysis['drawdown_analysis']['max_drawdown']} "
          f"({performance_analysis['drawdown_analysis']['max_drawdown_percent']:.1f}%)")
    
    # Generar reporte en texto plano también
    generate_text_report(monthly_summary, filename.replace('.json', '.txt'))
    
    return filename

def generate_recommendations(analysis, summary):
    """Genera recomendaciones basadas en el análisis"""
    recommendations = []
    
    # Análisis de win rate
    win_rate = summary['overview']['winRate']
    if win_rate < 0.5:
        recommendations.append({
            'type': 'warning',
            'area': 'Win Rate',
            'message': f'Win rate bajo ({win_rate*100:.1f}%). Considerar revisar estrategia de entrada.'
        })
    
    # Análisis de drawdown
    max_dd = analysis['drawdown_analysis']['max_drawdown_percent']
    if max_dd > 10:
        recommendations.append({
            'type': 'critical',
            'area': 'Risk Management',
            'message': f'Drawdown elevado ({max_dd:.1f}%). Implementar stops más ajustados.'
        })
    
    # Análisis de símbolos
    top_losers = sorted(
        [(s, d) for s, d in analysis['symbol_performance'].items() if d['pnl'] < 0],
        key=lambda x: x[1]['pnl']
    )[:3]
    
    if top_losers:
        symbols_str = ', '.join([s for s, _ in top_losers])
        recommendations.append({
            'type': 'suggestion',
            'area': 'Symbol Selection',
            'message': f'Revisar estrategia para: {symbols_str} (pérdidas consistentes)'
        })
    
    # Análisis de consistencia
    consistency = analysis['consistency_metrics']['win_rate_days']
    if consistency < 0.5:
        recommendations.append({
            'type': 'warning',
            'area': 'Consistency',
            'message': f'Solo {consistency*100:.1f}% de días rentables. Buscar mayor consistencia.'
        })
    
    return recommendations

def generate_text_report(summary, filename):
    """Genera un reporte en texto plano para fácil lectura"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"RESUMEN MENSUAL DE TRADING\n")
        f.write(f"{summary['monthName']} {summary['year']}\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("RESUMEN GENERAL:\n")
        f.write(f"  Total de trades: {summary['overview']['totalTrades']}\n")
        f.write(f"  P&L Neto: ${summary['overview']['netPnL']}\n")
        f.write(f"  Win Rate: {summary['overview']['winRate']*100:.1f}%\n")
        f.write(f"  Profit Factor: {summary['overview']['profitFactor']}\n")
        f.write(f"  Expectancy: ${summary['overview']['expectancy']}\n")
        f.write("\n")
        
        f.write("DESGLOSE SEMANAL:\n")
        for week in summary['weeklyBreakdown']:
            f.write(f"  Semana {week['week']}: {week['trades']} trades, ${week['netPnL']}, WR: {week['winRate']*100:.1f}%\n")
        f.write("\n")
        
        f.write("RECOMENDACIONES:\n")
        for rec in summary['recommendations']:
            emoji = {"critical": "🔴", "warning": "🟡", "suggestion": "🔵"}.get(rec['type'], "⚪")
            f.write(f"  {emoji} [{rec['area']}] {rec['message']}\n")
    
    print(f"📝 Reporte de texto generado: {filename}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 3:
        # Si se pasan año y mes como argumentos
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        generate_monthly_summary(year, month)
    else:
        # Por defecto, generar del mes anterior
        today = datetime.now()
        if today.day <= 5:  # Si estamos en los primeros días del mes
            # Generar resumen del mes anterior
            if today.month == 1:
                generate_monthly_summary(today.year - 1, 12)
            else:
                generate_monthly_summary(today.year, today.month - 1)
        else:
            # Generar resumen del mes actual
            generate_monthly_summary()