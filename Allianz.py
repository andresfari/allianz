

import streamlit as st
import yfinance as yf
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Variable de estado para controlar la visualización
if 'show_form' not in st.session_state:
    st.session_state.show_form = True

# Sección para ingresar datos del usuario
if st.session_state.show_form:
    with st.form("my_form"):
        # Título de la aplicación
        st.title("¡Bienvenido a Allianz Patrimonial!")
        st.image("allianz foto.png")
        st.write(" Completa los siguientes datos para conocer las opciones de inversión")
        nombre = st.text_input("Nombre completo")
        poliza = st.text_input("Número de póliza")
        contraseña = st.text_input("Contraseña")
        submitted = st.form_submit_button("Continuar")
        
    if submitted:
        if not nombre or not poliza or not contraseña:
            st.error("Falta información. Asegúrate de que esten todos los datos completos. ")
        else:
            st.session_state.show_form = False  # Cambiar a la sección de calculadora

# Función para calcular el rendimiento y riesgo
def calcular_rendimiento_riesgo(etf_symbol, period):
    data = yf.Ticker(etf_symbol).history(period=period)
    
    # Asegurarse de que hay datos disponibles
    if data.empty:
        return None, None
    
    # Cálculo del rendimiento total
    precio_inicial = data['Close'].iloc[0]
    precio_final = data['Close'].iloc[-1]
    rendimiento = ((precio_final / precio_inicial) - 1) * 100  # Convertir a porcentaje
    
    
    # Cálculo de la volatilidad (desviación estándar de los retornos diarios)
    retornos_diarios = data['Close'].pct_change().dropna()
    volatilidad = retornos_diarios.std() * (252 ** 0.5) * 100  # Anualizar la volatilidad
    
    return {
        "Rendimiento Total (%)": round(rendimiento, 2),
        "Riesgo (Desviación Estándar Anualizada) (%)": round(volatilidad, 2)
    }, data['Close']

# Nueva función para obtener la tasa libre de riesgo
def obtener_tasa_libre_de_riesgo():
    # Descargar los datos recientes del bono a 13 semanas
    tasa_irx = yf.Ticker("^IRX").history(period="1d")
    
    # Asegurarse de que los datos están disponibles
    if tasa_irx.empty:
        return None
    
    # Obtener la tasa más reciente en decimal (el valor viene en porcentaje)
    return tasa_irx["Close"].iloc[-1] / 100

# Nueva función para calcular el Sharpe ratio
def calcular_sharpe_ratio(rendimiento, volatilidad, tasa_libre_de_riesgo):
    if volatilidad == 0:  # Evitar división por cero
        return None
    return (rendimiento / 100 - tasa_libre_de_riesgo) / (volatilidad / 100)


# Lista de ETFs
ETFs_Data = [
    {"nombre": "AZ QQQ NASDAQ 100", "descripcion": "ETF que sigue el rendimiento del índice NASDAQ 100.", "simbolo": "QQQ"},
    {"nombre": "AZ SPDR S&P 500 ETF TRUST", "descripcion": "ETF que sigue el rendimiento del índice S&P 500.", "simbolo": "SPY"},
    {"nombre": "AZ SPDR DJIA TRUST", "descripcion": "ETF que sigue el rendimiento del índice Dow Jones Industrial Average.", "simbolo": "DIA"},
    {"nombre": "AZ VANGUARD EMERGING MARKET ETF", "descripcion": "ETF de Vanguard que sigue el rendimiento de mercados emergentes.", "simbolo": "VWO"},
    {"nombre": "AZ FINANCIAL SELECT SECTOR SPDR", "descripcion": "ETF que sigue el rendimiento del sector financiero de EE.UU.", "simbolo": "XLF"},
    {"nombre": "AZ HEALTH CARE SELECT SECTOR", "descripcion": "ETF que sigue el rendimiento del sector de salud de EE.UU.", "simbolo": "XLV"},
    {"nombre": "AZ DJ US HOME CONSTRUCT", "descripcion": "ETF que sigue el rendimiento del sector de construcción de viviendas en EE.UU.", "simbolo": "ITB"},
    {"nombre": "AZ SILVER TRUST", "descripcion": "ETF que sigue el precio de la plata.", "simbolo": "SLV"},
    {"nombre": "AZ MSCI TAIWAN INDEX FD", "descripcion": "ETF que sigue el rendimiento del índice MSCI Taiwan.", "simbolo": "EWT"},
    {"nombre": "AZ MSCI UNITED KINGDOM", "descripcion": "ETF que sigue el rendimiento del índice MSCI United Kingdom.", "simbolo": "EWU"},
    {"nombre": "AZ MSCI SOUTH KOREA IND", "descripcion": "ETF que sigue el rendimiento del índice MSCI South Korea.", "simbolo": "EWY"},
    {"nombre": "AZ MSCI EMU", "descripcion": "ETF que sigue el rendimiento del índice MSCI EMU (Unión Monetaria Europea).", "simbolo": "EZU"},
    {"nombre": "AZ MSCI JAPAN INDEX FD", "descripcion": "ETF que sigue el rendimiento del índice MSCI Japan.", "simbolo": "EWJ"},
    {"nombre": "AZ MSCI CANADA", "descripcion": "ETF que sigue el rendimiento del índice MSCI Canada.", "simbolo": "EWC"},
    {"nombre": "AZ MSCI GERMANY INDEX", "descripcion": "ETF que sigue el rendimiento del índice MSCI Germany.", "simbolo": "EWG"},
    {"nombre": "AZ MSCI AUSTRALIA INDEX", "descripcion": "ETF que sigue el rendimiento del índice MSCI Australia.", "simbolo": "EWA"},
    {"nombre": "AZ BARCLAYS AGGREGATE", "descripcion": "ETF que sigue el rendimiento del índice de bonos Barclays Aggregate.", "simbolo": "AGG"}
]

