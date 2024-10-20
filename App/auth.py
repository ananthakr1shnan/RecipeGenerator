import hashlib
import chromadb
import streamlit as st
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Initialize ChromaDB client (local persistent client)
client = chromadb.PersistentClient(path="./chroma_db")

# Create or get the collection for user data
user_collection = client.get_or_create_collection("user_data")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username, email, password):
    hashed_password = hash_password(password)
    user_collection.add(
        documents=[hashed_password],
        metadatas=[{"username": username, "email": email}],
        ids=[username],
    )


def authenticate_user(username, password):
    results = user_collection.get(where={"username": username}, ids=[username])
    if results["documents"]:
        stored_password = results["documents"][0]
        return stored_password == hash_password(password)
    return False


def get_user_email(username):
    results = user_collection.get(where={"username": username}, ids=[username])
    if results["metadatas"]:
        return results["metadatas"][0].get("email")
    return None


def send_email(subject, body, to_email):
    from_email = os.getenv("SENDER_EMAIL")  # Sender's email address
    password = os.getenv("EMAIL_PASSWORD")  # Sender's email password

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)  # For Gmail
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
    finally:
        server.quit()


def login_signup_page():
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.username is not None:
        return

    st.title("Login/Signup Page")

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login Section")

        username = st.text_input("User Name")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.username = username
                st.success(f"Logged In as {username}")
                st.experimental_set_query_params(reload=True)
            else:
                st.error("Incorrect Username/Password")

    elif choice == "Sign Up":
        st.subheader("Create New Account")

        new_username = st.text_input("User Name")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            create_user(new_username, new_email, new_password)
            st.success("You have successfully created an account")
            st.info("Go to Login Menu to login")
