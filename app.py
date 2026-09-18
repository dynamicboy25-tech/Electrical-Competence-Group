import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="UCL Electrical Competence App", layout="centered")

# --- Mock Database & State Initialization ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"inducted": True, "tier": "CAT III"},
        "student1": {"inducted": False, "tier": "Pending"}
    }
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None
if 'training_step' not in st.session_state:
    st.session_state.training_step = 1

doc_db = pd.DataFrame({
    "Tag/QR": ["RIG-001", "BATT-02", "SOP-01", "POL-01"],
    "Title": ["Dynamometer Test Bed", "Li-Ion Pack Assembly", "H07RN-F Glanding", "UCL Corporate Policy"],
    "Category": ["CAT II", "CAT II", "CAT I", "Policy"],
    "PI / Owner": ["Pouya Kolahian", "Mark Buckwell", "Joe Barwick", "Pouya Kolahian"],
    "Last Zs Test": ["0.45 Ohms (Pass)", "N/A", "N/A", "N/A"],
    "Status": ["Active", "Maintenance", "Active", "Active"]
})

# --- Navigation Functions ---
def next_step():
    st.session_state.training_step += 1

def reset_training():
    st.session_state.training_step = 1

def pass_induction():
    st.session_state.user_db[st.session_state.logged_in_user]["inducted"] = True
    st.session_state.user_db[st.session_state.logged_in_user]["tier"] = "CAT I"
    st.success("Induction passed! You are now a CAT I Standard Operative.")
    st.rerun()

# --- Main App Logic ---
st.title("⚡ UCL Electrical Competence Group")

if st.session_state.logged_in_user is None:
    st.subheader("Welcome to the ESPER Portal")
    with st.form("login_form"):
        username_input = st.text_input("Username (e.g., student1, admin):").strip().lower()
        submit_button = st.form_submit_button("Log In")
        if submit_button and username_input != "":
            if username_input not in st.session_state.user_db:
                st.session_state.user_db[username_input] = {"inducted": False, "tier": "Pending"}
            st.session_state.logged_in_user = username_input
            st.rerun()

