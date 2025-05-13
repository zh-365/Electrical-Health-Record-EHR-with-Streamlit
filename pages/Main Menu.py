import streamlit as st
import datetime
import bcrypt
import mysql.connector
import _mysql_connector
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np

with st.sidebar:
    selected = option_menu(
        menu_title = "App Features",
        options  = ["Main Dashboard", "Make an Appointment", "Chat Function", 
                    "Diagnosis Result & Prescription", "Pet Diagnosis", "Vaccination"],
    )

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.switch_page("App.py")

def is_authenticated():
        return 'logged_in' in st.session_state and st.session_state['logged_in']
    
# Connect to MySQL database
db_config = {
    'user': 'root',
    'password': 'zoelee2003',
    'host': 'localhost',
    'database': 'ehr'
}
cnx = mysql.connector.connect(**db_config)

# Main Dashboard
if selected == "Main Dashboard":
    query = "SELECT username FROM userprofile;"
    df = pd.read_sql(query, cnx)
    cnx.close()

    left_co, cent_co, last_co = st.columns(3)
    with cent_co:
        st.image('pages/logo.png')

    if is_authenticated():
        st.markdown(f"<h2 style='text-align: center;'>Welcome to ZooNO Disease, {st.session_state['username']}!</h2>"
                    , unsafe_allow_html=True)

    st.text("")
    st.text("")
    st.text("")

    st.subheader("Nearest Hospital from your Location")
    col1, col2, col3 = st.columns(3)

    col1.metric("General Hospital",
                    "Grey-Sloan Memorial Hospital",
                    "https://www.greysloan.com")    
    col2.metric("Veterinary Hospital",
                    "House Hospital",
                    "https://www.house.md.com")    
    col3.metric("Emergency Clinic",
                    "Chicago Hope",
                    "https://www.er.com")


# Make an Appointment
elif selected == "Make an Appointment":
    st.header('Book Offline Appointment')

    name = st.text_input("Name")
    email = st.text_input("Email")
    doctor_or_vet = st.selectbox("Would you like to consult a Doctor or Vet?", ["Doctor", "Vet"])

    if doctor_or_vet == "Doctor":
        def fetch_doctor():
            query = "SELECT CONCAT(doctorFullName,' (', schedule, ')') AS doctor_with_schedule FROM doctor;"
            df = pd.read_sql(query, cnx)
            #cnx.close()
            return df
        
        def insert_doctorAppointment(name, email, doctorName, dateOfAppointment, reason):
            cursor = cnx.cursor()
            try:
                cursor.execute(
                    "INSERT INTO appointment_doctor(Name, email, doctorName, dateOfAppointment, reason) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, doctorName, dateOfAppointment, reason)
                )
                cnx.commit()
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
            finally:
                cursor.close()
                cnx.close()
        
        doctor_df = fetch_doctor()
        doctor_list = doctor_df['doctor_with_schedule'].tolist()
        doctorName = st.selectbox("Choose a doctor", doctor_list)
        dateOfAppointment = st.date_input("Select a Date according to Availability")
        reason = st.text_input("Reason for Appointment:")

        if st.button("Submit"):
            if name and email:
                st.success("We will contact you through email about the appointment.")
                insert_doctorAppointment(name, email, doctorName, dateOfAppointment, reason)
            else:
                if not name:
                    st.error("Please enter your name.")
                if not email:
                    st.error("Please enter your email.")

    
    elif doctor_or_vet == "Vet":
        def fetch_vet():
            query1 = "SELECT CONCAT(vetFullName,' (', schedule, ')') AS vet_with_schedule FROM vet;"
            df = pd.read_sql(query1, cnx)
            #cnx.close()
            return df
        
        def insert_vetAppointment(name, email, vetName, dateOfAppointment, reason):
            cursor = cnx.cursor()
            try:
                cursor.execute(
                    "INSERT INTO appointment_vet(Name, email, vetName, dateOfAppointment, reason) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, vetName, dateOfAppointment, reason)
                )
                cnx.commit()
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
            finally:
                cursor.close()
                cnx.close()
        
        vet_df = fetch_vet()
        vet_list = vet_df['vet_with_schedule'].tolist()
        vetName = st.selectbox("Choose a vet", vet_list)
        dateOfAppointment = st.date_input("Select a Date according to Availability")
        reason = st.text_input("Reason for Appointment:")

        if st.button("Submit"):
            if name and email:
                st.success("We will contact you through email about the appointment.")
                insert_vetAppointment(name, email, vetName, dateOfAppointment, reason)
            else:
                if not name:
                    st.error("Please enter your name.")
                if not email:
                    st.error("Please enter your email.")


    
