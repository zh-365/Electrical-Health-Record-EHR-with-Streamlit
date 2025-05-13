import streamlit as st
import bcrypt
import mysql.connector
import _mysql_connector
from sqlalchemy import create_engine
from streamlit_option_menu import option_menu


left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image('pages/logo.png')


selected = option_menu(
    menu_title = None,
    options = ["Login", "Sign-Up"],
    menu_icon = "cast",
    default_index = 0,
    # orientation = "horizontal"
)

db_config = {
        'user': 'root',
        'password': 'zoelee2003',
        'host': 'localhost',
        'database': 'ehr'
    }

# Connect using mysql-connector-python
cnx = mysql.connector.connect(**db_config)

if selected == "Login":
    def check_credentials(username, password):
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT password FROM userprofile WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        cnx.close()

        if user:
            stored_password = user[0]
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        return False

    st.header("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type = "password")

    def is_authenticated():
        return 'logged_in' in st.session_state and st.session_state['logged_in']

    if st.button("Login"):
        if check_credentials(username, password):
            st.success("Login Success!")
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.switch_page("pages/Main Menu.py")
        else:
            st.error("Invalid username or password.")

if selected == "Sign-Up":
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def insert_userprofile(username, password, email, phoneNumber):
        hashed_password = hash_password(password)
        cursor = cnx.cursor()
        try:
            cursor.execute(
                "INSERT INTO userprofile(username, password, email, phoneNumber) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, email, phoneNumber)
            )
            cnx.commit()
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
        finally:
            cursor.close()
            cnx.close()

    st.header("Sign Up")

    username = st.text_input("Username")
    password = st.text_input("Password", type = "password")
    confirmPassword = st.text_input("Confirm Password", type = "password")
    email = st.text_input("E-mail")
    phoneNumber = st.text_input("Phone Number")

    if st.button("Sign Up"):
        if password == confirmPassword:
            insert_userprofile(username, password, email, phoneNumber)
            st.success("Registration Complete!")
        else:
            st.error("Passwords do not match.")
                 
    