else:
    current_user = st.session_state.logged_in_user
    user_data = st.session_state.user_db[current_user]
    
    st.sidebar.write(f"**Logged in as:** {current_user}")
    st.sidebar.write(f"**Competency Tier:** {user_data['tier']}")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in_user = None
        st.session_state.training_step = 1
        st.rerun()

    # ==========================================
    # FLOW A: MULTI-PAGE INDUCTION TRAINING
    # ==========================================
    if not user_data["inducted"]:
        st.progress(st.session_state.training_step / 5, text=f"Step {st.session_state.training_step} of 5")
        
        # PAGE 1: The Regulatory Framework
        if st.session_state.training_step == 1:
            st.header("Module 1: The Regulatory Framework")
            st.write("""
            Electrical work at UCL is governed by strict UK laws. 
            * **EAWR 1989:** Mandates that all electrical systems must be constructed and maintained to prevent danger.
            * **PUWER 1998:** Requires that equipment is suitable for its intended use, maintained safely, and operated only by trained individuals.
            * **Accountability:** Your Principal Investigator (PI) and Lab Manager are legally accountable for your safety. Operating outside of your authorized training tier is a direct breach of university policy and UK law.
            """)
            st.button("Next: Competency Tiers ➡️", on_click=next_step)

        # PAGE 2: ESPER Framework & Flowchart
        elif st.session_state.training_step == 2:
            st.header("Module 2: The ESPER Competency Framework")
            st.info("""
            **CAT I (Standard Operative):** Authorized to use standard, off-the-shelf, CE-marked equipment plugged into standard 13A sockets. **You may NOT build, open, or modify bespoke circuits.**
            
            **CAT II (Advanced Operative):** Authorized to design/build bespoke electronics and battery packs. Requires formal CPD training and a Specialist Review.
            
            **CAT III (Specialist Operative):** Infrastructure specialists handling high-voltage/high-risk systems.
            """)
            st.write("*Please review the Activity Decision Matrix below:*")
            # Note for GitHub deployment: Save your flowchart image as 'decision_tree.png' in the same folder as this app.
            try:
                st.image("decision_tree.png", caption="UCL Electrical Safety Decision Tree")
            except:
                st.warning("[Flowchart Image Placeholder: Upload 'decision_tree.png' to GitHub to display here]")
            
            st.button("Next: Voltage Limits ➡️", on_click=next_step)

        # PAGE 3: Voltage & Batteries
        elif st.session_state.training_step == 3:
            st.header("Module 3: Voltage Limits & Battery Hazards")
            st.write("Category 2 (Complex/High Risk) Work automatically includes any setup exceeding standard SELV limits: **50V AC or 120V DC**.")
            st.error("""
            **THE BATTERY EXCEPTION**
            Standard low-voltage exemptions do **NOT** apply to batteries. Even a single lithium-ion cell carries severe risks of high short-circuit currents, arc flashes, and thermal runaway. 
            
            Therefore, **all bare battery assembly and testing is classified as Category 2** and requires a formal Risk Assessment, regardless of voltage.
            """)
            st.button("Next: Emergency Protocols ➡️", on_click=next_step)

        # PAGE 4: Emergency & DSEAR
        elif st.session_state.training_step == 4:
            st.header("Module 4: Emergency Protocols & Hazardous Environments")
            st.write("""
            * **The Two-Person Rule:** For any energized Category 2 testing, a second briefed person must be present to operate the Emergency Power Off (EPO) if needed.
            * **Hazardous Environments (DSEAR):** If you are working near explosive gases (like hydrogen or battery off-gassing) or in wet labs, standard electrical equipment is strictly prohibited. ATEX-certified (Ex) or IP67-rated components are mandatory.
            * **Machinery:** All bespoke automated machinery must have a hardwired emergency stop. Software-only stops are illegal.
            """)
            st.button("Proceed to Final Quiz ➡️", on_click=next_step)

        # PAGE 5: The 10-Question Quiz
        elif st.session_state.training_step == 5:
            st.header("📝 Final Induction Quiz")
            st.write("You must score at least **80% (8/10)** to pass and unlock CAT I lab access.")
            
            with st.form("quiz_form"):
                q1 = st.radio("1. Who is ultimately accountable for ensuring you operate within your authorized tier?", ["The Student Union", "The Principal Investigator (PI) / Lab Manager", "The Building Janitor"], index=None)
                q2 = st.radio("2. As a CAT I Standard Operative, what are you authorized to do?", ["Build custom battery packs", "Modify the wiring of a dynamometer", "Use standard, off-the-shelf equipment plugged into a 13A socket"], index=None)
                q3 = st.radio("3. Under the EAWR 1989 and PUWER 1998, working outside your competency tier is:", ["A breach of UK law and UCL policy", "Allowed if you are careful", "Allowed if you watch a YouTube tutorial"], index=None)
                q4 = st.radio("4. What are the voltage limits for the SELV exemption?", ["15V AC / 20V DC", "50V AC / 120V DC", "230V AC / 400V DC"], index=None)
                q5 = st.radio("5. Are bare lithium-ion battery cells exempt from Category II rules if they are under 50V?", ["Yes, low voltage means low risk", "No, they carry severe short-circuit and thermal runaway risks"], index=None)
                q6 = st.radio("6. What is the 'Two-Person Rule'?", ["Two people must sign a document", "A second person trained to hit the EPO must be present for energized CAT II testing", "You must use two multimeters"], index=None)
                q7 = st.radio("7. If working in a DSEAR zoned explosive atmosphere (e.g., battery off-gassing), what equipment is required?", ["Standard plastic enclosures", "ATEX-certified (Ex) components", "Any waterproof component"], index=None)
                q8 = st.radio("8. How must an Emergency Stop (EPO) on custom machinery operate?", ["Via a hardwired electromechanical circuit", "Via a software command to a microcontroller", "By unplugging it from the wall"], index=None)
                q9 = st.radio("9. What should you do if a battery goes into thermal runaway inside a blast-rated containment box?", ["Open the box to put out the fire", "Hit the EPO, evacuate, do not open the box, and alert a first aider", "Pour water into the box vents"], index=None)
                q10 = st.radio("10. How can you find the active Permit to Energise and test results for a lab rig?", ["Scan the rig's QR code using this App", "Ask the department head", "Look for a paper tag on the floor"], index=None)
                
                submit_quiz = st.form_submit_button("Submit Answers")
                
                if submit_quiz:
                    # Check answers
                    answers = [
                        q1 == "The Principal Investigator (PI) / Lab Manager",
                        q2 == "Use standard, off-the-shelf equipment plugged into a 13A socket",
                        q3 == "A breach of UK law and UCL policy",
                        q4 == "50V AC / 120V DC",
                        q5 == "No, they carry severe short-circuit and thermal runaway risks",
                        q6 == "A second person trained to hit the EPO must be present for energized CAT II testing",
                        q7 == "ATEX-certified (Ex) components",
                        q8 == "Via a hardwired electromechanical circuit",
                        q9 == "Hit the EPO, evacuate, do not open the box, and alert a first aider",
                        q10 == "Scan the rig's QR code using this App"
                    ]
                    
                    score = sum(bool(a) for a in answers) # Counts true values
                    
                    if None in [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]:
                        st.warning("Please answer all questions before submitting.")
                    elif score >= 8:
                        st.balloons()
                        st.success(f"You scored {score}/10! Passed.")
                        pass_induction()
                    else:
                        st.error(f"You scored {score}/10. 80% (8/10) is required to pass.")
                        st.button("Review Modules and Try Again", on_click=reset_training)

    # ==========================================
    # FLOW B: INDUCTED USER DASHBOARD (SEARCH)
    # ==========================================
    else:
        st.header("Lab Information & Document Search")
        st.success(f"Cleared for {user_data['tier']} operations.")
        
        search_query = st.text_input("🔍 Search Database (e.g., RIG-001, BATT-02, Pouya):", "")
        if search_query:
            results = doc_db[doc_db.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
            if not results.empty:
                st.write(f"**Found {len(results)} matching records:**")
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.warning("No documents or equipment found matching that query.")
