import json
import os
from pathlib import Path

# Crear directorio de datos
os.makedirs("data", exist_ok=True)

# Áreas disponibles basadas en dominios
AREAS_DOMAINS = {
    "ac": "AREA CENTRAL",
    "lex": "FACULTAD DE DERECHO",
    "fec": "FACULTAD DE ECONOMIA", 
    "fisica": "FACULTAD DE FISICA",
    "matcom": "FACULTAD DE MATEMATICA Y COMPUTACION",
    "psico": "FACULTAD DE PSICOLOGIA",
    "fcom": "FACULTAD DE COMUNICACION",
    "fbio": "FACULTAD DE BIOLOGIA",
    "rect": "DIRECCIÓN DE INFRAESTRUCTURA"
}

# Nombres y apellidos para generar usuarios realistas
NOMBRES = ["ALEJANDRO", "MARIA", "CARLOS", "LAURA", "JORGE", "ANA", "ROBERTO", "ELENA"]
APELLIDOS = ["GARCIA", "RODRIGUEZ", "MARTINEZ", "LOPEZ", "HERNANDEZ", "GONZALEZ", "PEREZ", "SANCHEZ"]

# Títulos/cargos posibles
TITULOS = [
    "RECIEN GRADUADO EN ADIESTRAMIENTO - NS",
    "PROFESOR TITULAR",
    "INVESTIGADOR PRINCIPAL", 
    "ESPECIALISTA EN LEGISLACIÓN",
    "ANALISTA JURÍDICO",
    "CONSULTOR EXTERNO",
    "ESTUDIANTE DE MAESTRIA",
    "DOCTOR EN DERECHO"
]

# Textos de ejemplo para interacciones
ADDITIONS = [
    "Considero necesario añadir un párrafo sobre protección ambiental\n",
    "Propongo incluir referencia a los derechos humanos internacionales\n",
    "Sugiero agregar un mecanismo de seguimiento y evaluación\n",
    "Recomiendo añadir disposiciones sobre transparencia\n",
    "Sería importante incluir sanciones específicas para el incumplimiento\n"
]

DELETIONS = [
    "Este párrafo resulta redundante con el artículo anterior\n",
    "La redacción es muy ambigua y debería eliminarse\n",
    "Propongo eliminar por considerar que limita derechos fundamentales\n",
    "Este contenido está duplicado en otra sección de la ley\n"
]

MODIFICATIONS = [
    "Recomiendo cambiar 'podrá' por 'deberá' para mayor obligatoriedad\n",
    "Sugiero modificar el plazo de 30 a 60 días hábiles\n",
    "Propongo reestructurar la redacción para mayor claridad conceptual\n",
    "Considero necesario especificar las excepciones aplicables\n"
]

QUESTIONS = [
    "¿Cuál es el fundamento legal de este párrafo?\n",
    "¿Cómo se aplicaría este artículo en la práctica cotidiana?\n",
    "¿Existe jurisprudencia relacionada con este contenido?\n",
    "¿Qué recursos están disponibles para cumplir esta disposición?\n"
]

def generar_usuario(area_domain, nombre, apellido, titulo):
    """
    Genera datos de usuario con interacciones distribuidas en diferentes párrafos
    """
    usuario = {
        "Nombre": nombre,
        "Apellidos": apellido,
        "Area": AREAS_DOMAINS[area_domain],
        "Title": titulo
    }
    
    # Distribuir párrafos según el área (simulando intereses diferentes)
    if area_domain == "lex":
        # Facultad de Derecho - interacciones en artículos legales clave
        parrafos = [1, 2, 5, 9, 15, 25, 30, 45, 60, 75]
    elif area_domain == "fec":
        # Economía - artículos relacionados con recursos y presupuestos
        parrafos = [10, 20, 35, 50, 65, 80, 95, 110]
    elif area_domain == "matcom":
        # Matemáticas - artículos técnicos y de implementación
        parrafos = [3, 8, 18, 28, 40, 55, 70, 85]
    elif area_domain == "rect":
        # Infraestructura - artículos operativos
        parrafos = [4, 12, 22, 33, 44, 66, 88, 99]
    else:
        # Áreas generales - distribución aleatoria
        parrafos = [6, 14, 26, 39, 52, 68, 81, 97]
    
    for parrafo in parrafos:
        usuario[str(parrafo)] = {
            "additions": [ADDITIONS[parrafo % len(ADDITIONS)]] if parrafo % 4 == 0 else [],
            "deletions": [DELETIONS[parrafo % len(DELETIONS)]] if parrafo % 5 == 0 else [],
            "modifications": [MODIFICATIONS[parrafo % len(MODIFICATIONS)]] if parrafo % 3 == 0 else [],
            "questions": [QUESTIONS[parrafo % len(QUESTIONS)]] if parrafo % 6 == 0 else []
        }
    
    return usuario

