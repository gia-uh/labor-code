import os
import json
import streamlit as st
from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
from enum import Enum
import hashlib
from pydantic import BaseModel

load_dotenv()

st.session_state.bopened = None
st.session_state.btype = None


def load_json_files_from_directory(directory_path):
    json_dict = {}
    # Listar todos los ficheros en el directorio
    for filename in os.listdir(directory_path):
        # Comprobar que es un fichero JSON
        if filename.endswith(".json"):
            full_path = os.path.join(directory_path, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                name_without_extension = os.path.splitext(filename)[0]
                json_dict[name_without_extension] = content
    return json_dict


class Query(str, Enum):
    APPROVED = "APPROBADO"
    ERROR_NOT_FOUND = "ERROR_NO_ENCONTRADO"
    ERROR_PASSWORD = "ERROR_CONTRASEÑA"
    ERROR_SERVICE = "ERROR_SERVICIO"


class User(BaseModel):
    username: str
    pasw: str


# DEFAULT_PASSWORD = "38d406a798688f99c83852840952c276eb7635f7ea9024babcde8648b0c37e31"
DEFAULT_PASSWORD = st.secrets["user"]["default_password"]


def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_user(user: User):
    try:
        server = Server(st.secrets["ldap"]["address"], get_info=ALL)
        conn = Connection(
            server,
            f"cn={st.secrets["ldap"]["user"]},dc=uh,dc=cu",
            st.secrets["ldap"]["passwd"],
            auto_bind=True,
        )

        # 2. Buscar el DN del usuario
        search_filter = f"(uid={user.username})"  # Puede ser 'sAMAccountName', 'cn', etc. según tu LDAP
        conn.search(
            search_base="dc=uh,dc=cu",
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["*"],
        )

        if not conn.entries:
            return Query.ERROR_NOT_FOUND

        user_dn = conn.entries[0].entry_dn
        # 3. Intentar autenticar con las credenciales del usuario
        user_conn = Connection(server, user_dn, user.pasw, auto_bind=True)

        # Si llegamos aquí, la autenticación fue exitosa
        user_conn.unbind()
        return Query.APPROVED

    except Exception as e:
        if "invalidCredentials" in str(e):
            return Query.ERROR_PASSWORD
        else:
            return Query.ERROR_SERVICE
        
            

def login():
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Autenticarse")

        if submit:
            checking = check_user(User(username=username, pasw=password))
            if checking is Query.APPROVED or (
                username == st.secrets["user"]["default_user"]
                and hash_password(password) == DEFAULT_PASSWORD
            ):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            elif checking is Query.ERROR_NOT_FOUND:
                st.error("Invalid username")

            elif checking is Query.ERROR_PASSWORD:
                st.error("Invalid password")


def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
intro_page = st.Page("pages/intro.py", title="Inicio", icon=":material/home:")
ideas_page = st.Page("pages/ideas.py", title="Fundamentos", icon=":material/layers:")
question_page = st.Page("pages/questions.py", title="FAQs", icon=":material/help_outline:")
project_page = st.Page(
    "pages/project.py", title="Anteproyecto", icon=":material/menu_book:"
)
chat_page = st.Page("pages/chat.py", title="Asistente", icon=":material/chat_bubble:")
search_page = st.Page("pages/search.py", title="Buscar", icon=":material/search:")


# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Main app logic
if not st.session_state.logged_in:
    pg = st.navigation([login_page])
else:
    with st.spinner("Wait for it...", show_time=True):
        project = load_json_files_from_directory(st.secrets["dirs"]["project"]["law"])
        intro =  load_json_files_from_directory(st.secrets["dirs"]["project"]["intro"])
        st.session_state["project"] = project
        st.session_state["intro"] = intro
    pg = st.navigation(
        [intro_page, ideas_page, project_page, chat_page,question_page, search_page, logout_page]
        [
            intro_page,
            ideas_page,
            project_page,
            chat_page,
            search_page,
            logout_page,
            ]
    )

pg.run()
