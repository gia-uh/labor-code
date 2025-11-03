import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path


AREAS = {"AREA CENTRAL":"ac",
     "BIOMAT":"biomat",
     "CEAP":"ceap",
     "CEDEM":"cedem",
     "CEEC": "ceec",
     "CEHSEU":"cehseu",
     "CEPES":"cepes",
     "CETED":"ceted",
     "CIEI":"ciei",
     "CIM":"cim",
     "COLEGIO GRADO 12":"grado12",
     "CONFUCIO":"confucio",
     "FACULTAD DE ARTES Y LETRAS":"fayl",
     "FACULTAD DE BIOLOGIA":"fbio",
     "FACULTAD DE COMUNICACION":"fcom",
     "FACULTAD DE CONTABILIDAD Y FINANZAS":"fcf",
     "FACULTAD DE DERECHO":"lex",
     "FACULTAD DE ECONOMIA":"fec",
     "FACULTAD DE ESPAÑOL PARA NO HISPANOHABLANTES":"fenhi",
     "FACULTAD DE FILOSOFIA E HISTORIA":"ffh",
     "FACULTAD DE FISICA":"fisica",
     "FACULTAD DE GEOGRAFIA":"geo",
     "FACULTAD DE LENGUAS EXTRANJERAS":"flex",
     "FACULTAD DE MATEMATICA Y COMPUTACION":"matcom",
     "FACULTAD DE PSICOLOGIA":"psico",
     "FACULTAD DE QUIMICA":"fq",
     "FACULTAD DE TURISMO":"ftur",
     "FACULTAD PREPARATORIA":"fpi",
     "FLACSO":"flacso",
     "FUNDACION":"fundacion",
     "IMRE":"imre",
     "INSTEC":"instec",
     "INSTITUTO DE FARMACIA Y ALIMENTOS":"ifal",
     "IRIS":"iris",
     "ISDI":"isdi",
     "JBN":"jbn",
     "RECTORADO":"rect",
     "SAN GERONIMO":"sangeronimo",
     "UPA":"upa"
    }

CAT = {
    "additions":"AGREGAR" ,
    "deletions":"ELIMINAR",
    "modifications":"MODIFICACR",
    "questions": "DUDAS"
}    

mappings = st.session_state["mappings"]
def load_all_data_from_folder(file_option: str ="all", cat_option: str ="all"):
    """
    Loads all JSON data from the specified folders
    """
    data = []
    
    if file_option == "all":
        folders = [os.path.join("data", f) for f in os.listdir("data")]
    
    else:
        folders = [f"data/{file_option}"]
    
    
    for folder in folders:
        for file in Path(folder).iterdir():
            try:
                content = json.load(file.open())
                for key,value in content.items():
                    if key.isnumeric():
                        base = {"Paragrafo": pars[key], "Area":content["Area"]}
                        if cat_option == "all":
                            for k,v in value.items():
                                new_base = base.copy()
                                new_base["Categoria"] = CAT[k]
                                for text in v:
                                    new = new_base.copy()
                                    new["Informacion"] = text.strip()
                                    data.append(new)
                        else:
                            base.update({"Categoria": CAT[cat_option]})
                            for text in value[cat_option]:
                                new = base.copy()
                                new["Informacion"] = text.strip()
                                data.append(new)
                            
            
            except Exception as e:
                st.warning(f"Error al cargar {file}: {str(e)}")
    
    return data


def current_areas():
    yield "TODAS"
    for key,value in AREAS.items():
        folder = f"data/{value}"
        if os.path.exists(folder) and os.path.isdir(folder):
            yield key
        
col1, col2, col3 = st.columns(3)

with col1:
   area_option =  st.selectbox("Areas",current_areas())
   file_option = "all" if area_option == "TODAS" else AREAS[area_option]
   
with col2:
    question_option = st.selectbox("Preguntas",["TODAS","AGREGAR","ELIMINAR","MODIFICACR","DUDAS"])
    cat_option = "all" if question_option=="TODAS" else question_option


with col3:
    type_option = st.write("T")