def crear_archivos_prueba():
    """
    Crea múltiples archivos JSON de prueba organizados por áreas
    """
    
    # Configuración de usuarios por área
    config_usuarios = {
        "ac": [
            ("admin@uh.cu", "ADMINISTRADOR", "SISTEMA", "COORDINADOR GENERAL")
        ],
        "lex": [
            ("profesor.derecho@lex.uh.cu", "CARLOS", "MARTINEZ LOPEZ", "PROFESOR TITULAR"),
            ("abogado@lex.uh.cu", "ANA", "RODRIGUEZ GARCIA", "ESPECIALISTA EN LEGISLACIÓN"),
            ("estudiante@estudiantes.lex.uh.cu", "JORGE", "HERNANDEZ PEREZ", "ESTUDIANTE DE MAESTRIA")
        ],
        "fec": [
            ("economista@fec.uh.cu", "ROBERTO", "GONZALEZ SANCHEZ", "ANALISTA JURÍDICO"),
            ("contador@fec.uh.cu", "ELENA", "LOPEZ MARTINEZ", "CONSULTOR EXTERNO")
        ],
        "matcom": [
            ("programador@matcom.uh.cu", "LAURA", "GARCIA RODRIGUEZ", "ESPECIALISTA EN LEGISLACIÓN"),
            ("datascientist@estudiantes.matcom.uh.cu", "MARIA", "PEREZ HERNANDEZ", "RECIEN GRADUADO EN ADIESTRAMIENTO - NS")
        ],
        "psico": [
            ("psicologo@psico.uh.cu", "ALEJANDRO", "SANCHEZ GONZALEZ", "DOCTOR EN DERECHO")
        ],
        "fcom": [
            ("comunicador@fcom.uh.cu", "CARLOS", "HERNANDEZ GARCIA", "INVESTIGADOR PRINCIPAL")
        ],
        "fbio": [
            ("biologo@fbio.uh.cu", "ANA", "MARTINEZ LOPEZ", "PROFESOR TITULAR")
        ],
        "rect": [
            ("tecnico@rect.uh.cu", "ALEJANDRO", "BELTRAN VARELA", "RECIEN GRADUADO EN ADIESTRAMIENTO - NS"),
            ("ingeniero@rect.uh.cu", "ROBERTO", "VARELA BELTRAN", "ESPECIALISTA EN LEGISLACIÓN")
        ]
    }
    
    total_archivos = 0
    
    for area_domain, usuarios in config_usuarios.items():
        # Crear directorio del área
        area_dir = Path(f"data/{area_domain}")
        area_dir.mkdir(exist_ok=True)
        
        for email, nombre, apellidos, titulo in usuarios:
            # Generar datos del usuario
            datos_usuario = generar_usuario(area_domain, nombre, apellidos, titulo)
            
            # Guardar archivo JSON
            archivo_path = area_dir / f"{email}.json"
            with open(archivo_path, 'w', encoding='utf-8') as f:
                json.dump(datos_usuario, f, indent=4, ensure_ascii=False)
            
            total_archivos += 1
            print(f"✅ Creado: {archivo_path}")
    
    return total_archivos

