import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="UCL Electrical Competence App", layout="centered")

# --- Mock Database & State Initialization ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"name": "System Admin", "upi": "admin", "inducted": True, "tier": "CAT III"},
        "pouya": {"name": "Pouya Kolahian", "upi": "pouya", "inducted": True, "tier": "CAT III"}
    }
if 'quiz_logs' not in st.session_state:
    st.session_state.quiz_logs = []  # Stores the Excel log data
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

# --- Helper Functions ---
def next_step():
    st.session_state.training_step += 1

def reset_training():
    st.session_state.training_step = 1

def log_attempt(upi, name, score_val, passed):
    """Logs the quiz attempt for Excel export"""
    record = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "UPI": upi,
        "Score": f"{score_val}/10",
        "Result": "Pass" if passed else "Fail (Retake Required)"
    }
    st.session_state.quiz_logs.append(record)

def pass_induction(upi, name, score_val):
    st.session_state.user_db[upi]["inducted"] = True
    st.session_state.user_db[upi]["tier"] = "CAT I"
    st.session_state.training_step = 1  
    log_attempt(upi, name, score_val, True)
    st.success("Induction passed! You are now a CAT I Standard Operative.")
    st.rerun()

def render_download_buttons(key_prefix):
    try:
        with open("corporate_policy.pdf", "rb") as pdf_file:
            st.download_button(label="⬇️ Download Corporate Policy", data=pdf_file, file_name="UCL_Corporate_Policy.pdf", mime="application/pdf", key=f"{key_prefix}_1")
    except FileNotFoundError:
        st.warning("⚠️ corporate_policy.pdf not yet uploaded.")
        
    try:
        with open("technical_framework.pdf", "rb") as pdf_file:
            st.download_button(label="⬇️ Download Safety Framework", data=pdf_file, file_name="UCL_Technical_Safety_Framework.pdf", mime="application/pdf", key=f"{key_prefix}_2")
    except FileNotFoundError:
        st.warning("⚠️ technical_framework.pdf not yet uploaded.")
        
    try:
        with open("infrastructure_guide.pdf", "rb") as pdf_file:
            st.download_button(label="⬇️ Download Infrastructure Guide", data=pdf_file, file_name="UCL_Industrial_Infrastructure.pdf", mime="application/pdf", key=f"{key_prefix}_3")
    except FileNotFoundError:
        st.warning("⚠️ infrastructure_guide.pdf not yet uploaded.")

# --- Main App Logic ---
st.title("⚡ UCL Electrical Competence Group")

if st.session_state.logged_in_user is None:
    st.subheader("Welcome to the ESPER Portal")
    with st.form("login_form"):
        name_input = st.text_input("Full Name:").strip()
        upi_input = st.text_input("UCL UPI (e.g., zcab123):").strip().lower()
        submit_button = st.form_submit_button("Log In")
        
        if submit_button and upi_input != "" and name_input != "":
            if upi_input not in st.session_state.user_db:
                st.session_state.user_db[upi_input] = {"name": name_input, "upi": upi_input, "inducted": False, "tier": "Pending"}
            st.session_state.logged_in_user = upi_input
            st.rerun()
        elif submit_button:
            st.error("Please enter both your Name and UPI.")

