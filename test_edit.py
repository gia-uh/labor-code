# import streamlit as st
# import json
# from datetime import datetime

# def texto_con_editor(texto_inicial):
#     """
#     Componente que muestra un texto y permite seleccionar una acción
#     con editor de texto para cada opción
#     """
    
#     # Dividir la pantalla en dos columnas
#     col1, col2 = st.columns([1, 2])
    
#     with col1:
#         # Mostrar el texto original en un cuadro de texto
#         st.subheader("📝 Texto Original")
#         st.text_area(
#             "Texto a revisar:",
#             value=texto_inicial,
#             height=200,
#             disabled=True,
#             key="texto_original"
#         )
        
#         # Opciones de acción
#         st.subheader("🛠️ Acciones")
#         opcion = st.radio(
#             "Selecciona una acción:",
#             ["Agregar", "Eliminar", "Modificar", "Dudas"],
#             horizontal=True
#         )
    
#     with col2:
#         st.subheader(f"✏️ Editor - {opcion}")
        
#         # Texto por defecto según la opción seleccionada
#         textos_por_defecto = {
#             "Agregar": "Escribe aquí la información que quieres agregar...",
#             "Eliminar": "Selecciona el texto que quieres eliminar...",
#             "Modificar": "Escribe tu modificación propuesta...",
#             "Dudas": "¿Qué dudas tienes sobre este texto?..."
#         }
        
#         # Editor de texto
#         texto_editado = st.text_area(
#             f"Editor de {opcion}:",
#             value=textos_por_defecto[opcion],
#             height=200,
#             key=f"editor_{opcion.lower()}"
#         )
        
#         # Botón para procesar la acción
#         if st.button(f"💾 Guardar {opcion}", type="primary"):
#             guardar_cambios(opcion, texto_editado, texto_inicial)
        
#         # Mostrar historial de cambios si existe
#         mostrar_historial()

# def guardar_cambios(opcion, texto_editado, texto_original):
#     """Guarda los cambios realizados"""
    
#     timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
#     cambio = {
#         "fecha": timestamp,
#         "accion": opcion,
#         "texto_original": texto_original,
#         "texto_editado": texto_editado,
#         "comentario": f"{opcion} realizado el {timestamp}"
#     }
    
#     # Guardar en session state
#     if "historial_cambios" not in st.session_state:
#         st.session_state.historial_cambios = []
    
#     st.session_state.historial_cambios.append(cambio)
    
#     st.success(f"✅ {opcion} guardado correctamente!")
#     st.balloons()

# def mostrar_historial():
#     """Muestra el historial de cambios"""
    
#     if "historial_cambios" in st.session_state and st.session_state.historial_cambios:
#         st.subheader("📋 Historial de Cambios")
        
#         for i, cambio in enumerate(reversed(st.session_state.historial_cambios[-5:]), 1):
#             with st.expander(f"{cambio['accion']} - {cambio['fecha']}"):
#                 st.write(f"**Acción:** {cambio['accion']}")
#                 st.write(f"**Fecha:** {cambio['fecha']}")
#                 st.write(f"**Texto editado:**")
#                 st.code(cambio['texto_editado'], language="text")
                
#                 # Botón para eliminar este cambio
#                 if st.button(f"🗑️ Eliminar este cambio", key=f"eliminar_{i}"):
#                     eliminar_cambio(i-1)

# def eliminar_cambio(indice):
#     """Elimina un cambio del historial"""
#     if "historial_cambios" in st.session_state:
#         # Convertir a lista y eliminar el elemento
#         cambios = st.session_state.historial_cambios
#         indice_real = len(cambios) - 1 - indice
#         if 0 <= indice_real < len(cambios):
#             del cambios[indice_real]
#             st.session_state.historial_cambios = cambios
#             st.rerun()

# # Función principal de la aplicación
# def main():
#     st.set_page_config(
#         page_title="Editor de Texto Interactivo",
#         page_icon="📝",
#         layout="wide"
#     )
    
