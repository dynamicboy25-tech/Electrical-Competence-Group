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
        
        # --- ENHANCED TRAINING CONTENT ---
        st.markdown("### 📚 Module 1: The Regulatory Framework")
        st.write("""
        Electrical work at UCL is governed by strict UK laws, primarily the **Electricity at Work Regulations 1989 (EAWR)** and **PUWER 1998**. These laws mandate that all equipment must be safe, suitable for its intended environment, and operated only by competent individuals. Top-down management applies here: your Principal Investigator (PI) is strictly accountable for ensuring you operate only within your authorized tier.
        """)
        
        st.markdown("### 🧑‍🔧 Module 2: The ESPER Competency Framework")
        st.info("""
        UCL uses the **Electrically Skilled Persons Register (ESPER)** to categorize what work you are legally allowed to perform.
        * **CAT I (Standard Operative):** This is your starting tier. You are authorized to use standard, off-the-shelf, CE-marked equipment plugged into standard 13A sockets. **You may NOT build, open, or modify bespoke circuits.**
        * **CAT II (Advanced Operative):** Researchers authorized to design and build bespoke electronics and battery packs. Requires formal CPD training.
        * **CAT III (Specialist Operative):** Lab Managers and infrastructure specialists handling high-voltage/high-risk systems.
        """)
        
        st.markdown("### ⚡ Module 3: Voltage Limits & Battery Hazards")
        st.error("""
        **Category 2 (Complex/High Risk) Work** automatically includes any setup exceeding standard Separated Extra Low Voltage (SELV) limits: **50V AC or 120V DC**. 
        
        **THE BATTERY EXCEPTION:** Standard low-voltage exemptions do **NOT** apply to batteries. Even a single 3.7V lithium-ion cell carries severe risks of high short-circuit currents, arc flashes, and thermal runaway. Therefore, **all bare battery assembly and testing is classified as Category 2** and requires a formal Risk Assessment and Permit to Energise.
        """)
        
        st.markdown("### 🚨 Module 4: Emergency Protocols & The Two-Person Rule")
        st.write("""
        * **The Two-Person Rule:** For any complex, energized Category 2 testing, a second briefed person must be present. They must know how to operate the Emergency Power Off (EPO) button and safely isolate the rig.
        * **Hazardous Environments (DSEAR):** If you are working near explosive gases (like hydrogen or battery off-gassing) or in wet labs, standard electrical equipment is strictly prohibited. ATEX-certified (Ex) or IP67-rated components are mandatory.
        * **Emergency Response:** If a battery vents or equipment catches fire inside a containment box, **do not open the box**. Hit the EPO, evacuate the immediate area, and alert a first aider.
        """)
        
        st.divider()
        
        # --- INDUCTION QUIZ ---
        st.subheader("📝 Induction Quiz")
        st.write("Review the modules above, then complete this quiz to unlock your CAT I lab access.")
        with st.form("quiz_form"):
            q1 = st.radio("1. As a new CAT I Standard Operative, are you allowed to build or modify bespoke circuits?", 
                          ["Yes, if I am careful.", 
                           "No, I may only use standard off-the-shelf equipment.", 
                           "Yes, if it is under 50V."])
            
            q2 = st.radio("2. Are bare lithium-ion batteries exempt from Category II rules if they are under 50V?", 
                          ["Yes, low voltage means low risk.", 
                           "No, they carry high short-circuit and thermal runaway risks."])
            
            q3 = st.radio("3. What is the 'Two-Person Rule'?", 
                          ["Two people must sign the Risk Assessment.", 
                           "A second person trained to use the Emergency Power Off (EPO) must be present for energized Cat II testing.", 
                           "Equipment must have two separate power cables."])
            
            submit_quiz = st.form_submit_button("Submit Quiz")
            
            if submit_quiz:
                # Correct Answers
                if (q1 == "No, I may only use standard off-the-shelf equipment." and 
                    q2 == "No, they carry high short-circuit and thermal runaway risks." and 
                    q3 == "A second person trained to use the Emergency Power Off (EPO) must be present for energized Cat II testing."):
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