def main():
    st.set_page_config(
        page_title="Análisis de Interacciones de Usuarios",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Análisis de Interacciones de Usuarios")
    st.markdown("Analiza las interacciones de usuarios con el proceso de consulta")
    
    # Si no hay datos, mostrar mensaje
    if 'df' not in st.session_state or st.session_state.df.empty:
        st.info("""
        ### Instrucciones:
        1. Especifica la ruta donde están las carpetas con archivos JSON
        2. Haz clic en 'Cargar Datos'
        3. Los datos deben tener al menos estos campos:
           - `pregunta`: La pregunta con la que interactuó el usuario
           - `tipo_interaccion`: Agregar, Eliminar, Modificar, Dudas
           - `area`: Área de la interacción (opcional)
        """)
        return
    
    df = st.session_state.df
    
    # Filtros
    areas_disponibles = sorted(df['area'].unique())
    tipos_interaccion = sorted(df['tipo_interaccion'].unique())
    
    # Selección múltiple para áreas
    areas_seleccionadas = st.sidebar.multiselect( 
        "Selecciona el área:",
        options=areas_disponibles,
        default=areas_disponibles if len(areas_disponibles) > 0 else []
    )
    
    # Selección múltiple para tipos de interacción
    tipos_seleccionados = st.sidebar.multiselect(
        "Selecciona el tipo de interacción:",
        options=tipos_interaccion,
        default=tipos_interaccion if len(tipos_interaccion) > 0 else []
    )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if areas_seleccionadas:
        df_filtrado = df_filtrado[df_filtrado['area'].isin(areas_seleccionadas)]
    
    if tipos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['tipo_interaccion'].isin(tipos_seleccionados)]
    
    # Mostrar resumen
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interacciones", len(df_filtrado))
    
    with col2:
        st.metric("Áreas", len(areas_seleccionadas) if areas_seleccionadas else "Todas")
    
    with col3:
        st.metric("Tipos Interacción", len(tipos_seleccionados) if tipos_seleccionados else "Todos")
    
    with col4:
        st.metric("Preguntas Únicas", df_filtrado['pregunta'].nunique())
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📋 Datos Detallados", "📈 Análisis por Área", "🔍 Análisis por Tipo"])
    
    with tab1:
        st.subheader("Datos Filtrados")
        
        # Mostrar dataframe con opciones
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True
        )
        
        # Opción para descargar datos filtrados
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name="interacciones_filtradas.csv",
            mime="text/csv"
        )
    
    with tab2:
        st.subheader("Análisis por Área")
        
        if not df_filtrado.empty:
            # Resumen por área
            resumen_area = df_filtrado.groupby('area').agg({
                'pregunta': 'count',
                'tipo_interaccion': lambda x: x.nunique(),
                'usuario': lambda x: x.nunique() if 'usuario' in df_filtrado.columns else 0
            }).rename(columns={
                'pregunta': 'total_interacciones',
                'tipo_interaccion': 'tipos_interaccion_unicos',
                'usuario': 'usuarios_unicos'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Resumen por Área:**")
                st.dataframe(resumen_area, use_container_width=True)
            
            with col2:
                # Gráfico de distribución por área
                if len(resumen_area) > 0:
                    st.write("**Distribución por Área:**")
                    chart_data = resumen_area.set_index('area')['total_interacciones']
                    st.bar_chart(chart_data)
    
    with tab3:
        st.subheader("Análisis por Tipo de Interacción")
        
        if not df_filtrado.empty:
            # Resumen por tipo de interacción
            resumen_tipo = df_filtrado.groupby('tipo_interaccion').agg({
                'pregunta': 'count',
                'area': lambda x: x.nunique(),
                'usuario': lambda x: x.nunique() if 'usuario' in df_filtrado.columns else 0
            }).rename(columns={
                'pregunta': 'total_interacciones',
                'area': 'areas_unicas',
                'usuario': 'usuarios_unicos'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Resumen por Tipo:**")
                st.dataframe(resumen_tipo, use_container_width=True)
            
            with col2:
                # Gráfico de distribución por tipo
                if len(resumen_tipo) > 0:
                    st.write("**Distribución por Tipo:**")
                    chart_data = resumen_tipo.set_index('tipo_interaccion')['total_interacciones']
                    st.bar_chart(chart_data)
            
            # Preguntas más frecuentes por tipo de interacción
            st.write("**Preguntas Más Frecuentes por Tipo:**")
            for tipo in tipos_seleccionados if tipos_seleccionados else tipos_interaccion:
                df_tipo = df_filtrado[df_filtrado['tipo_interaccion'] == tipo]
                if not df_tipo.empty:
                    preguntas_frecuentes = df_tipo['pregunta'].value_counts().head(5)
                    if not preguntas_frecuentes.empty:
                        st.write(f"**{tipo} - Top 5 Preguntas:**")
                        st.dataframe(preguntas_frecuentes.reset_index().rename(
                            columns={'index': 'Pregunta', 'pregunta': 'Frecuencia'}
                        ), use_container_width=True)

if __name__ == "__main__":
    pars = st.session_state.project["paragraphs"]
    print(pars["199"])
    articles = st.session_state.project["articles"]
    print(articles["199"])
    print(mappings["articles"]["199"])
    print(load_all_data_from_folder())
    main()