def crear_casos_especificos_prueba():
    """
    Crea casos de prueba específicos para probar filtros particulares
    """
    
    # Caso 1: Usuario con muchas interacciones en LIBRO PRIMERO
    usuario_libro1 = {
        "Nombre": "MARTIN",
        "Apellidos": "JIMENEZ ORTIZ",
        "Area": "FACULTAD DE DERECHO",
        "Title": "DOCTOR EN DERECHO",
        "1": {
            "additions": ["Propongo añadir referencia explícita a derechos humanos internacionales\n"],
            "deletions": [],
            "modifications": ["Recomiendo cambiar 'derecho' por 'facultad' en todo el texto\n"],
            "questions": ["¿Cuál es el alcance exacto de este artículo?\n"]
        },
        "2": {
            "additions": [],
            "deletions": ["Considero que este párrafo debe eliminarse por redundancia\n"],
            "modifications": [],
            "questions": []
        },
        "3": {
            "additions": ["Añadir mecanismo de apelación automática\n"],
            "deletions": [],
            "modifications": ["Modificar plazos de 15 a 30 días naturales\n"],
            "questions": ["¿Existe jurisprudencia constitucional al respecto?\n"]
        },
        "4": {
            "additions": [],
            "deletions": [],
            "modifications": ["Cambiar redacción para mayor claridad conceptual\n"],
            "questions": []
        },
        "5": {
            "additions": ["Incluir referencia a tratados internacionales ratificados\n"],
            "deletions": ["Eliminar por contradicción con normativa superior\n"],
            "modifications": [],
            "questions": ["¿Cómo se articula con la ley orgánica?\n"]
        }
    }
    
    # Caso 2: Usuario enfocado en DISPOSICIONES
    usuario_disposiciones = {
        "Nombre": "SUSANA",
        "Apellidos": "RAMIREZ CASTRO", 
        "Area": "FACULTAD DE ECONOMIA",
        "Title": "ANALISTA JURÍDICO",
        "41": {
            "additions": ["Añadir disposición sobre implementación gradual por fases\n"],
            "deletions": [],
            "modifications": [],
            "questions": ["¿Cuál es el cronograma de aplicación específico?\n"]
        },
        "42": {
            "additions": [],
            "deletions": ["Eliminar por falta de asignación presupuestaria\n"],
            "modifications": [],
            "questions": []
        },
        "46": {
            "additions": ["Incluir transición especial para casos en trámite\n"],
            "deletions": [],
            "modifications": ["Extender plazo transitorio a 180 días hábiles\n"],
            "questions": ["¿Cómo afecta esta disposición a los procesos actuales?\n"]
        },
        "50": {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "questions": ["¿Cuándo entra en vigor exactamente esta disposición final?\n"]
        }
    }
    
    # Caso 3: Usuario técnico con muchas modificaciones
    usuario_tecnico = {
        "Nombre": "DIEGO",
        "Apellidos": "TORRES MOLINA",
        "Area": "FACULTAD DE MATEMATICA Y COMPUTACION", 
        "Title": "ESPECIALISTA EN LEGISLACIÓN",
        "17": {
            "additions": [],
            "deletions": [],
            "modifications": ["Precisar términos técnicos sobre protección de datos\n"],
            "questions": ["¿Se incluye específicamente la protección de datos personales?\n"]
        },
        "18": {
            "additions": ["Añadir referencia a estándares internacionales ISO\n"],
            "deletions": [],
            "modifications": ["Especificar formatos de almacenamiento requeridos\n"],
            "questions": []
        },
        "25": {
            "additions": [],
            "deletions": ["Eliminar por ambigüedad técnica peligrosa\n"],
            "modifications": ["Corregir terminología informática obsoleta\n"],
            "questions": ["¿Qué normativa técnica específica aplica aquí?\n"]
        },
        "33": {
            "additions": ["Incluir requisitos de seguridad informática\n"],
            "deletions": [],
            "modifications": ["Modificar especificaciones técnicas\n"],
            "questions": ["¿Existen estándares nacionales para esto?\n"]
        }
    }
    
    # Caso 4: Usuario original proporcionado (para referencia)
    usuario_original = {
        "Nombre": "ALEJANDRO",
        "Apellidos": "BELTRAN VARELA", 
        "Area": "DIRECCIÓN DE INFRAESTRUCTURA",
        "Title": "RECIEN GRADUADO EN ADIESTRAMIENTO - NS",
        "9": {
            "additions": ["Esto es una prueba de adicion\n"],
            "deletions": [],
            "modifications": [],
            "questions": []
        },
        "10": {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "questions": ["Pregunta basica\n"]
        },
        "199": {
            "additions": ["Pruena Libro Segundo  Titulo 1 Articulo 26\n"],
            "deletions": [],
            "modifications": [],
            "questions": []
        },
        "200": {
            "additions": ["Segunda prueba de l dia\n"],
            "deletions": [],
            "modifications": [],
            "questions": []
        }
    }
    
    # Guardar casos específicos
    casos_especificos = [
        ("lex/especialista_libro1@lex.uh.cu.json", usuario_libro1),
        ("fec/especialista_disposiciones@fec.uh.cu.json", usuario_disposiciones),
        ("matcom/tecnico_avanzado@matcom.uh.cu.json", usuario_tecnico),
        ("rect/original@rect.uh.cu.json", usuario_original)
    ]
    
    for archivo_path, datos in casos_especificos:
        full_path = Path(f"data/{archivo_path}")
        full_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        
        print(f"🔍 Caso específico creado: {full_path}")

if __name__ == "__main__":
    print("🧪 Generando archivos JSON de prueba...")
    
    # Crear archivos principales
    total = crear_archivos_prueba()
    
    # Crear casos específicos
    crear_casos_especificos_prueba()
    
    print(f"\n🎉 Generación completada!")
    print(f"📁 Total de archivos creados: {total + 4}")
    print(f"📊 Áreas cubiertas: {len(AREAS_DOMAINS)}")
    print(f"👥 Usuarios de prueba: {total + 4}")
    print("\n📋 Estructura creada:")
    for area in AREAS_DOMAINS:
        area_dir = Path(f"data/{area}")
        if area_dir.exists():
            archivos = list(area_dir.glob("*.json"))
            print(f"   📂 {area}/ -> {len(archivos)} archivos")