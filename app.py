# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from terminalbaires.simulation import SIMULAR
from terminalbaires.generators import calcular_promedio_por_ciclo,contar_eventos_binarios

st.title("Simulación – Terminal Baires")

# ---- sidebar para parámetros ----
with st.sidebar:
    rendimiento = st.number_input("Rendimiento grúa (t/h)", 10, 100, 25)
    tasa        = st.number_input("Barcos por mes", 1.0, 60.0, 30.0)
    barcos      = st.number_input("Barcos a servir", 1, 50, 10)
    lanzar      = st.button("Ejecutar simulación")

# ---- lógica ----
data_path = Path("data")
if lanzar:
    with st.spinner("Corriendo simulación..."):
        SIMULAR(rendimiento, tasa, barcos, data_path)
    st.success("¡Simulación terminada!")

# ---- carga automática de los dos últimos logs ----
log_files = sorted(data_path.glob("*_log.csv"), key=lambda p: p.stat().st_mtime)

if len(log_files) < 2:
    st.error("No hay suficientes archivos *_log.csv en la carpeta.")
    st.stop()

file_sel, file_sel2 = log_files[-2:]          # los dos más nuevos

# lee los CSV
df1 = pd.read_csv(file_sel,  sep=";", decimal=",")
df2 = pd.read_csv(file_sel2, sep=";", decimal=",")

# (opcional) informa qué archivos se usaron
st.info(f"Procesando: {file_sel.name}  ➜  {file_sel2.name}")

# Variables a analizar
variables = [
    "tiempo_espera",
    "tiempo_servicio",
    "tiempo_ocioso",
    "tiempo_total_operacion",
]
# Agrupamos por barco (id) y calculamos promedio para cada df

st.subheader("Resumen de resultados para los escenarios")
        
promedio1, desvio1, detalle1 = calcular_promedio_por_ciclo(df1, "tiempo_espera")
promedio1S, desvio1S, detalle1S = calcular_promedio_por_ciclo(df1, "tiempo_servicio")
promedio1O, desvio1O, detalle1O = calcular_promedio_por_ciclo(df1, "tiempo_ocioso")
promedio1T, desvio1T, detalle1T = calcular_promedio_por_ciclo(df1, "tiempo_total_operacion")

promedio2, desvio2, detalle2 = calcular_promedio_por_ciclo(df2, "tiempo_espera")
promedio2S, desvio2S, detalle2S= calcular_promedio_por_ciclo(df2, "tiempo_servicio")
promedio2O, desvio2O, detalle2O= calcular_promedio_por_ciclo(df2, "tiempo_ocioso")
promedio2T, desvio2T, detalle2T  = calcular_promedio_por_ciclo(df2, "tiempo_total_operacion")

# ─────── armamos la tabla resumen ───────────────────────────────────────────────────
tabla = pd.DataFrame(
    {
        "Escenario": [f'1G_{rendimiento}_{tasa}_{barcos}', f'2G_{rendimiento}_{tasa}_{barcos}'],
        "Espera":   [detalle1,       detalle2],
        "Servicio": [detalle1S,      detalle2S],
        "Ocioso":   [detalle1O,      detalle2O],
        "Total":    [detalle1T,      detalle2T],
    }
)

st.subheader("Resumen de resultados")
st.dataframe(tabla.style, use_container_width=True)


# Variables a analizar
variables = [
    "tiempo_espera",
    "tiempo_servicio",
    "tiempo_ocioso",
    "tiempo_total_operacion"
]

# Agrupamos por barco (id) y calculamos promedio para cada df
df1_promedios = df1.groupby("id")[variables].mean().reset_index()
df2_promedios = df2.groupby("id")[variables].mean().reset_index()

st.header("Comparación de variables por barco")

for var in variables:
    st.subheader(var.capitalize())

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df1_promedios["id"], df1_promedios[var],
            label="1 grúa", marker="o", markersize=3, linewidth=1)
    ax.plot(df2_promedios["id"], df2_promedios[var],
            label="2 grúas", marker="x", markersize=3, linewidth=1)
    ax.set_xlabel("ID del Barco")
    ax.set_ylabel(var)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig, use_container_width=True)
