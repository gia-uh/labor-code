import os
import streamlit as st 
from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
from enum import Enum
import hashlib
from pydantic import BaseModel
load_dotenv()


class Consulta(str, Enum):
    APROBADO = "APROBADO"
    ERROR_NO_ENCONTRADO = "ERROR_NO_ENCONTRADO"
    ERROR_CONTRASEÑA = "ERROR_CONTRASEÑA"
    ERROR_SERVICIO = "ERROR_SERVICIO"

class User(BaseModel):
    username: str
    pasw: str

DEFAULT_PASSWORD = "38d406a798688f99c83852840952c276eb7635f7ea9024babcde8648b0c37e31"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_user(user:User):
    try:  
        server = Server(os.getenv("LDAP_ADDRESS",""), get_info=ALL)
        conn = Connection(
            server, 
            f"cn={os.getenv("LDAP_USER")},dc=uh,dc=cu", 
            os.getenv("LDAP_PASSWORD"), 
            auto_bind=True
        )
        
        # 2. Buscar el DN del usuario
        search_filter = f"(uid={user.username})"  # Puede ser 'sAMAccountName', 'cn', etc. según tu LDAP
        conn.search(search_base="dc=uh,dc=cu", 
                   search_filter=search_filter, 
                   search_scope=SUBTREE,
                   attributes=['*'])
        
        if not conn.entries:
            return  Consulta.ERROR_NO_ENCONTRADO
            
        user_dn = conn.entries[0].entry_dn
        # 3. Intentar autenticar con las credenciales del usuario
        user_conn = Connection(server, user_dn, user.pasw, auto_bind=True)

        # Si llegamos aquí, la autenticación fue exitosa
        user_conn.unbind()
        return Consulta.APROBADO
        
    except Exception as e:
        if "invalidCredentials" in str(e):
            return Consulta.ERROR_CONTRASEÑA
        else:
            return Consulta.ERROR_SERVICIO
        
            

def login():
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            checking = check_user(User(username=username,pasw=password))
            if checking is Consulta.APROBADO or (username =="gia-uh" and hash_password(password) ==DEFAULT_PASSWORD):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            elif checking is Consulta.ERROR_NO_ENCONTRADO:
                st.error("Invalid username")
            
            elif checking is Consulta.ERROR_CONTRASEÑA:
                st.error("Invalid password")

def logout():
    """Logout function"""
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

def main_app():
    """Main application after login"""
    st.title(f"Welcome, {st.session_state.username}!")
    
    
    logout()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Main app logic
if not st.session_state.logged_in:
    login()
else:
    main_app()