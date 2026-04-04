import streamlit as st
import pandas as pd
import os

# ... [Keep your PATH LOGIC and CONFIGURATION sections the same] ...

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(students_path):
        st.error(f"Error: '{students_path}' not found!")
        return [], []
        
    all_students_df = pd.read_csv(students_path)
    all_students = all_students_df['Name'].tolist()
    
    assigned_students = []
    if os.path.exists(groups_path):
        try:
            df = pd.read_csv(groups_path)
            # Ensure we check the correct columns for already assigned students
            for col in ['Member 1', 'Member 2', 'Member 3']:
                if col in df.columns:
                    assigned_students.extend(df[col].dropna().tolist())
        except:
            pass
            
    return all_students, assigned_students

# Updated Supervisor List
supervisors = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]
# New Priority List
priorities = ["1 (Highest)", "2 (Middle)", "3 (Lowest)"]

all_students, assigned_students = load_data()

# ... [Keep add_custom_style() and UI DESIGN sections the same] ...

# --- THE FORM ---
with st.form("registration_form", clear_on_submit=True):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name", placeholder="Enter your project title...")
    
    # Split into two columns for Supervisor and Priority
    col_sup, col_prio = st.columns([2, 1])
    with col_sup:
        selected_supervisor = st.selectbox("Select Supervisor", ["-- Select Supervisor --"] + supervisors)
    with col_prio:
        selected_priority = st.selectbox("Priority Level", priorities)
    
    st.divider()
    
    # ... [Keep Member selection columns the same] ...
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

# --- LOGIC ---
if submit:
    current_selection = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or selected_supervisor == "-- Select Supervisor --":
        st.error("⚠️ Please fill in the Project Title and select a Supervisor.")
    elif len(current_selection) < 2:
        st.error("⚠️ A group must have at least 2 members.")
    elif len(current_selection) != len(set(current_selection)):
        st.error("⚠️ You cannot select the same student twice!")
    else:
        # Added "Priority" field to the data being saved
        new_data = pd.DataFrame([{
            "Group Name": group_name,
            "Supervisor": selected_supervisor,
            "Priority": selected_priority[0], # Saves just the number '1', '2', or '3'
            "Member 1": m1,
            "Member 2": m2,
            "Member 3": m3 if m3 != "None" else ""
        }])
        
        file_exists = os.path.exists(groups_path)
        new_data.to_csv(groups_path, mode='a', index=False, header=not file_exists)
        
        st.success(f"✅ Group '{group_name}' registered successfully with Priority {selected_priority[0]}!")
        st.balloons()
        st.rerun()

# ... [Keep the DISPLAY SECTION the same] ...

# --- DISPLAY SECTION ---
st.divider()
st.subheader("📋 Registered Groups")
if os.path.exists(groups_path):
    display_df = pd.read_csv(groups_path)
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No groups registered yet.")
