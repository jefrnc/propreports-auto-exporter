#!/usr/bin/env python3
"""
PropReports Trade Exporter
Extrae datos de trading de PropReports y los exporta en formato JSON
"""

import requests
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional
import time

class PropReportsExporter:
    def __init__(self, domain: str, username: str, password: str):
        self.domain = domain
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = f"https://{domain}"
        
    def login(self) -> bool:
        """Autentica con PropReports"""
        login_url = f"{self.base_url}/login.php"
        
        # Headers para simular navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': self.base_url,
            'Referer': login_url
        }
        
        # Datos de login
        login_data = {
            'user': self.username,
            'password': self.password
        }
        
        try:
            # Realizar login
            response = self.session.post(
                login_url, 
                data=login_data, 
                headers=headers,
                allow_redirects=False
            )
            
            # Verificar si el login fue exitoso
            if response.status_code == 302:  # Redirección exitosa
                print(f"✅ Login exitoso para {self.username}")
                return True
            else:
                print(f"❌ Error en login: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def get_trades_page(self, date_from: str, date_to: str) -> Optional[str]:
        """Obtiene la página de trades para un rango de fechas"""
        # URL correcta para reportes en PropReports
        trades_url = f"{self.base_url}/report.php"
        
        # Parámetros correctos según el formulario encontrado
        params = {
            'reportName': 'trades',  # Tipo de reporte: trades
            'startDate': date_from,
            'endDate': date_to,
            'groupId': '-4',  # Todas las cuentas
            'accountId': '10371',  # ID de cuenta (podría necesitar ajuste)
            'baseCurrency': 'USD',
            'mode': '1'  # Modo estándar
        }
        
        try:
            response = self.session.get(trades_url, params=params)
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ Error al obtener trades: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error al obtener trades: {e}")
            return None
    
    def parse_trades_html(self, html_content: str) -> List[Dict]:
        """Parsea el HTML de trades y extrae los datos"""
        soup = BeautifulSoup(html_content, 'html.parser')
        trades = []
        
        # PropReports usa tablas con class="report"
        trades_table = soup.find('table', {'class': 'report'})
        
        if not trades_table:
            print("⚠️  No se encontró tabla de trades")
            return trades
        
        current_date = None
        
        # Procesar todas las filas de la tabla
        for row in trades_table.find_all('tr'):
            # Detectar separadores de fecha
            if 'sectionSeparator' in row.get('class', []):
                date_cell = row.find('td')
                if date_cell:
                    # Extraer fecha (ej: "Mon, Jul 21, 2025")
                    date_text = date_cell.text.strip()
                    # Convertir a formato YYYY-MM-DD
                    try:
                        date_obj = datetime.strptime(date_text, '%a, %b %d, %Y')
                        current_date = date_obj.strftime('%Y-%m-%d')
                    except:
                        current_date = date_text
                continue
            
            # Detectar filas de encabezado
            if 'summary' in row.get('class', []):
                continue
            
            # Procesar filas de datos (trades)
            cells = row.find_all('td')
            
            # Las filas de trades tienen mínimo 10 columnas
            if len(cells) >= 10 and current_date:
                try:
                    # Estructura típica de PropReports trades:
                    # Opened | Closed | Held | Symbol | Type | Entry | Exit | Size | P&L | Comm | Net | Account
                    
                    # Parse individual fields
                    pnl = self._parse_number(cells[8].text)
                    commission = self._parse_number(cells[9].text) if len(cells) > 9 else 0
                    
                    # PropReports provides net P&L in cell[17]
                    net = self._parse_number(cells[17].text) if len(cells) > 17 else (pnl - commission)
                    
                    trade = {
                        'date': current_date,
                        'opened': cells[0].text.strip(),
                        'closed': cells[1].text.strip(),
                        'held': cells[2].text.strip(),
                        'symbol': cells[3].text.strip(),
                        'type': cells[4].text.strip(),  # Long/Short
                        'entry': self._parse_number(cells[5].text),
                        'exit': self._parse_number(cells[6].text),
                        'size': self._parse_number(cells[7].text),
                        'pnl': pnl,
                        'commission': commission,
                        'net': net,  # Use provided net or calculate
                        'account': self.username  # Account not in HTML
                    }
                    
                    # Determinar side basado en type
                    trade['side'] = 'BUY' if trade['type'].lower() == 'long' else 'SELL'
                    trade['quantity'] = abs(trade['size'])
                    trade['price'] = trade['entry']
                    
                    # Validar que es un trade real y no una fila de subtotal/header
                    # Los trades reales tienen tiempos en 'opened' (ej: "09:30:15")
                    # Las filas de subtotales tienen "Equities" u otros textos
                    is_valid_trade = (
                        trade['symbol'] and 
                        trade['symbol'] not in ['', 'Total:', 'Totals:'] and
                        ':' in trade['opened'] and  # El campo opened debe tener formato de hora
                        trade['type'] in ['Long', 'Short', 'long', 'short']  # Type debe ser Long/Short
                    )
                    
                    if is_valid_trade:
                        trades.append(trade)
                        
                except Exception as e:
                    # Ignorar filas que no son trades (totales, etc.)
                    pass
        
        print(f"  📊 Encontrados {len(trades)} trades válidos")
        return trades
    
    def _parse_number(self, text: str) -> float:
        """Convierte texto a número, maneja formatos con comas y paréntesis"""
        # Limpiar texto
        text = text.strip().replace(',', '').replace('$', '')
        
        # Manejar números negativos en paréntesis
        if text.startswith('(') and text.endswith(')'):
            text = '-' + text[1:-1]
        
        try:
            return float(text)
        except:
            return 0.0
    
    def export_to_json(self, trades: List[Dict], output_dir: str = "exports") -> str:
        """Exporta los trades a formato JSON"""
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Agrupar trades por día
        trades_by_day = {}
        for trade in trades:
            date = trade.get('date', 'unknown')
            if date not in trades_by_day:
                trades_by_day[date] = []
            trades_by_day[date].append(trade)
        
        # Calcular estadísticas
        total_trades = len(trades)
        total_pnl = sum(trade.get('pnl', 0) for trade in trades)
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        # Estructura de datos para exportar
        export_data = {
            'exportDate': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'account': self.username,
            'dateRange': {
                'from': min(trades, key=lambda x: x['date'])['date'] if trades else '',
                'to': max(trades, key=lambda x: x['date'])['date'] if trades else ''
            },
            'summary': {
                'totalTrades': total_trades,
                'totalPnL': round(total_pnl, 2),
                'winningTrades': len(winning_trades),
                'losingTrades': len(losing_trades),
                'winRate': round(len(winning_trades) / total_trades, 4) if total_trades > 0 else 0,
                'avgWin': round(sum(t['pnl'] for t in winning_trades) / len(winning_trades), 2) if winning_trades else 0,
                'avgLoss': round(sum(t['pnl'] for t in losing_trades) / len(losing_trades), 2) if losing_trades else 0
            },
            'dailyData': [
                {
                    'date': date,
                    'trades': day_trades,
                    'dailySummary': {
                        'totalTrades': len(day_trades),
                        'grossPnL': round(sum(t.get('pnl', 0) for t in day_trades), 2),
                        'commissions': round(sum(t.get('commission', 0) for t in day_trades), 2),
                        'netPnL': round(sum(t.get('pnl', 0) - t.get('commission', 0) for t in day_trades), 2)
                    }
                }
                for date, day_trades in sorted(trades_by_day.items())
            ]
        }
        
        # Nombre del archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/propreports_{self.username}_{timestamp}.json"
        
        # Guardar JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Datos exportados a: {filename}")
        return filename
    
    def export_trades(self, days_back: int = 7) -> Optional[str]:
        """Proceso principal de exportación"""
        # Login
        if not self.login():
            return None
        
        # Calcular rango de fechas
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        print(f"📅 Extrayendo trades desde {date_from} hasta {date_to}")
        
        # Obtener página de trades
        html_content = self.get_trades_page(date_from, date_to)
        if not html_content:
            return None
        
        # Parsear trades
        trades = self.parse_trades_html(html_content)
        print(f"📊 Encontrados {len(trades)} trades")
        
        if not trades:
            print("⚠️  No se encontraron trades en el período")
            return None
        
        # Exportar a JSON
        return self.export_to_json(trades)


def main():
    """Función principal"""
    # Configuración desde variables de entorno
    DOMAIN = os.getenv('PROPREPORTS_DOMAIN', '')
    USERNAME = os.getenv('PROPREPORTS_USER', '')
    PASSWORD = os.getenv('PROPREPORTS_PASS', '')
    DAYS_BACK = int(os.getenv('EXPORT_DAYS_BACK', '30'))

    if not all([DOMAIN, USERNAME, PASSWORD]):
        print("❌ Missing required environment variables: PROPREPORTS_DOMAIN, PROPREPORTS_USER, PROPREPORTS_PASS")
        raise SystemExit(1)
    
    # Crear exportador
    exporter = PropReportsExporter(DOMAIN, USERNAME, PASSWORD)
    
    # Exportar días configurados
    output_file = exporter.export_trades(days_back=DAYS_BACK)
    
    if output_file:
        print(f"\n✅ Exportación completada exitosamente")
        print(f"📁 Archivo: {output_file}")
    else:
        print("\n❌ Error en la exportación")

if __name__ == "__main__":
    main()