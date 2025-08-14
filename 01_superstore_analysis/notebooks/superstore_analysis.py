import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
import sys

# Configuración de visualización
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
pio.templates.default = "plotly_white"

# === Carga de datos con manejo robusto de errores ===
try:
    data_path = Path('data') / 'Sample - Superstore.xls'  
    
    if not data_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo en la ruta: {data_path}")
    
    if data_path.suffix in ('.xls', '.xlsx'):
        df = pd.read_excel(data_path)  
    else:
        # Prueba diferentes codificaciones comunes
        encodings = ['utf-8', 'latin1', 'ISO-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(data_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("No se pudo determinar la codificación del archivo")

    print(f"Datos cargados correctamente. Filas: {len(df)}, Columnas: {len(df.columns)}")

except Exception as e:
    print(f"Error al cargar los datos: {str(e)}", file=sys.stderr)
    sys.exit(1)

# === Limpieza y preparación de datos ===
try:
    # Normalización de nombres de columnas
    df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
    
    # Conversión de fechas
    date_cols = [c for c in ['order_date', 'ship_date'] if c in df.columns]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Creación de variables derivadas
    if 'order_date' in df.columns:
        df['year'] = df['order_date'].dt.year
        df['year_month'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
        df['month_name'] = df['order_date'].dt.month_name()
    
    # Verificación de columnas numéricas esenciales
    numeric_cols = ['sales', 'profit', 'quantity']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

except Exception as e:
    print(f"Error en la preparación de datos: {str(e)}", file=sys.stderr)

# === Cálculo de KPIs con verificación ===
try:
    kpis = {}
    
    if 'sales' in df.columns:
        total_sales = df['sales'].sum()
        kpis['Total Sales'] = total_sales
        
        if 'profit' in df.columns:
            total_profit = df['profit'].sum()
            profit_margin = (total_profit / total_sales) if total_sales != 0 else np.nan
            kpis.update({
                'Total Profit': total_profit,
                'Profit Margin': f"{profit_margin:.2%}" if not np.isnan(profit_margin) else "N/A"
            })
    
    print("\n=== KPIs Principales ===")
    for k, v in kpis.items():
        print(f"{k}: {v}")

except Exception as e:
    print(f"Error al calcular KPIs: {str(e)}", file=sys.stderr)

# === Visualizaciones con verificación de datos ===
try:
    # 1. Tendencia mensual de ventas
    if 'year_month' in df.columns and 'sales' in df.columns:
        by_month = df.groupby('year_month', as_index=False).agg(
            sales=('sales', 'sum'),
            profit=('profit', 'sum') if 'profit' in df.columns else None
        )
        
        fig1 = px.line(by_month, x='year_month', y='sales', 
                      title='Tendencia Mensual de Ventas',
                      labels={'sales': 'Ventas', 'year_month': 'Mes'},
                      template='plotly_white')
        fig1.update_layout(hovermode='x unified')
        pio.write_html(fig1, file='ventas_por_mes.html', auto_open=False)
        fig1.show()
    
    # 2. Ventas por categoría y subcategoría (Top 20)
    if all(c in df.columns for c in ['category', 'sub_category', 'sales']):
        cat = df.groupby(['category', 'sub_category'], as_index=False)['sales'].sum()
        cat = cat.sort_values('sales', ascending=False).head(20)
        
        fig2 = px.bar(cat, x='sub_category', y='sales', color='category',
                     title='Top 20 Subcategorías por Ventas',
                     labels={'sales': 'Ventas', 'sub_category': 'Subcategoría'},
                     template='plotly_white')
        fig2.update_layout(xaxis={'categoryorder': 'total descending'})
        pio.write_html(fig2, file='top_subcategorias.html', auto_open=False)
        fig2.show()
    
    # 3. Ventas por región y segmento
    group_cols = [c for c in ['region', 'segment'] if c in df.columns]
    if group_cols and 'sales' in df.columns:
        reg = df.groupby(group_cols, as_index=False)['sales'].sum()
        
        fig3 = px.bar(reg, x=group_cols[0], y='sales', 
                     color=group_cols[1] if len(group_cols) > 1 else None,
                     barmode='group',
                     title='Ventas por ' + (' y '.join(group_cols).title()),
                     labels={'sales': 'Ventas'},
                     template='plotly_white')
        pio.write_html(fig3, file='ventas_por_region.html', auto_open=False)
        fig3.show()

except Exception as e:
    print(f"Error al generar visualizaciones: {str(e)}", file=sys.stderr)

# === Creación del dashboard consolidado ===
try:
    html_files = [p for p in Path('.').glob('*.html') if p.name != 'dashboard_superstore.html']
    
    if html_files:
        # Cabecera del dashboard
        parts = [
            '<!DOCTYPE html>',
            '<html lang="es">',
            '<head>',
            '<meta charset="UTF-8">',
            '<title>Dashboard Superstore</title>',
            '<style>',
            'body { font-family: Arial, sans-serif; margin: 20px; }',
            'h1 { color: #2c3e50; }',
            'h2 { color: #3498db; margin-top: 30px; }',
            '.kpi-box { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }',
            '</style>',
            '</head>',
            '<body>',
            '<h1>📊 Dashboard Superstore</h1>'
        ]
        
        # Sección de KPIs
        parts.append('<div class="kpi-box">')
        parts.append('<h2>🔍 KPIs Principales</h2>')
        for k, v in kpis.items():
            parts.append(f'<p><strong>{k}:</strong> {v}</p>')
        parts.append('</div>')
        
        # Gráficos
        for p in html_files:
            chart_name = p.stem.replace('_', ' ').title()
            parts.append(f'<h2>📈 {chart_name}</h2>')
            parts.append(f'<iframe src="{p.name}" width="100%" height="500" frameborder="0"></iframe>')
        
        parts.extend(['</body>', '</html>'])
        
        # Escribir el archivo del dashboard
        with open('dashboard_superstore.html', 'w', encoding='utf-8') as f:
            f.write('\n'.join(parts))
        
        print('\n✅ Dashboard creado exitosamente: dashboard_superstore.html')
    else:
        print('No se encontraron gráficos para incluir en el dashboard', file=sys.stderr)

except Exception as e:
    print(f"Error al crear el dashboard: {str(e)}", file=sys.stderr)
