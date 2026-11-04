# Ejecutar con: streamlit run dashboard.py
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard de Proyectos TI", layout="wide")
st.title("Dashboard de KPIs de Proyectos TI")

# Opción local: archivo en la misma carpeta
df = pd.read_csv("metricas.csv", parse_dates=["fecha_inicio", "fecha_fin"])

# Opción en la nube: descomenta y reemplaza la URL por la de tu archivo
# URL = "https://raw.githubusercontent.com/usuario/repo/main/proyectos_metricas.csv"
# df = pd.read_csv(URL, parse_dates=["fecha_inicio", "fecha_fin"])

# Filtro por proyecto
proyectos = st.sidebar.multiselect(
    "Selecciona proyectos", df["proyecto"].unique(), default=list(df["proyecto"].unique())
)
d = df[df["proyecto"].isin(proyectos)].copy()

# KPIs globales de la selección
EV, PV, AC = d["ev"].sum(), d["pv"].sum(), d["ac"].sum()
k1, k2, k3, k4 = st.columns(4)
k1.metric("SPI (cronograma)", f"{EV / PV:.2f}")
k2.metric("CPI (costo)", f"{EV / AC:.2f}")
k3.metric("% tareas completadas",
          f"{d['tareas_completadas'].sum() / d['tareas_planificadas'].sum():.0%}")
k4.metric("Satisfacción promedio", f"{d['satisfaccion_cliente'].mean():.2f} / 5")

st.divider()

# Gráfica 1: CPI por sprint
d["cpi_sprint"] = d["ev"] / d["ac"]
c1, c2 = st.columns(2)
c1.plotly_chart(px.line(d, x="sprint", y="cpi_sprint", color="proyecto", markers=True,
                        title="CPI por sprint (1 = presupuesto en línea)"),
                use_container_width=True)

# Gráfica 2: Defectos detectados vs corregidos
defectos = (d.groupby("proyecto")[["defectos_detectados", "defectos_corregidos"]]
            .sum().reset_index()
            .melt(id_vars="proyecto", var_name="tipo", value_name="cantidad"))
c2.plotly_chart(px.bar(defectos, x="proyecto", y="cantidad", color="tipo", barmode="group",
                       title="Defectos detectados vs corregidos"),
                use_container_width=True)

# Gráfica 3: Cobertura de pruebas por sprint
c3, c4 = st.columns(2)
c3.plotly_chart(px.line(d, x="sprint", y="cobertura_pruebas_pct", color="proyecto",
                        markers=True, title="Cobertura de pruebas (%)"),
                use_container_width=True)

# Gráfica 4: MTTR vs incidentes en producción
c4.plotly_chart(px.scatter(d, x="incidentes_produccion", y="mttr_horas", color="proyecto",
                           size="horas_trabajadas", title="Incidentes vs MTTR (horas)"),
                use_container_width=True)

st.subheader("Datos detallados")
st.dataframe(d, use_container_width=True)