else:
    current_upi = st.session_state.logged_in_user
    user_data = st.session_state.user_db[current_upi]
    
    st.sidebar.write(f"**Name:** {user_data['name']}")
    st.sidebar.write(f"**UPI:** {current_upi}")
    st.sidebar.write(f"**Tier:** {user_data['tier']}")
    if st.sidebar.button("Log Out"):
        st.session_state.logged_in_user = None
        st.session_state.training_step = 1
        st.rerun()

    # ==========================================
    # FLOW A: MULTI-PAGE INDUCTION TRAINING
    # ==========================================
    if not user_data["inducted"]:
        st.progress(st.session_state.training_step / 5, text=f"Step {st.session_state.training_step} of 5")
        
        with st.expander("📚 View Official Reference Documents"):
            st.write("You may reference the official policies at any time during this induction or quiz.")
            render_download_buttons(key_prefix="induction")
            
        st.divider()
        
        # PAGE 1: The Regulatory Framework
        if st.session_state.training_step == 1:
            st.header("Module 1: The Regulatory Framework")
            st.write("Electrical work within the department is not just guided by best practices; it is governed by strict, legally binding UK legislation. Ignorance of these laws is not a defense.")
            st.subheader("The Core Legislation")
            
            law1, law2 = st.columns(2)
            with law1:
                st.info("**⚡ The Electricity at Work Regulations 1989 (EAWR)**\nThe primary statutory law. Mandates that all systems must be constructed and maintained to prevent danger.")
                st.info("**🏭 Provision and Use of Work Equipment Regs 1998 (PUWER)**\nRequires that all lab equipment is suitable for its intended use, safe, and maintained.")
            with law2:
                st.warning("**💥 Dangerous Substances & Explosive Atmospheres (DSEAR)**\nRequires control of fire and explosion risks (e.g., battery off-gassing).")
                st.warning("**⚙️ Supply of Machinery (Safety) Regulations 2008**\nApplies to bespoke machinery built in-house. Requires hardwired Emergency Stops.")

            st.divider()
            st.subheader("Top-Down Management & PI Accountability")
            st.error("**Your Principal Investigator (PI) and Lab Manager bear the primary legal responsibility for your safety.**\n\nThey are strictly accountable for ensuring you operate *only* within your authorized competency tier.")
            
            confirm_law = st.checkbox("I acknowledge that my PI is accountable for my authorization, and working outside my authorized tier is a breach of UCL policy and UK law.")
            if confirm_law:
                st.button("Next: Competency Tiers ➡️", on_click=next_step)
            else:
                st.button("Next: Competency Tiers ➡️", disabled=True)

        # PAGE 2: ESPER Framework & Flowchart
        elif st.session_state.training_step == 2:
            st.header("Module 2: The ESPER Competency Framework")
            st.write("To ensure safety, UCL categorizes personnel and activities into distinct tiers.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("🟢 **CAT I (Standard)**\nAuthorized to use standard, off-the-shelf equipment. Cannot build or modify circuits.")
            with col2:
                st.warning("🟡 **CAT II (Advanced)**\nAuthorized to design and build bespoke electronics. Requires CPD & Specialist Review.")
            with col3:
                st.error("🔴 **CAT III (Specialist)**\nLab Managers & specialists handling infrastructure.")

            st.divider()
            st.subheader("The Activity Decision Matrix")
            try:
                st.image("decision_tree.png", caption="UCL Electrical Safety Decision Tree", use_container_width=True)
            except:
                st.warning("[Flowchart Image Placeholder]")
            
            st.info("💡 **How to read this chart:** If the equipment is NOT plug connected, MCB protected, and used for its intended purpose, you automatically enter **Category 2 (Complex)** work.")
            
            confirm_matrix = st.checkbox("I understand that as a CAT I Operative, I must stop work and seek authorization if my activity falls under Category 2.")
            if confirm_matrix:
                st.button("Next: Voltage Limits ➡️", on_click=next_step)
            else:
                st.button("Next: Voltage Limits ➡️", disabled=True)

        # PAGE 3: Voltage & Batteries
        elif st.session_state.training_step == 3:
            st.header("Module 3: Voltage Limits & Battery Hazards")
            st.write("The ESPER framework strictly separates voltage hazards (shock) from current hazards (fire and thermal runaway).")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("**🔌 The Low Voltage Exemption**\nSystems operating strictly below **42.2V AC or 60V DC** are generally exempt from the Specialist Review, PROVIDED they are driven by a current-limited source.")
            with col2:
                st.warning("**🔥 The Short-Circuit Hazard**\nEven at safe touch voltages, high sustained currents dump massive amounts of energy instantly, causing arc flashes.")

            st.divider()
            st.subheader("The Battery Exclusion Rule")
            st.error("**Standard low-voltage exemptions do NOT apply to bare battery cells or custom packs.**\n\nALL energized bare battery assembly and testing is automatically Category 2 and requires a formal Risk Assessment, regardless of the pack's voltage.")
            
            confirm_battery = st.checkbox("I understand that all bare battery work is automatically Category 2.")
            if confirm_battery:
                st.button("Next: Emergency Protocols ➡️", on_click=next_step)
            else:
                st.button("Next: Emergency Protocols ➡️", disabled=True)

        # PAGE 4: Emergency & DSEAR
        elif st.session_state.training_step == 4:
            st.header("Module 4: Emergency Protocols & Hazardous Environments")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info("**👥 The Two-Person Rule**\nLone working is strictly forbidden for energized Category 2 work. A briefed Second Person must be present.")
            with col2:
                st.warning("**🛑 Machinery & Hardwired E-Stops**\nAll bespoke automated machinery must have a hardwired Emergency Power Off (EPO) circuit. Software-only stops are illegal.")

            st.divider()
            st.subheader("Thermal Runaway Emergency Protocol")
            st.error("**IF A BATTERY VENTS OR CATCHES FIRE INSIDE A BLAST-RATED CONTAINMENT BOX:**\n1. **DO NOT OPEN THE BOX.**\n2. Hit the EPO.\n3. Evacuate.\n4. Alert a First Aider.")
            
            confirm_emergency = st.checkbox("I understand the Two-Person Rule, the hardwired EPO requirement, and the 'DO NOT OPEN' protocol.")
            if confirm_emergency:
                st.button("Proceed to Final Quiz ➡️", on_click=next_step)
            else:
                st.button("Proceed to Final Quiz ➡️", disabled=True)

        # PAGE 5: The 10-Question Quiz
        elif st.session_state.training_step == 5:
            st.header("📝 Final Induction Quiz")
            st.write("You must score at least **80% (8/10)** to pass. If you score below 80%, your attempt will be recorded as a fail, and you must retake the training.")
            
            with st.form("quiz_form"):
                q1 = st.radio("1. Who is ultimately accountable for ensuring you operate within your authorized tier?", ["The Student Union", "The Principal Investigator (PI) / Lab Manager", "The Building Janitor"], index=None)
                q2 = st.radio("2. As a CAT I Standard Operative, what are you authorized to do?", ["Build custom battery packs", "Modify the wiring of a dynamometer", "Use standard, off-the-shelf equipment plugged into a 13A socket"], index=None)
                q3 = st.radio("3. Under the EAWR 1989 and PUWER 1998, working outside your competency tier is:", ["A breach of UK law and UCL policy", "Allowed if you are careful", "Allowed if you watch a YouTube tutorial"], index=None)
                q4 = st.radio("4. What are the voltage limits for the SELV exemption (provided the source is current-limited)?", ["15V AC / 20V DC", "42.2V AC / 60V DC", "50V AC / 120V DC"], index=None)
                q5 = st.radio("5. Are bare lithium-ion battery cells exempt from Category II rules if they are under 50V?", ["Yes, low voltage means low risk", "No, they carry severe short-circuit and thermal runaway risks"], index=None)
                q6 = st.radio("6. What is the 'Two-Person Rule'?", ["Two people must sign a document", "A second person trained to hit the EPO must be present for energized CAT II testing", "You must use two multimeters"], index=None)
                q7 = st.radio("7. If working in a DSEAR zoned explosive atmosphere (e.g., battery off-gassing), what equipment is required?", ["Standard plastic enclosures", "ATEX-certified (Ex) components", "Any waterproof component"], index=None)
                q8 = st.radio("8. How must an Emergency Stop (EPO) on custom machinery operate?", ["Via a hardwired electromechanical circuit", "Via a software command to a microcontroller", "By unplugging it from the wall"], index=None)
                q9 = st.radio("9. What should you do if a battery goes into thermal runaway inside a blast-rated containment box?", ["Open the box to put out the fire", "Hit the EPO, evacuate, do not open the box, and alert a first aider", "Pour water into the box vents"], index=None)
                q10 = st.radio("10. How can you find the active Permit to Energise and test results for a lab rig?", ["Scan the rig's QR code using this App", "Ask the department head", "Look for a paper tag on the floor"], index=None)
                
                submit_quiz = st.form_submit_button("Submit Answers")
                
                if submit_quiz:
                    answers = [
                        q1 == "The Principal Investigator (PI) / Lab Manager",
                        q2 == "Use standard, off-the-shelf equipment plugged into a 13A socket",
                        q3 == "A breach of UK law and UCL policy",
                        q4 == "42.2V AC / 60V DC",
                        q5 == "No, they carry severe short-circuit and thermal runaway risks",
                        q6 == "A second person trained to hit the EPO must be present for energized CAT II testing",
                        q7 == "ATEX-certified (Ex) components",
                        q8 == "Via a hardwired electromechanical circuit",
                        q9 == "Hit the EPO, evacuate, do not open the box, and alert a first aider",
                        q10 == "Scan the rig's QR code using this App"
                    ]
                    
                    score = sum(bool(a) for a in answers)
                    
                    if None in [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]:
                        st.warning("Please answer all questions before submitting.")
                    elif score >= 8:
                        st.balloons()
                        pass_induction(current_upi, user_data['name'], score)
                    else:
                        log_attempt(current_upi, user_data['name'], score, False)
                        st.error(f"You scored {score}/10. 80% (8/10) is required to pass. Your attempt has been logged.")
                        st.button("Review Modules and Try Again", on_click=reset_training)

    # ==========================================
    # FLOW B: INDUCTED USER DASHBOARD (TABS)
    # ==========================================
    else:
        st.success(f"Cleared for {user_data['tier']} operations.")
        
        # Check if the user is an admin to show the extra tab
        is_admin = current_upi in ["admin", "pouya"]
        
        if is_admin:
            tab1, tab2, tab3 = st.tabs(["🔍 Search & Dashboard", "📚 Document Library", "⚙️ Admin Panel"])
        else:
            tab1, tab2 = st.tabs(["🔍 Search & Dashboard", "📚 Document Library"])
        
        # --- TAB 1: Search ---
        with tab1:
            st.header("Lab Information Search")
            search_query = st.text_input("Search Database (e.g., RIG-001, BATT-02):", "")
            
            if search_query:
                results = doc_db[doc_db.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
                if not results.empty:
                    st.dataframe(results, use_container_width=True, hide_index=True)
                else:
                    st.warning("No documents or equipment found matching that query.")
                    
            st.divider()
            st.subheader("Quick Links")
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("📄 Submit New Permit to Energise")
            with col_b:
                st.button("🚨 Emergency Isolation Protocols", type="primary")

        # --- TAB 2: Document Library ---
        with tab2:
            st.header("Official Electrical Competence Documents")
            render_download_buttons(key_prefix="library")

        # --- TAB 3: Admin Panel (Only visible to admin/pouya) ---
        if is_admin:
            with tab3:
                st.header("Admin Panel: Student Induction Records")
                st.write("View and download the logs of all student induction attempts.")
                
                if len(st.session_state.quiz_logs) > 0:
                    logs_df = pd.DataFrame(st.session_state.quiz_logs)
                    st.dataframe(logs_df, use_container_width=True, hide_index=True)
                    
                    # Convert DataFrame to CSV for download
                    csv = logs_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="⬇️ Download Records as CSV (Excel)",
                        data=csv,
                        file_name=f"UCL_Induction_Logs_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
                else:
                    st.info("No students have taken the quiz yet during this session.")
