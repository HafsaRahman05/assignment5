import streamlit as st
from cryptography.fernet import Fernet
import hashlib

# Constants
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# In-memory storage
stored_data = {}
failed_attempts = {}
session_auth = {"authorized": True}

# Fernet Key (session-based)
if "fernet_key" not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()

fernet = Fernet(st.session_state.fernet_key)

# Utility: Hash passkey using SHA-256
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

# Insert new data
def insert_data(user_id, text, passkey):
    encrypted_text = fernet.encrypt(text.encode()).decode()
    hashed_passkey = hash_passkey(passkey)
    stored_data[user_id] = {"encrypted_text": encrypted_text, "passkey": hashed_passkey}
    st.success(f"✅ Data securely stored for **User ID:** `{user_id}`")

# Retrieve existing data
def retrieve_data(user_id, passkey):
    if user_id not in stored_data:
        st.error("❌ No data found for this User ID.")
        return

    # Check for lockout
    if failed_attempts.get(user_id, 0) >= 3:
        session_auth["authorized"] = False
        st.warning("⚠️ Too many failed attempts. Redirecting to login page.")
        st.experimental_rerun()
        return

    hashed_input = hash_passkey(passkey)
    if hashed_input == stored_data[user_id]["passkey"]:
        decrypted_text = fernet.decrypt(stored_data[user_id]["encrypted_text"].encode()).decode()
        st.success(f"🔓 Decrypted Data: `{decrypted_text}`")
        failed_attempts[user_id] = 0  # Reset attempts on success
    else:
        failed_attempts[user_id] = failed_attempts.get(user_id, 0) + 1
        attempts_left = 3 - failed_attempts[user_id]
        st.error(f"❌ Incorrect passkey. **Attempts left:** {attempts_left}")

# Admin Login Page
def login_page():
    st.title("🔐 Admin Reauthorization")
    username = st.text_input("👤 Admin Username")
    password = st.text_input("🔑 Admin Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session_auth["authorized"] = True
            failed_attempts.clear()
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid credentials. Try again.")

# Home Page
def home_page():
    st.title("🔒 Secure Data Encryption System")
    st.write("Use the sidebar to navigate through options.")
    st.info("This app allows you to securely **store** and **retrieve** encrypted data protected by a custom passkey.")

# Insert Data Page
def insert_page():
    st.title("📥 Store Secure Data")
    user_id = st.text_input("🆔 Enter User ID")
    data = st.text_area("📝 Enter Data to Encrypt")
    passkey = st.text_input("🔑 Set a Passkey", type="password")

    if st.button("🔒 Store Data"):
        if user_id and data and passkey:
            insert_data(user_id, data, passkey)
        else:
            st.warning("⚠️ All fields are required.")

# Retrieve Data Page
def retrieve_page():
    st.title("📤 Retrieve Encrypted Data")
    user_id = st.text_input("🆔 Enter User ID")
    passkey = st.text_input("🔑 Enter Your Passkey", type="password")

    if st.button("🔓 Decrypt Data"):
        if user_id and passkey:
            retrieve_data(user_id, passkey)
        else:
            st.warning("⚠️ Both fields are required.")

# Optional: View Encrypted Data (Admin Debugging)
def view_encrypted_data_page():
    st.title("🗂️ Stored Encrypted Data (Admin View)")
    if stored_data:
        st.json(stored_data)
    else:
        st.info("ℹ️ No data stored yet.")

# Main App Routing
def main():
    if not session_auth.get("authorized", True):
        login_page()
        return

    st.sidebar.title("🔐 Secure Data Storage")
    menu = st.sidebar.radio("📋 Menu", ["Home", "Insert Data", "Retrieve Data", "Login", "View Encrypted Data"])

    if menu == "Home":
        home_page()
    elif menu == "Insert Data":
        insert_page()
    elif menu == "Retrieve Data":
        retrieve_page()
    elif menu == "Login":
        login_page()
    elif menu == "View Encrypted Data":
        view_encrypted_data_page()

# Run the app
if __name__ == "__main__":
    main()
