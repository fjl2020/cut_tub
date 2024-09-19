import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

# Función para hacer la optimización de cortes (greedy) con cantidad de tubos
def cortar_tubos(largos_tubos_cantidad, cortes_necesarios):
    tubos_usados = []
    cortes_restantes = cortes_necesarios.copy()

    for largo_tubo, cantidad_tubos in largos_tubos_cantidad.items():
        for _ in range(cantidad_tubos):  # Iterar sobre cada tubo disponible
            cortes_en_tubo = []
            espacio_disponible = largo_tubo
            
            for corte, cantidad in cortes_restantes.items():
                while cantidad > 0 and corte <= espacio_disponible:
                    cortes_en_tubo.append(corte)
                    espacio_disponible -= corte
                    cantidad -= 1

                cortes_restantes[corte] = cantidad

            tubos_usados.append({
                'largo_tubo': largo_tubo,
                'cortes_realizados': cortes_en_tubo,
                'espacio_sobrante': espacio_disponible
            })

            # Si ya no quedan más cortes, podemos terminar
            if sum(cortes_restantes.values()) == 0:
                break

        if sum(cortes_restantes.values()) == 0:
            break

    return tubos_usados, cortes_restantes

# Función para convertir el resultado a un diccionario
def generar_diccionario_resultados(tubos_usados):
    resultados = []
    for i, tubo in enumerate(tubos_usados):
        for corte in tubo['cortes_realizados']:
            resultados.append({
                'Tubo': f"Tubo {i+1}",
                'Largo Tubo': tubo['largo_tubo'],
                'Corte Realizado': corte,
                'Espacio Sobrante': tubo['espacio_sobrante']
            })
    return resultados

# Función para exportar los resultados a CSV en formato de descarga
def exportar_csv(diccionario_resultados):
    df_resultados = pd.DataFrame(diccionario_resultados)
    output = io.StringIO()
    df_resultados.to_csv(output, index=False)
    return output.getvalue()

# Función para dibujar gráfico de tubos con cortes y bordes
def graficar_tubos_con_bordes(tubos_usados):
    fig = go.Figure()

    for i, tubo in enumerate(tubos_usados):
        largo_tubo = tubo['largo_tubo']
        cortes = tubo['cortes_realizados']
        espacio_sobrante = tubo['espacio_sobrante']
        
        # Añadir una barra para el tubo con borde
        fig.add_trace(go.Bar(
            y=[f"Tubo {i+1}"],
            x=[largo_tubo],
            orientation='h',
            marker=dict(color='lightgray', line=dict(color='black', width=2)),  # Borde del tubo
            name=f"Tubo {i+1} (Total: {largo_tubo})"
        ))

        # Añadir los cortes realizados dentro del tubo con bordes
        acumulado = 0
        for corte in cortes:
            fig.add_trace(go.Bar(
                y=[f"Tubo {i+1}"],
                x=[corte],
                orientation='h',
                base=acumulado,
                marker=dict(color='green', line=dict(color='black', width=2)),  # Borde de los cortes
                name=f"Corte {corte} mm"
            ))

            # Añadir una línea separadora después de cada corte
            acumulado += corte
            fig.add_trace(go.Scatter(
                x=[acumulado, acumulado],
                y=[f"Tubo {i+1}", f"Tubo {i+1}"],
                mode="lines",
                line=dict(color="black", width=2, dash="dash"),
                showlegend=False
            ))

        # Añadir el espacio sobrante al final del tubo con borde
        if espacio_sobrante > 0:
            fig.add_trace(go.Bar(
                y=[f"Tubo {i+1}"],
                x=[espacio_sobrante],
                orientation='h',
                base=acumulado,
                marker=dict(color='red', line=dict(color='black', width=2)),  # Borde del espacio sobrante
                name=f"Espacio Sobrante {espacio_sobrante} mm"
            ))

    fig.update_layout(
        barmode='stack',
        title="Optimización de Tubos y Cortes con Bordes",
        xaxis_title="Longitud (mm)",
        yaxis_title="Tubos",
        showlegend=False,
        height=400 + len(tubos_usados) * 50  # Ajustar altura dependiendo de cuántos tubos haya
    )
    
    return fig

# Streamlit app
st.title("Optimización de Cortes de Tubos")

# Cargar tabla de cortes
st.subheader("Tabla de Cortes Necesarios")
st.write("Ingresa los largos de corte y la cantidad necesaria de cada uno.")
cortes_input = st.text_area("Largos de cortes (formato: largo,cantidad)", "200,2\n150,4\n100,3")
cortes_data = []
if cortes_input:
    cortes_data = [list(map(int, line.split(','))) for line in cortes_input.splitlines()]

cortes_df = pd.DataFrame(cortes_data, columns=["Largo", "Cantidad"])
st.write(cortes_df)

# Cargar tabla de largos de tubos y cantidad de tubos disponibles
st.subheader("Tabla de Largos de Tubos Disponibles y Cantidad de Tubos")
st.write("Ingresa los largos de tubos disponibles y la cantidad de cada largo.")
tubos_input = st.text_area("Largos de tubos y cantidad de tubos (formato: largo,cantidad)", "5000,2\n6000,3\n7000,1")
tubos_data = []
if tubos_input:
    tubos_data = [list(map(int, line.split(','))) for line in tubos_input.splitlines()]

tubos_df = pd.DataFrame(tubos_data, columns=["Largo Tubo", "Cantidad"])
st.write(tubos_df)

# Botón para ejecutar la optimización
if st.button("Optimizar Cortes"):
    # Convertir los datos de entrada
    cortes_necesarios = {row["Largo"]: row["Cantidad"] for _, row in cortes_df.iterrows()}
    largos_tubos_cantidad = {row["Largo Tubo"]: row["Cantidad"] for _, row in tubos_df.iterrows()}

    # Ejecutar el algoritmo de optimización
    tubos_usados, cortes_restantes = cortar_tubos(largos_tubos_cantidad, cortes_necesarios)

    # Generar el diccionario de resultados
    diccionario_resultados = generar_diccionario_resultados(tubos_usados)
    
    # Exportar a CSV
    csv_data = exportar_csv(diccionario_resultados)

    # Mostrar resultados
    st.subheader("Resultados de la Optimización")
    for i, tubo in enumerate(tubos_usados):
        st.write(f"Tubo {i+1}: {tubo['largo_tubo']} mm")
        st.write(f"Cortes realizados: {tubo['cortes_realizados']}")
        st.write(f"Espacio sobrante: {tubo['espacio_sobrante']} mm")

    if sum(cortes_restantes.values()) > 0:
        st.warning("No se pudieron cortar todas las piezas requeridas con los tubos disponibles.")
    else:
        st.success("Se cortaron todas las piezas requeridas.")

    # Botón para descargar el archivo CSV
    st.download_button(
        label="Descargar CSV",
        data=csv_data,
        file_name="resultados_cortes.csv",
        mime="text/csv",
    )

    # Mostrar gráfico de los tubos con bordes
    st.subheader("Gráfico de Tubos y Cortes con Bordes")
    fig = graficar_tubos_con_bordes(tubos_usados)
    st.plotly_chart(fig)