# Chat Function
elif selected == "Chat Function":
    st.title("ZooNO Disease Chat Room")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # React to user input
    if prompt := st.chat_input("Enter message"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
    response = f"{prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

elif selected == "Diagnosis Result & Prescription":
    st.title("Medical Report")

    def get_patient_id(username):
        query1 = "SELECT patientID FROM userprofile WHERE username = %s"
        df = pd.read_sql(query1, cnx, params = [username])
        if not df.empty:
            return df.iloc[0]['patientID']
        return None

    def get_patient_name(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query2 = "SELECT patientFullName from patient WHERE patientID = %s"
        df = pd.read_sql(query2, cnx, params = [patient_id])
        if not df.empty:
            return df.iloc[0]['patientFullName']
        return "Unknown"
    
    def get_doctor_name(username):
        query3 = "SELECT d.doctorFullName FROM diagnosis2 AS diag INNER JOIN doctor AS d ON diag.doctorid = d.doctorid INNER JOIN userprofile AS u ON diag.patientID = u.patientID WHERE u.username = %s"
        df = pd.read_sql(query3, cnx, params = [username])
        if not df.empty:
            return df.iloc[0]['doctorFullName']
        return "Unknown"
    
    def get_patient_info(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query4 = "SELECT TIMESTAMPDIFF(YEAR, dateofBirth, CURDATE()) AS age, gender, medicalHistory FROM patient WHERE patientID = %s"
        df = pd.read_sql(query4, cnx, params = [patient_id])
        return df
    
    def get_diagnosis_details(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query5 = "SELECT dateofDiagnosis, symptoms, animalContact, typeOfAnimal FROM diagnosis2 WHERE patientID = %s"
        df = pd.read_sql(query5, cnx, params = [patient_id])
        return df
    
    def get_disease_description(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query6 = "SELECT d.name, d.description, d.symptoms, d.treatment FROM patientdisease AS pd INNER JOIN disease AS d ON pd.diseaseID = d.diseaseID INNER JOIN userprofile AS u ON pd.patientID = u.patientID WHERE u.patientID = %s"
        df = pd.read_sql(query6, cnx, params = [patient_id])
        return df
    
    def get_prescription(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query7 = "SELECT p.medication, p.dosage, p.frequency, p.startDate, p.endDate FROM ehr AS e INNER JOIN prescription AS p ON e.prescriptionID = p.prescriptionID INNER JOIN userprofile AS u ON e.patientID = u.patientID WHERE u.patientID = %s;"
        df = pd.read_sql(query7, cnx, params = [patient_id])
        return df

    patient_id = get_patient_id(st.session_state['username'])
    patient_name = get_patient_name(patient_id)
    doctor_name = get_doctor_name(st.session_state['username'])
    patient_info = get_patient_info(patient_id)
    diagnosis_detail = get_diagnosis_details(patient_id)
    disease_description = get_disease_description(patient_id)
    prescription_details = get_prescription(patient_id)

    st.text("")
    st.text("")
    st.text("")
    st.text(f"Patient Name: {patient_name}")
    st.text(f"Diagnosis By: {doctor_name}")
    st.text("")
    st.subheader("Patient Information")
    st.table(patient_info)
    st.text("")
    st.subheader("Summary of Diagnosis")
    st.table(diagnosis_detail)
    st.subheader("Disease Description & Available Treatments")
    st.table(disease_description)
    st.subheader("Prescription Details")
    st.table(prescription_details)

elif selected == "Pet Diagnosis":
    st.title("Pet Medical Record")

    def get_patient_id(username):
        query1 = "SELECT patientID FROM userprofile WHERE username = %s"
        df = pd.read_sql(query1, cnx, params = [username])
        if not df.empty:
            return df.iloc[0]['patientID']
        return None
    
    def get_owner_name(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query2 = "SELECT patientFullName from patient WHERE patientID = %s"
        df = pd.read_sql(query2, cnx, params = [patient_id])
        if not df.empty:
            return df.iloc[0]['patientFullName']
        return "Unknown"
    
    def get_vet_name(username):
        query3 = "SELECT v.vetFullName FROM petdiagnosis AS pd INNER JOIN vet AS v ON pd.vetid = v.vetid INNER JOIN pet AS p ON pd.petID = p. petID INNER JOIN userprofile AS u ON p.patientID = u.patientID WHERE u.username = %s"
        df = pd.read_sql(query3, cnx, params = [username])
        if not df.empty:
            return df.iloc[0]['vetFullName']
        return "Unknown"
    
    def get_pet_info(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query4 = "SELECT nameofPet, age, gender, species FROM pet WHERE patientID = %s"
        df = pd.read_sql(query4, cnx, params = [patient_id])
        return df
    
    def get_diagnosis_details(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query5 = "SELECT p.nameofPet, pd.dateofDiagnosis, pd.symptoms FROM pet AS p INNER JOIN petdiagnosis AS pd ON p.petID = pd.petID WHERE patientID = %s"
        df = pd.read_sql(query5, cnx, params = [patient_id])
        return df
    
    def get_disease_description(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query6 = "SELECT d.name, d.description, d.symptoms, d.treatment, pd.prescription FROM petdiagnosis as pd INNER JOIN disease as d ON d.diseaseID = pd.diseaseID INNER JOIN pet as p ON p.petID = pd.petID INNER JOIN userprofile AS u ON p.patientID = u.patientID WHERE u.patientID = %s"
        df = pd.read_sql(query6, cnx, params = [patient_id])
        return df

    patient_id = get_patient_id(st.session_state['username'])
    owner_name = get_owner_name(patient_id)
    vet_name = get_vet_name(st.session_state['username'])
    patient_info = get_pet_info(patient_id)
    diagnosis_detail = get_diagnosis_details(patient_id)
    disease_description = get_disease_description(patient_id)

    st.text("")
    st.text("")
    st.text("")
    st.text(f"Owner: {owner_name}")
    st.text(f"Diagnosis By: {vet_name}")
    st.text("")
    st.subheader("Pet Information")
    st.table(patient_info)
    st.text("")
    st.subheader("Summary of Diagnosis")
    st.table(diagnosis_detail)
    st.subheader("Disease Description & Prescriptions")
    st.table(disease_description)

elif selected == "Vaccination":
    st.title("Vaccination Table")

    def get_patient_id(username):
        query1 = "SELECT patientID FROM userprofile WHERE username = %s"
        df = pd.read_sql(query1, cnx, params = [username])
        if not df.empty:
            return df.iloc[0]['patientID']
        return None
    
    def get_patient_name(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query2 = "SELECT patientFullName from patient WHERE patientID = %s"
        df = pd.read_sql(query2, cnx, params = [patient_id])
        if not df.empty:
            return df.iloc[0]['patientFullName']
        return "Unknown"
    
    def get_patient_vaccination(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query3 = "SELECT hv.rabies, hv.yellowfever, hv.japaneseencephalitis, hv.anthrax, hv.qfever, hv.tickborneencephalitis, hv.plague, hv.hantavirus FROM userprofile AS u INNER JOIN humanvaccination AS hv ON u.patientID = hv.patientID WHERE u.patientID = %s"
        df = pd.read_sql(query3, cnx, params = [patient_id])
        return df
    
    def get_pet_vaccination(patient_id):
        patient_id = int(patient_id) if isinstance(patient_id, (np.integer, np.int64)) else patient_id
        query4 = "SELECT p.nameofPet, pv.Rabies, pv.Leptospirosis, pv.LymeDisease, pv.FeLV, pv.FIV, pv.Giardia FROM pet AS p INNER JOIN petvaccination AS pv ON p.petID = pv.petID INNER JOIN userprofile AS u ON u.patientID = p.patientID WHERE u.patientID = %s"
        df = pd.read_sql(query4, cnx, params = [patient_id])
        return df
    
    patient_id = get_patient_id(st.session_state['username'])
    patient_name = get_patient_name(patient_id)
    vaccination_detail = get_patient_vaccination(patient_id)
    pet_vaccination = get_pet_vaccination(patient_id)

    st.subheader(f"Patient Name: {patient_name}")
    st.table(vaccination_detail)
    st.text("")
    st.text("")
    st.text("")
    if pet_vaccination is not None and not pet_vaccination.empty:
        st.subheader("Pet Vaccination Status")
        st.table(pet_vaccination)
    else:
        st.write("No vaccination information available for any pet.")
    



