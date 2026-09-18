import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="UCL Electrical Competence App", layout="centered")

# --- Mock Database Initialization ---
# In a real app deployed on GitHub, you'd replace this with a connection to a database (e.g., Supabase, Firebase, or a private GitHub Gist)
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"inducted": True, "tier": "CAT III"},
        "student1": {"inducted": False, "tier": "Pending"}
    }
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

# --- Mock Document Database ---
doc_db = pd.DataFrame({
    "Tag/QR": ["RIG-001", "BATT-02", "SOP-01", "POL-01"],
    "Title": ["Dynamometer Test Bed", "Li-Ion Pack Assembly", "H07RN-F Glanding", "UCL Corporate Policy"],
    "Category": ["CAT II", "CAT II", "CAT I", "Policy"],
    "PI / Owner": ["Pouya Kolahian", "Mark Buckwell", "Joe Barwick", "Pouya Kolahian"],
    "Last Zs Test": ["0.45 Ohms (Pass)", "N/A", "N/A", "N/A"],
    "Status": ["Active", "Maintenance", "Active", "Active"]
})

# --- Helper Functions ---
def login(username):
    if username == "":
        st.warning("Please enter a valid UCL ID or Username.")
        return
    
    if username not in st.session_state.user_db:
        # Create a new user profile needing induction
        st.session_state.user_db[username] = {"inducted": False, "tier": "Pending"}
    
    st.session_state.logged_in_user = username

def logout():
    st.session_state.logged_in_user = None

def pass_induction():
    st.session_state.user_db[st.session_state.logged_in_user]["inducted"] = True
    st.session_state.user_db[st.session_state.logged_in_user]["tier"] = "CAT I"
    st.success("Induction passed! You are now a CAT I Standard Operative.")
    st.rerun()

# --- Main App Logic ---
st.title("⚡ UCL Electrical Competence Group")

# 1. LOGIN SCREEN
if st.session_state.logged_in_user is None:
    st.subheader("Welcome to the ESPER Portal")
    st.write("Please log in with your UCL credentials to access lab information or complete your Day 1 Induction.")
    
    with st.form("login_form"):
        username_input = st.text_input("Username (e.g., student1, admin):").strip().lower()
        submit_button = st.form_submit_button("Log In")
        
        if submit_button:
            login(username_input)
            st.rerun()

# 2. ROUTING ONCE LOGGED IN
else:
    current_user = st.session_state.logged_in_user
    user_data = st.session_state.user_db[current_user]
    
    st.sidebar.write(f"**Logged in as:** {current_user}")
    st.sidebar.write(f"**Competency Tier:** {user_data['tier']}")
    if st.sidebar.button("Log Out"):
        logout()
        st.rerun()

    # Flow A: User Needs Induction (First Time)
    if not user_data["inducted"]:
        st.header("Day 1 Basic Electrical Induction")
        st.warning("You must complete this basic training and pass the quiz before accessing the lab or searching documents.")
        
        # Training Content
        st.write("""
        ### Section 1: The Competency Framework
        UCL uses the ESPER framework. As a new user, you will start as a **CAT I Standard Operative**. This allows you to use standard, off-the-shelf equipment (plugged into a standard 13A socket). You may not build or modify bespoke circuits.
        
        ### Section 2: Voltage Limits & Batteries
        Standard low voltage exemptions apply to current-limited sources below **50V AC or 120V DC**. However, **batteries are never exempt** due to the severe risk of high short-circuit currents and thermal runaway.
        
        ### Section 3: The Two-Person Rule
        For any complex, energized Category II testing, a second person must be present and trained to operate the Emergency Power Off (EPO) button.
        """)
        
        st.divider()
        
        # Induction Quiz
        st.subheader("Induction Quiz")
        with st.form("quiz_form"):
            q1 = st.radio("1. What is your starting competency tier?", ["CAT III (Specialist)", "CAT II (Advanced)", "CAT I (Standard)"])
            q2 = st.radio("2. Are bare lithium-ion batteries exempt from Category II rules if they are under 50V?", ["Yes, they are safe.", "No, they carry high short-circuit risks."])
            q3 = st.radio("3. Can you do energized CAT II testing alone?", ["Yes, if you are careful.", "No, the Two-Person Rule applies."])
            
            submit_quiz = st.form_submit_button("Submit Quiz")
            
            if submit_quiz:
                if q1 == "CAT I (Standard)" and q2 == "No, they carry high short-circuit risks." and q3 == "No, the Two-Person Rule applies.":
                    pass_induction()
                else:
                    st.error("One or more answers are incorrect. Please review the training material and try again.")

    # Flow B: User is Inducted (Search & Dashboard)
    else:
        st.header("Lab Information & Document Search")
        st.success(f"Welcome back. You are cleared for {user_data['tier']} operations.")
        
        st.write("Enter a document name, equipment QR code (e.g., RIG-001), or PI name to retrieve active permits and safety data.")
        
        # Search Bar
        search_query = st.text_input("🔍 Search Database:", "")
        
        if search_query:
            # Filter the dataframe based on the search query
            results = doc_db[doc_db.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
            
            if not results.empty:
                st.write(f"**Found {len(results)} matching records:**")
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.warning("No documents or equipment found matching that query.")
                
        st.divider()
        st.subheader("Quick Links")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 Submit New Permit to Energise")
            st.button("⚙️ Log Maintenance Activity")
        with col2:
            st.button("🚨 Emergency Isolation Protocols", type="primary")
