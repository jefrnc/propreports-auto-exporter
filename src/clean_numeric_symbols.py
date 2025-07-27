#!/usr/bin/env python3
"""
Script para limpiar trades con símbolos numéricos de los archivos JSON existentes
"""

import os
import json
import glob
from datetime import datetime

def is_valid_trade(trade):
    """Valida si un trade es real o es una fila de subtotal/header"""
    # Los trades reales tienen:
    # - opened con formato de hora (HH:MM:SS)
    # - symbol que no es solo números
    # - type que es Long/Short
    
    symbol = trade.get('symbol', '')
    opened = trade.get('opened', '')
    trade_type = trade.get('type', '')
    
    # Verificar que no es un símbolo numérico
    if symbol.isdigit():
        return False
    
    # Verificar que opened tiene formato de hora
    if ':' not in opened:
        return False
    
    # Verificar que type es Long/Short
    if trade_type.lower() not in ['long', 'short']:
        return False
    
    return True

def clean_json_file(filepath):
    """Limpia un archivo JSON eliminando trades inválidos"""
    print(f"🔧 Procesando: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Obtener trades originales
        original_trades = data.get('trades', [])
        original_count = len(original_trades)
        
        # Filtrar trades válidos
        valid_trades = [trade for trade in original_trades if is_valid_trade(trade)]
        removed_count = original_count - len(valid_trades)
        
        if removed_count > 0:
            print(f"  ⚠️  Eliminados {removed_count} trades inválidos")
            
            # Actualizar datos
            data['trades'] = valid_trades
            
            # Recalcular summary
            data['summary'] = {
                'totalTrades': len(valid_trades),
                'totalPnL': round(sum(t.get('pnl', 0) for t in valid_trades), 2),
                'totalCommissions': round(sum(t.get('commission', 0) for t in valid_trades), 2),
                'netPnL': round(sum(t.get('net', t.get('pnl', 0) - t.get('commission', 0)) for t in valid_trades), 2),
                'winningTrades': len([t for t in valid_trades if t.get('pnl', 0) > 0]),
                'losingTrades': len([t for t in valid_trades if t.get('pnl', 0) < 0]),
                'symbols': list(set(t.get('symbol', '') for t in valid_trades if t.get('symbol')))
            }
            
            # Agregar metadata de limpieza
            if 'metadata' not in data:
                data['metadata'] = {}
            data['metadata']['cleaned'] = True
            data['metadata']['cleanedAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['metadata']['removedTrades'] = removed_count
            
            # Guardar archivo actualizado
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Archivo actualizado")
        else:
            print(f"  ✅ No se encontraron trades inválidos")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")

def clean_all_exports(base_dir='exports'):
    """Limpia todos los archivos JSON de exports"""
    print("🧹 Iniciando limpieza de trades con símbolos numéricos...")
    
    # Buscar todos los archivos JSON en daily
    daily_files = glob.glob(os.path.join(base_dir, 'daily', '*.json'))
    
    print(f"📁 Encontrados {len(daily_files)} archivos para procesar")
    
    total_cleaned = 0
    for filepath in sorted(daily_files):
        clean_json_file(filepath)
        total_cleaned += 1
    
    print(f"\n✅ Limpieza completada: {total_cleaned} archivos procesados")

if __name__ == "__main__":
    # Cambiar al directorio del test repo
    test_repo_dir = os.path.join(os.path.dirname(__file__), '..', 'test-propreports-export')
    if os.path.exists(test_repo_dir):
        os.chdir(test_repo_dir)
        print(f"📂 Trabajando en: {os.getcwd()}")
    
    clean_all_exports()