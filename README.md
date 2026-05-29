# 📊 Dashboard de Vendedores

Dashboard interactivo de ventas por vendedor y región, desarrollado con **Streamlit + Pandas + Plotly**.

## 🚀 Cómo ejecutar

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el dashboard
streamlit run dashboard_vendedores.py
```

## 📁 Estructura

```
dashboard-vendedores/
├── dashboard_vendedores.py   # App principal
├── sellers.xlsx              # Dataset
├── requirements.txt          # Dependencias
└── README.md
```

## ✨ Funcionalidades

- **KPIs globales**: vendedores activos, unidades vendidas, total ventas, promedio.
- **Filtros globales** (sidebar): región y rango de unidades vendidas.
- **Tabla interactiva** con filtro rápido por región.
- **Búsqueda de vendedor específico** con radar chart vs promedio de su región.
- **4 gráficas interactivas** en pestañas:
  - Unidades Vendidas por vendedor
  - Total de Ventas por vendedor
  - Promedio de Ventas por vendedor
  - Comparativa por región (pie + scatter)

## 🛠 Stack

| Herramienta | Uso |
|-------------|-----|
| Streamlit | Framework web interactivo |
| Pandas | Manejo y análisis de datos |
| Plotly | Gráficas interactivas |
| OpenPyXL | Lectura de archivos Excel |
