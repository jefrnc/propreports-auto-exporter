#!/usr/bin/env python3
"""
Generador de dashboard HTML para GitHub Pages
"""

import os
import json
from datetime import datetime, timedelta
from generate_calendar import get_year_data, calculate_year_stats

def generate_html_dashboard():
    """Genera un dashboard HTML completo con gráficos interactivos"""
    year = datetime.now().year
    year_data = get_year_data(year)
    stats = calculate_year_stats(year_data)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Dashboard - PropReports Auto-Exporter</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/cal-heatmap@4.2.4/dist/cal-heatmap.min.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/cal-heatmap@4.2.4/dist/cal-heatmap.css">
    <style>
        .profit { color: #10b981; }
        .loss { color: #ef4444; }
        .cal-heatmap-container { display: flex; justify-content: center; }
    </style>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <header class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-800 mb-2">Trading Dashboard</h1>
            <p class="text-gray-600">PropReports Auto-Exporter Analytics</p>
        </header>
        
        <!-- Key Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-500">Total P&L</h3>
                <p class="text-2xl font-bold mt-2 """ + ('profit' if stats['total_pnl'] >= 0 else 'loss') + f"""">
                    ${stats['total_pnl']:,.2f}
                </p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-500">Total Trades</h3>
                <p class="text-2xl font-bold mt-2 text-gray-800">{stats['total_trades']:,}</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-500">Win Rate</h3>
                <p class="text-2xl font-bold mt-2 text-gray-800">{stats['win_rate']:.1f}%</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-500">Daily Average</h3>
                <p class="text-2xl font-bold mt-2 """ + ('profit' if stats['daily_avg'] >= 0 else 'loss') + f"""">
                    ${stats['daily_avg']:.2f}
                </p>
            </div>
        </div>
        
        <!-- Calendar Heatmap -->
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Trading Calendar {year}</h2>
            <div id="calendar" class="cal-heatmap-container"></div>
        </div>
        
        <!-- Charts -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">Daily P&L</h2>
                <canvas id="dailyPnlChart"></canvas>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-bold text-gray-800 mb-4">Cumulative P&L</h2>
                <canvas id="cumulativePnlChart"></canvas>
            </div>
        </div>
        
        <!-- Monthly Breakdown -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">Monthly Performance</h2>
            <canvas id="monthlyChart"></canvas>
        </div>
    </div>
    
    <script>
        // Data preparation
        const yearData = """ + json.dumps(year_data) + """;
        
        // Calendar Heatmap
        const cal = new CalHeatmap();
        const calData = {};
        
        Object.entries(yearData).forEach(([date, data]) => {
            const timestamp = new Date(date).getTime() / 1000;
            calData[timestamp] = data.pnl;
        });
        
        cal.init({
            domain: 'month',
            subDomain: 'day',
            data: calData,
            start: new Date(""" + str(year) + """, 0, 1),
            cellSize: 15,
            range: 12,
            legend: [-100, -50, 0, 50, 100],
            legendColors: {
                min: "#ef4444",
                max: "#10b981",
                empty: "#e5e7eb"
            },
            itemName: ["trade", "trades"],
            subDomainTextFormat: "%d",
            displayLegend: true,
            tooltip: true,
            onClick: function(date, value) {
                const dateStr = new Date(date).toISOString().split('T')[0];
                const data = yearData[dateStr];
                if (data) {
                    alert(`${dateStr}\\nTrades: ${data.trades}\\nP&L: $${data.pnl.toFixed(2)}`);
                }
            }
        });
        
        // Daily P&L Chart
        const dailyDates = Object.keys(yearData).filter(date => yearData[date].trades > 0);
        const dailyPnl = dailyDates.map(date => yearData[date].pnl);
        
        new Chart(document.getElementById('dailyPnlChart'), {
            type: 'bar',
            data: {
                labels: dailyDates,
                datasets: [{
                    label: 'Daily P&L',
                    data: dailyPnl,
                    backgroundColor: dailyPnl.map(pnl => pnl >= 0 ? '#10b981' : '#ef4444')
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: {
                        title: { display: true, text: 'P&L ($)' }
                    }
                }
            }
        });
        
        // Cumulative P&L Chart
        let cumulative = 0;
        const cumulativePnl = dailyDates.map(date => {
            cumulative += yearData[date].pnl;
            return cumulative;
        });
        
        new Chart(document.getElementById('cumulativePnlChart'), {
            type: 'line',
            data: {
                labels: dailyDates,
                datasets: [{
                    label: 'Cumulative P&L',
                    data: cumulativePnl,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: {
                        title: { display: true, text: 'Cumulative P&L ($)' }
                    }
                }
            }
        });
        
        // Monthly Chart
        const monthlyData = {};
        Object.entries(yearData).forEach(([date, data]) => {
            const month = date.substring(0, 7);
            if (!monthlyData[month]) {
                monthlyData[month] = { trades: 0, pnl: 0 };
            }
            monthlyData[month].trades += data.trades;
            monthlyData[month].pnl += data.pnl;
        });
        
        const months = Object.keys(monthlyData).sort();
        const monthlyPnl = months.map(m => monthlyData[m].pnl);
        const monthlyTrades = months.map(m => monthlyData[m].trades);
        
        new Chart(document.getElementById('monthlyChart'), {
            type: 'bar',
            data: {
                labels: months.map(m => {
                    const [year, month] = m.split('-');
                    return new Date(year, month - 1).toLocaleDateString('en', { month: 'short' });
                }),
                datasets: [{
                    label: 'P&L',
                    data: monthlyPnl,
                    backgroundColor: monthlyPnl.map(pnl => pnl >= 0 ? '#10b981' : '#ef4444'),
                    yAxisID: 'y'
                }, {
                    label: 'Trades',
                    data: monthlyTrades,
                    type: 'line',
                    borderColor: '#6366f1',
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'P&L ($)' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Trades' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
    </script>
    
    <footer class="text-center mt-8 text-gray-600">
        <p>Generated on """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """ UTC</p>
        <p class="mt-2">
            <a href="https://github.com/jefrnc/propreports-auto-exporter" class="text-blue-600 hover:underline">
                PropReports Auto-Exporter
            </a>
        </p>
    </footer>
</body>
</html>"""
    
    # Guardar dashboard
    os.makedirs('docs', exist_ok=True)
    with open('docs/index.html', 'w') as f:
        f.write(html)
    
    print("✅ Dashboard HTML generado en docs/index.html")

if __name__ == "__main__":
    generate_html_dashboard()