# Periodos en formato de duración para yfinance
periodos = {
    "1 mes": "1mo",
    "3 meses": "3mo",
    "6 meses": "6mo",
    "1 año": "1y",
    "año a la fecha": "ytd",
    "5 años": "5y",
    "10 años": "10y"
}

# Sección de cálculo y gráficos
if not st.session_state.show_form:
    st.title(" Análisis de instrumentos de inversión")
    st.write("### Aquí puedes visualizar los índices en los que puedes invertir, junto con su información financiera")

    # Selección de múltiples ETFs
    opciones_etfs = {etf["nombre"]: etf for etf in ETFs_Data}
    etfs_seleccionados = st.multiselect("Selecciona uno o más índices ETFs:", opciones_etfs.keys())
    

    # Selección de periodo
    periodo_seleccionado = st.selectbox("Selecciona un periodo:", list(periodos.keys()))

    #Entrada de cantidad a invertir
    inversion = st.number_input("Monto de inversión")
    
    # Mostrar descripción de los ETFs seleccionados
    if etfs_seleccionados:
        st.write("**Descripción de los ETFs seleccionados:**")
        for etf_nombre in etfs_seleccionados:
            etf = opciones_etfs[etf_nombre]
            st.write(f"**{etf['nombre']}:** {etf['descripcion']}")
            
        

        # Calcular y mostrar rendimiento y riesgo para cada ETF en el periodo seleccionado

        # Crear DataFrame con los resultados
        resultados = []
        precios_dict = {}
        for etf_nombre in etfs_seleccionados:
            etf = opciones_etfs[etf_nombre]
            resultado, precios = calcular_rendimiento_riesgo(etf["simbolo"], periodos[periodo_seleccionado])
            if resultado:
                resultados.append({
                    "ETF": etf["nombre"],
                    "Rendimiento Total (%)": resultado["Rendimiento Total (%)"],
                    "Riesgo (Desviación Estándar Anualizada) (%)": resultado["Riesgo (Desviación Estándar Anualizada) (%)"]
                })
                precios_dict[etf["nombre"]] = precios  # Guardar precios para graficar rendimiento acumulado

        # Convertir los resultados en un DataFrame
        resultados_df = pd.DataFrame(resultados)
        
       
        # Obtener tasa libre de riesgo y calcular Sharpe ratio para los ETFs seleccionados
        tasa_libre_de_riesgo = obtener_tasa_libre_de_riesgo()
        if tasa_libre_de_riesgo is not None:
            st.write("### Sharpe Ratio Calculado")
            sharpe_ratios = []
            for etf in resultados:
                sharpe_ratio = calcular_sharpe_ratio(etf["Rendimiento Total (%)"], etf["Riesgo (Desviación Estándar Anualizada) (%)"], tasa_libre_de_riesgo)
                if sharpe_ratio is not None:
                    sharpe_ratios.append({
                        "ETF": etf["ETF"],
                        "Sharpe Ratio": round(sharpe_ratio, 2)
                    })
           
           
            # Mostrar tabla de Sharpe ratios
            sharpe_df = pd.DataFrame(sharpe_ratios).set_index("ETF")
            st.table(sharpe_df.style.format("{:.2f}"))
        else:
            st.warning("No se pudo obtener la tasa libre de riesgo para calcular el Sharpe ratio.")

        # Mostrar tabla de resultados
        st.write("### Rendimiento y Riesgo")
        st.table(resultados_df.set_index("ETF").style.format("{:.2f}"))

        # Botón para calcular el total de la inversión
        if st.button("Calcular crecimiento de la inversión"):
            if inversion <= 999:
                st.error("La aportación mínima es de $1,000. Por favor, ingresa un monto de inversión válido.")
            else:
                for etf in resultados:
                    rendimiento = etf["Rendimiento Total (%)"] / 100  # Convertir a decimal
                    total_inversion = inversion * (1 + rendimiento)
                    st.write(f"Por tu inversión en el ETF **{etf['ETF']}**, tu saldo final sería de  **${total_inversion:.2f}**.")

        
        # Gráfica de Rendimiento Acumulado con Seaborn
        st.write("### Gráfica de Rendimiento Acumulado")
        rendimiento_acumulado_df = pd.DataFrame()
        for etf_nombre, precios in precios_dict.items():
            rendimiento_acumulado_df[etf_nombre] = (precios / precios.iloc[0] - 1) * 100  # Rendimiento acumulado en %

        plt.figure(figsize=(10, 6))
        sns.lineplot(data=rendimiento_acumulado_df)
        plt.title("Rendimiento Acumulado de los ETFs Seleccionados")
        plt.xlabel("Fecha")
        plt.ylabel("Rendimiento Acumulado (%)")
        plt.legend(title="ETFs", labels=etfs_seleccionados)
        st.pyplot(plt.gcf())

        # Gráfica de Riesgo Acumulado con Seaborn
        st.write("### Gráfica de Riesgo Acumulado")
        riesgo_acumulado_df = pd.DataFrame()
        for etf_nombre, precios in precios_dict.items():
            retornos_diarios = precios.pct_change().dropna()
            volatilidad_acumulada = (retornos_diarios.expanding().std() * (252 ** 0.5)) * 100  # Anualizar la volatilidad acumulada
            riesgo_acumulado_df[etf_nombre] = volatilidad_acumulada

        plt.figure(figsize=(10, 6))
        sns.lineplot(data=riesgo_acumulado_df)
        plt.title("Riesgo Acumulado de los ETFs Seleccionados")
        plt.xlabel("Fecha")
        plt.ylabel("Volatilidad Acumulada (%)")
        plt.legend(title="ETFs", labels=etfs_seleccionados)
        st.pyplot(plt.gcf())
        
        st.write("# ¿Qué significan estos datos?")
        st.write("¿No le sabes a las finanzas? No te apures, que para eso estamos. Selecciona una pregunta para obtener una explicación de cada concepto.")

        # Título de la aplicación

        # Definir las preguntas y respuestas
        faq = {
            "¿Qué es un ETF?": "Un ETF (Fondo Cotizado en Bolsa) es un tipo de inversión que agrupa varios activos, como acciones o bonos, y se puede comprar o vender en la bolsa de valores. Ofrece diversificación y suele tener costos más bajos que los fondos de inversión tradicionales.",
            "¿Qué es el rendimiento?": "El rendimiento es el crecimiento o la disminución en el valor de una inversión durante un período de tiempo específico. Se expresa generalmente como un porcentaje.",
            "¿Qué es el riesgo en las inversiones?": "El riesgo es la posibilidad de que el valor de una inversión baje. Se mide a menudo por la volatilidad de los precios de esa inversión.",
            "¿Qué es el Sharpe Ratio?": "El Sharpe Ratio es una medida que evalúa el rendimiento de una inversión en relación con su riesgo. Para evaluar la inversión se utiliza una tasa libre de riesgo, que en este caso son los Bonos del Tesoro de los Estados Unidos. Un Sharpe Ratio alto indica que la inversión tiene un buen rendimiento ajustado al riesgo.",
            "¿Cuál sería un buen Sharpe Ratio?": "Si es menor a 1, la inversión no genera buenos retornos. Si el Sharpe tiene valores entre 1 y 3 se considera como un buen nivel de riesgo/rendimiento. Si es mayor a 3 se considera una excelente inversión.",
            "¿Qué es una tasa libre de riesgo?": "La tasa libre de riesgo es el rendimiento que se podría obtener de una inversión sin riesgo de pérdida, como los bonos del gobierno de corta duración."
        }

        # Crear un menú desplegable para seleccionar preguntas
        pregunta_seleccionada = st.selectbox("Selecciona una pregunta:", list(faq.keys()))

        # Mostrar la respuesta de la pregunta seleccionada
        st.write("**Respuesta:**")
        st.write(faq[pregunta_seleccionada])


        
    # Botón para regresar al formulario
    if st.button("Regresar al formulario de datos personales"):
        st.session_state.show_form = True  # Volver a mostrar el formulario

