import streamlit as st
import pandas as pd
import os

# --- PATH LOGIC (Prevents FileNotFoundError on Cloud) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
students_path = os.path.join(current_dir, 'students.csv')
groups_path = os.path.join(current_dir, 'final_groups.csv')

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓")

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(students_path):
        st.error(f"Error: '{students_path}' not found! Please ensure students.csv is in the same folder as app.py.")
        return [], []
        
    all_students_df = pd.read_csv(students_path)
    all_students = all_students_df['Name'].tolist()
    
    assigned_students = []
    if os.path.exists(groups_path):
        df = pd.read_csv(groups_path)
        for col in ['Member 1', 'Member 2', 'Member 3']:
            assigned_students.extend(df[col].dropna().tolist())
            
    return all_students, assigned_students

# Supervisor List
supervisors = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]

all_students, assigned_students = load_data()

# --- UI DESIGN ---
st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")

# --- THE FORM ---
with st.form("registration_form", clear_on_submit=True):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name", placeholder="Enter your project title...")
    selected_supervisor = st.selectbox("Select Supervisor", ["-- Select Supervisor --"] + supervisors)
    
    st.divider()
    
    st.subheader("2. Group Members")
    available = [s for s in all_students if s not in assigned_students]
    available.sort()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        m1 = st.selectbox("Member 1 (Leader)", ["-- Select --"] + available)
    with col2:
        m2 = st.selectbox("Member 2", ["-- Select --"] + available)
    with col3:
        m3 = st.selectbox("Member 3 (Optional)", ["-- Select --", "None"] + available)

    submit = st.form_submit_button("Submit Registration")

# --- LOGIC & VALIDATION ---
if submit:
    current_selection = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or selected_supervisor == "-- Select Supervisor --":
        st.error("⚠️ Please fill in the Project Title and select a Supervisor.")
    elif len(current_selection) < 2:
        st.error("⚠️ A group must have at least 2 members.")
    elif len(current_selection) != len(set(current_selection)):
        st.error("⚠️ You cannot select the same student twice!")
    else:
        new_data = pd.DataFrame([{
            "Group Name": group_name,
            "Supervisor": selected_supervisor,
            "Member 1": m1,
            "Member 2": m2,
            "Member 3": m3 if m3 != "None" else ""
        }])
        
        file_exists = os.path.exists(groups_path)
        new_data.to_csv(groups_path, mode='a', index=False, header=not file_exists)
        
        st.success(f"✅ Group '{group_name}' registered successfully!")
        st.balloons()
        st.rerun()

# --- DISPLAY SECTION ---
st.divider()
st.subheader("📋 Registered Groups")
if os.path.exists(groups_path):
    display_df = pd.read_csv(groups_path)
    
    # SHIFT INDEX TO START FROM 1
    display_df.index = display_df.index + 1
    
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No groups registered yet.")


