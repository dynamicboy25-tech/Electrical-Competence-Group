import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(page_title="UCL Electrical Competence App", layout="centered")

# --- Mock Database & State Initialization ---
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "admin": {"inducted": True, "tier": "CAT III"},
        "student1": {"inducted": False, "tier": "Pending"},
        "pouya": {"inducted": True, "tier": "CAT III"}
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

# --- Helper Functions ---
def next_step():
    st.session_state.training_step += 1

def reset_training():
    st.session_state.training_step = 1

def pass_induction():
    st.session_state.user_db[st.session_state.logged_in_user]["inducted"] = True
    st.session_state.user_db[st.session_state.logged_in_user]["tier"] = "CAT I"
    st.session_state.training_step = 1  
    st.success("Induction passed! You are now a CAT I Standard Operative.")
    st.rerun()

def render_download_buttons(key_prefix):
    """Renders the document download buttons safely, preventing duplicate key errors."""
    try:
        with open("corporate_policy.pdf", "rb") as pdf_file:
            st.download_button(label="⬇️ Download Corporate Policy", data=pdf_file, file_name="UCL_Corporate_Policy.pdf", mime="application/pdf", key=f"{key_prefix}_1")
    except FileNotFoundError:
        st.warning("⚠️ corporate_policy.pdf not yet uploaded to repository.")
        
    try:
        with open("technical_framework.pdf", "rb") as pdf_file:
            st.download_button(label="⬇️ Download Safety Framework & Decision Tree", data=pdf_file, file_name="UCL_Technical_Safety_Framework.pdf", mime="application/pdf", key=f"{key_prefix}_2")
    except FileNotFoundError:
        st.warning("⚠️ technical_framework.pdf not yet uploaded to repository.")
        
    try:
        with open("infrastructure_guide.pdf", "rb") as pdf_file:
            st.download_button(label="⬇️ Download Infrastructure Guide", data=pdf_file, file_name="UCL_Industrial_Infrastructure.pdf", mime="application/pdf", key=f"{key_prefix}_3")
    except FileNotFoundError:
        st.warning("⚠️ infrastructure_guide.pdf not yet uploaded to repository.")


# --- Main App Logic ---
st.title("⚡ UCL Electrical Competence Group")