#     st.title("📝 Editor de Texto Interactivo")
#     st.markdown("---")
    
#     # Texto de ejemplo o entrada del usuario
#     texto_ejemplo = """
#     La inteligencia artificial está transformando la forma en que interactuamos 
#     con la tecnología. Desde asistentes virtuales hasta sistemas de recomendación, 
#     la IA está presente en muchas áreas de nuestra vida diaria. 
    
#     El aprendizaje automático permite a las computadoras aprender de los datos 
#     y mejorar su rendimiento sin ser programadas explícitamente para cada tarea.
#     """
    
#     # Input para que el usuario pueda ingresar su propio texto
#     texto_usuario = st.text_area(
#         "📋 Ingresa tu texto aquí (opcional):",
#         value=texto_ejemplo,
#         height=100,
#         help="Puedes usar el texto de ejemplo o escribir el tuyo propio"
#     )
    
#     st.markdown("---")
    
#     # Llamar al componente principal
#     texto_con_editor(texto_usuario)
    
#     # Información adicional
#     with st.sidebar:
#         st.header("ℹ️ Información")
#         st.markdown("""
#         **Opciones disponibles:**
#         - **Agregar**: Añadir nueva información al texto
#         - **Eliminar**: Indicar qué partes quieres quitar
#         - **Modificar**: Proponer cambios al texto existente
#         - **Dudas**: Plantear preguntas o dudas sobre el contenido
        
#         **Características:**
#         - Editor de texto para cada acción
#         - Historial de cambios
#         - Interfaz intuitiva
#         """)
        
#         # Botón para limpiar historial
#         if st.button("🧹 Limpiar Historial"):
#             if "historial_cambios" in st.session_state:
#                 st.session_state.historial_cambios = []
#                 st.success("Historial limpiado!")
#                 st.rerun()

# if __name__ == "__main__":
#     main()
import streamlit as st
import json
from datetime import datetime

def texto_interactivo(texto_inicial):
    """
    Componente que muestra texto renderizado y permite seleccionar acciones
    con guardado automático
    """
    
    # Inicializar session state si no existe
    if "texto_actual" not in st.session_state:
        st.session_state.texto_actual = texto_inicial
    if "seleccion_actual" not in st.session_state:
        st.session_state.seleccion_actual = ""
    if "accion_actual" not in st.session_state:
        st.session_state.accion_actual = None
    if "comentarios" not in st.session_state:
        st.session_state.comentarios = []
    
    # Dividir la pantalla
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📖 Texto para revisar")
        
        # Mostrar el texto renderizado con opción de selección
        texto_seleccionado = st.text_area(
            "Selecciona texto para actuar:",
            value=st.session_state.texto_actual,
            height=300,
            key="texto_renderizado",
            label_visibility="collapsed"
        )
        
        # Detectar selección de texto
        if texto_seleccionado != st.session_state.texto_actual:
            st.session_state.seleccion_actual = texto_seleccionado
            st.session_state.accion_actual = None
            st.rerun()
    
    with col2:
        st.subheader("🛠️ Acciones")
        
        if st.session_state.seleccion_actual:
            st.info(f"📌 Texto seleccionado:\n\n*{st.session_state.seleccion_actual[:100]}...*")
            
            # Opciones de acción
            opcion = st.radio(
                "¿Qué quieres hacer?",
                ["Agregar", "Eliminar", "Modificar", "Dudas"],
                key="opciones_accion"
            )
            
            st.session_state.accion_actual = opcion
            
            # Editor según la acción
            textos_guia = {
                "Agregar": "¿Qué información quieres agregar?",
                "Eliminar": "¿Por qué quieres eliminar este texto?",
                "Modificar": "¿Cómo quieres modificar este texto?",
                "Dudas": "¿Qué dudas tienes sobre este texto?"
            }
            
            comentario = st.text_area(
                textos_guia[opcion],
                height=150,
                key="editor_comentario"
            )
            
            # Guardado automático cuando se escribe
            if comentario and comentario != textos_guia[opcion]:
                guardar_accion_automatico(opcion, st.session_state.seleccion_actual, comentario)
                st.session_state.seleccion_actual = ""
                st.session_state.accion_actual = None
                st.success("✅ Acción guardada automáticamente!")
                st.rerun()
        
        else:
            st.info("👆 Selecciona texto en el área izquierda para habilitar las acciones")
    
    # Mostrar historial de acciones
    mostrar_historial_acciones()

