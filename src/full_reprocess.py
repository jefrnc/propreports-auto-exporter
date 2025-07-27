#!/usr/bin/env python3
"""
Reprocesador completo que genera todos los resúmenes necesarios
"""

import os
import sys
from datetime import datetime, timedelta
from advanced_exporter import reprocess_recent_days, export_date_range
from weekly_summary import generate_weekly_summary
from monthly_summary import generate_monthly_summary

def get_weeks_in_range(start_date, end_date):
    """Obtiene todas las semanas en un rango de fechas"""
    weeks = set()
    current = start_date
    
    while current <= end_date:
        # Obtener el lunes de esa semana
        monday = current - timedelta(days=current.weekday())
        weeks.add(monday)
        current += timedelta(days=1)
    
    return sorted(weeks)

def get_months_in_range(start_date, end_date):
    """Obtiene todos los meses en un rango de fechas"""
    months = set()
    current = start_date
    
    while current <= end_date:
        months.add((current.year, current.month))
        # Avanzar al siguiente mes
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)
    
    return sorted(months)

def full_reprocess(days_back=60):
    """
    Reprocesa días, genera resúmenes semanales y mensuales automáticamente
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"🚀 Reprocesamiento completo de {days_back} días")
    print(f"📅 Período: {start_date.strftime('%Y-%m-%d')} hasta {end_date.strftime('%Y-%m-%d')}")
    print("=" * 50)
    
    # 1. Exportar todos los días
    print("\n📊 FASE 1: Exportando datos diarios...")
    exported_files = export_date_range(start_date, end_date, force_update=True)
    print(f"✅ Exportados {len(exported_files)} archivos diarios")
    
    # 2. Generar resúmenes semanales
    print("\n📊 FASE 2: Generando resúmenes semanales...")
    weeks = get_weeks_in_range(start_date, end_date)
    weekly_count = 0
    
    for week_start in weeks:
        try:
            # Solo generar si la semana ya terminó o es la actual
            week_end = week_start + timedelta(days=6)
            if week_end <= end_date or week_start <= end_date:
                print(f"  📅 Procesando semana del {week_start.strftime('%Y-%m-%d')}...")
                generate_weekly_summary(week_start)
                weekly_count += 1
        except Exception as e:
            print(f"  ⚠️  Error procesando semana {week_start}: {e}")
    
    print(f"✅ Generados {weekly_count} resúmenes semanales")
    
    # 3. Generar resúmenes mensuales
    print("\n📊 FASE 3: Generando resúmenes mensuales...")
    months = get_months_in_range(start_date, end_date)
    monthly_count = 0
    
    for year, month in months:
        try:
            # Solo generar si el mes ya terminó o es el actual
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            if (year < current_year) or (year == current_year and month <= current_month):
                print(f"  📅 Procesando {year}-{month:02d}...")
                generate_monthly_summary(year, month)
                monthly_count += 1
        except Exception as e:
            print(f"  ⚠️  Error procesando mes {year}-{month:02d}: {e}")
    
    print(f"✅ Generados {monthly_count} resúmenes mensuales")
    
    print("\n" + "=" * 50)
    print("🎉 Reprocesamiento completo finalizado!")
    print(f"📊 Resumen:")
    print(f"  - {len(exported_files)} días exportados")
    print(f"  - {weekly_count} resúmenes semanales")
    print(f"  - {monthly_count} resúmenes mensuales")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
        full_reprocess(days)
    else:
        print("Uso: python full_reprocess.py <días>")
        print("Ejemplo: python full_reprocess.py 60")