if st.session_state.logged_in_user is None:
    st.subheader("Welcome to the ESPER Portal")
    with st.form("login_form"):
        username_input = st.text_input("Username (e.g., student1, pouya):").strip().lower()
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
        
        # Accessible Document Expander on EVERY training page
        with st.expander("📚 View Official Reference Documents"):
            st.write("You may reference the official policies at any time during this induction or quiz.")
            render_download_buttons(key_prefix="induction")
            
        st.divider()
        
        # PAGE 1: The Regulatory Framework
        if st.session_state.training_step == 1:
            st.header("Module 1: The Regulatory Framework")
            st.write("Electrical work within the department is not just guided by best practices; it is governed by strict, legally binding UK legislation. Ignorance of these laws is not a defense.")
            
            st.subheader("The Core Legislation")
            
            # Use columns to break up the text and make it digestible
            law1, law2 = st.columns(2)
            
            with law1:
                st.info("""
                **⚡ The Electricity at Work Regulations 1989 (EAWR)**
                The primary statutory law. It mandates that all systems must be constructed and maintained to prevent danger. **BS 7671 (The IET Wiring Regulations)** is the technical standard used to achieve this compliance.
                """)
                
                st.info("""
                **🏭 Provision and Use of Work Equipment Regs 1998 (PUWER)**
                Requires that all lab equipment is suitable for its intended use, safe, and maintained. It legally mandates verification testing (like Earth Loop Impedance) and strict operator training.
                """)
            
            with law2:
                st.warning("""
                **💥 Dangerous Substances & Explosive Atmospheres (DSEAR)**
                Requires control of fire and explosion risks. In our labs, this is heavily triggered by **battery off-gassing** (thermal runaway) and hydrogen use, dictating strict ATEX-rated components.
                """)
                
                st.warning("""
                **⚙️ Supply of Machinery (Safety) Regulations 2008**
                Applies to bespoke machinery built in-house (e.g., custom dynamometers). Requires fail-safe control circuits and hardwired Emergency Stops (E-Stops) that override software.
                """)

            st.divider()
            
            st.subheader("Top-Down Management & PI Accountability")
            st.error("""
            **Your Principal Investigator (PI) and Lab Manager bear the primary legal responsibility for your safety.**
            
            They are strictly accountable for ensuring you operate *only* within your authorized competency tier (CAT I, II, or III). Attempting complex electrical work without the prerequisite training and a formal **Permit to Energise** is a critical breach of institutional competence and safety compliance.
            """)
            
            # Add friction: Checkbox required to proceed
            confirm_law = st.checkbox("I acknowledge that my PI is accountable for my authorization, and working outside my authorized tier is a breach of UCL policy and UK law.")
            
            if confirm_law:
                st.button("Next: Competency Tiers ➡️", on_click=next_step)
            else:
                st.button("Next: Competency Tiers ➡️", disabled=True, help="Please check the acknowledgment box above to proceed.")

        # PAGE 2: ESPER Framework & Flowchart
        elif st.session_state.training_step == 2:
            st.header("Module 2: The ESPER Competency Framework")
            st.write("To ensure safety, UCL categorizes personnel and activities into distinct tiers. Your training determines what you are legally allowed to touch.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success("🟢 **CAT I (Standard)**\n\nAuthorized to use standard, off-the-shelf equipment (13A plug). **Cannot build, open, or modify circuits.**")
            with col2:
                st.warning("🟡 **CAT II (Advanced)**\n\nAuthorized to design and build bespoke electronics and battery packs. Requires CPD & Specialist Review.")
            with col3:
                st.error("🔴 **CAT III (Specialist)**\n\nLab Managers & specialists handling high-voltage, unshielded, or facility-level infrastructure.")

            st.divider()
            
            st.subheader("The Activity Decision Matrix")
            st.write("Before starting any new work, you must trace your activity on the flowchart below.")
            
            try:
                st.image("decision_tree.png", caption="UCL Electrical Safety Decision Tree", use_container_width=True)
            except:
                st.warning("[Flowchart Image Placeholder: Upload 'decision_tree.png' to GitHub to display here]")
            
            st.info("""
            💡 **How to read this chart:** 
            Notice the very first question: *Is it plug connected, MCB protected, and used for its intended purpose?* 
            If the answer is **No**, you automatically enter **Category 2 (Complex)** work. As a new CAT I Operative, you must stop and seek your PI or Lab Manager.
            """)
            
            confirm_matrix = st.checkbox("I understand that as a CAT I Operative, I must stop work and seek authorization if my activity falls under Category 2.")
            
            if confirm_matrix:
                st.button("Next: Voltage Limits ➡️", on_click=next_step)
            else:
                st.button("Next: Voltage Limits ➡️", disabled=True, help="Please check the confirmation box above to proceed.")

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
            st.write("You must score at least **80% (8/10)** to pass and unlock CAT I lab access. Feel free to open the Reference Documents menu above to verify your answers.")
            
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
                    
                    score = sum(bool(a) for a in answers)
                    
                    if None in [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]:
                        st.warning("Please answer all questions before submitting.")
                    elif score >= 8:
                        st.balloons()
                        pass_induction()
                    else:
                        st.error(f"You scored {score}/10. 80% (8/10) is required to pass.")
                        st.button("Review Modules and Try Again", on_click=reset_training)

    # ==========================================
    # FLOW B: INDUCTED USER DASHBOARD (TABS)
    # ==========================================
    else:
        st.success(f"Cleared for {user_data['tier']} operations.")
        
        tab1, tab2 = st.tabs(["🔍 Search & Dashboard", "📚 Document Library"])
        
        # --- TAB 1: Search ---
        with tab1:
            st.header("Lab Information Search")
            search_query = st.text_input("Search Database (e.g., RIG-001, BATT-02, Pouya):", "")
            
            if search_query:
                results = doc_db[doc_db.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
                if not results.empty:
                    st.write(f"**Found {len(results)} matching records:**")
                    st.dataframe(results, use_container_width=True, hide_index=True)
                else:
                    st.warning("No documents or equipment found matching that query.")
                    
            st.divider()
            st.subheader("Quick Links")
            col_a, col_b = st.columns(2)
            with col_a:
                st.button("📄 Submit New Permit to Energise")
                st.button("⚙️ Log Maintenance Activity")
            with col_b:
                st.button("🚨 Emergency Isolation Protocols", type="primary")

        # --- TAB 2: Document Library ---
        with tab2:
            st.header("Official Electrical Competence Documents")
            st.write("Review the summaries below to understand the rules governing our laboratories. Click the buttons to download the complete, legally binding documents.")

            st.divider()

            st.subheader("1. UCL Corporate Policy: Electrical Safety, Testing, and Maintenance")
            st.write("**Who is it for?** All staff, PIs, and students.")
            st.write("""
            **Core Summary:**
            * **Legal Framework:** Outlines UCL's statutory duties under EAWR 1989, PUWER 1998, and DSEAR 2002.
            * **Competency & Accountability:** Defines the ESPER tier system (CAT I, II, III). Establishes that Principal Investigators (PIs) and Lab Managers are strictly accountable for ensuring students do not work outside their authorized tier.
            * **Information Access:** Mandates the use of this App and QR codes on all active rigs to provide immediate access to safety protocols and maintenance logs.
            """)
            
            st.divider()

            st.subheader("2. Technical Safety Framework & Decision Matrix")
            st.write("**Who is it for?** Researchers and students planning new experiments or custom test rigs.")
            st.write("""
            **Core Summary:**
            * **Activity Decision Tree:** Provides the step-by-step flowchart to determine if your work is Category 1 (Standard) or Category 2 (Complex/High Risk).
            * **Battery Rules:** Establishes that **all energized bare battery work is Category 2**, regardless of voltage, due to thermal runaway and short-circuit risks.
            * **Operational Rules:** Details the strict requirements for the "Two-Person Rule" during energized testing and the mandatory ATEX/IP67 component checks for hazardous environments.
            """)
            
            st.divider()

            st.subheader("3. Industrial Electrical Infrastructure: Conductor Selection & Installation")
            st.write("**Who is it for?** Category II and III Operatives building custom machinery, dynamometers, or fixed infrastructure.")
            st.write("""
            **Core Summary:**
            * **Cable Sizing & Routing:** The definitive engineering guide for selecting H07RN-F flexible cables and SWA for mechanical protection.
            * **Hazardous Environments:** Dictates exactly how to route cables through explosive atmospheres (requiring ATEX barrier glands) and wet labs (requiring IP67+ components).
            * **Verification Testing:** Details the strict testing protocols (Insulation Resistance, Earth Loop Impedance $Z_s$) required before a Permit to Energise can be issued.
            """)
            
            st.divider()
            
            st.subheader("Downloads")
            render_download_buttons(key_prefix="library")