def guardar_accion_automatico(accion, texto_seleccionado, comentario):
    """Guarda la acción automáticamente"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    accion_guardada = {
        "fecha": timestamp,
        "accion": accion,
        "texto_seleccionado": texto_seleccionado,
        "comentario": comentario,
        "estado": "completado"
    }
    
    st.session_state.comentarios.append(accion_guardada)

def mostrar_historial_acciones():
    """Muestra el historial de acciones realizadas"""
    
    if st.session_state.comentarios:
        st.markdown("---")
        st.subheader("📋 Historial de Acciones")
        
        for i, accion in enumerate(reversed(st.session_state.comentarios), 1):
            with st.expander(f"{accion['accion']} - {accion['fecha']}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.metric("Acción", accion['accion'])
                    st.caption(f"Fecha: {accion['fecha']}")
                
                with col2:
                    st.write("**Texto seleccionado:**")
                    st.info(accion['texto_seleccionado'][:200] + "..." if len(accion['texto_seleccionado']) > 200 else accion['texto_seleccionado'])
                    
                    st.write("**Comentario:**")
                    st.success(accion['comentario'])

# Función principal
def main():
    st.set_page_config(
        page_title="Editor de Texto Interactivo",
        page_icon="📝",
        layout="wide"
    )
    
    st.title("📝 Editor de Texto Interactivo")
    st.markdown("---")
    
    # Texto de ejemplo
    texto_ejemplo = """
    La inteligencia artificial está transformando radicalmente la forma en que interactuamos 
    con la tecnología moderna. Desde asistentes virtuales inteligentes hasta sistemas 
    de recomendación avanzados, la IA se ha integrado en numerosas áreas de nuestra vida cotidiana. 
    
    El aprendizaje automático, una rama fundamental de la IA, permite a las computadoras 
    aprender automáticamente de los datos y mejorar continuamente su rendimiento sin necesidad 
    de ser programadas explícitamente para cada tarea específica.
    
    Esta revolución tecnológica está creando nuevas oportunidades y desafíos en diversos 
    sectores como healthcare, educación, finanzas y transporte.
    """
    
    # Opción para usar texto personalizado
    st.write("### 📋 Texto para revisar")
    texto_usuario = st.text_area(
        "Puedes editar este texto o usar el de ejemplo:",
        value=texto_ejemplo,
        height=150,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Instrucciones
    st.info("""
    **Instrucciones:**
    1. **Selecciona** texto en el área de lectura
    2. **Elige** una acción (Agregar, Eliminar, Modificar, Dudas)
    3. **Escribe** tu comentario - se guardará automáticamente
    4. **Revisa** el historial de acciones below
    """)
    
    # Componente principal
    texto_interactivo(texto_usuario)
    
    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Cómo funciona")
        st.markdown("""
        - **Selecciona texto** para habilitar las acciones
        - **Elige una opción** y escribe tu comentario
        - **Guardado automático** al escribir
        - **Historial visible** de todas las acciones
        
        **Opciones disponibles:**
        - 🟢 **Agregar**: Sugerir adiciones
        - 🔴 **Eliminar**: Proponer eliminaciones  
        - 🔵 **Modificar**: Recomendar cambios
        - 🟡 **Dudas**: Plantear preguntas
        """)
        
        # Estadísticas
        if st.session_state.comentarios:
            st.metric("Acciones realizadas", len(st.session_state.comentarios))

if __name__ == "__main__":
    main()