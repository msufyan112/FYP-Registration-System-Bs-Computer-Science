import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Group & Supervisor Portal", page_icon="🎓")

# --- DATA LOADING ---
def load_data():
    # Load all students from your CSV
    all_students_df = pd.read_csv('students.csv')
    all_students = all_students_df['Name'].tolist()
    
    # Load already assigned students and supervisors from the saved groups file
    assigned_students = []
    if os.path.exists('final_groups.csv'):
        df = pd.read_csv('final_groups.csv')
        for col in ['Member 1', 'Member 2', 'Member 3']:
            assigned_students.extend(df[col].dropna().tolist())
            
    return all_students, assigned_students

# Supervisor List
supervisors = [
    "Dr. Anwar Muhammad", 
    "Dr. Waseeq ul Islam Zafar", 
    "Mr. Usman Rafi"
]

all_students, assigned_students = load_data()

# --- UI DESIGN ---
st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")
st.info("Note: Students already in a group will not appear in the selection lists.")

# --- THE FORM ---
with st.form("registration_form"):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name", placeholder="e.g. AI-Based Attendance System")
    
    # Supervisor Selection
    selected_supervisor = st.selectbox("Select Supervisor", ["-- Select Supervisor --"] + supervisors)
    
    st.divider()
    
    st.subheader("2. Group Members")
    # Filter out students who are already taken
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
    # Gather selections and remove placeholders
    current_selection = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name:
        st.error("⚠️ Please enter a Group Name or Project Title.")
    elif selected_supervisor == "-- Select Supervisor --":
        st.error("⚠️ Please choose a Supervisor.")
    elif len(current_selection) < 2:
        st.error("⚠️ A group must have at least 2 members.")
    elif len(current_selection) != len(set(current_selection)):
        st.error("⚠️ Duplicate Selection: You picked the same student twice!")
    else:
        # Prepare Data to Save
        new_entry = {
            "Group Name": group_name,
            "Supervisor": selected_supervisor,
            "Member 1": m1,
            "Member 2": m2,
            "Member 3": m3 if m3 != "None" else ""
        }
        
        new_data = pd.DataFrame([new_entry])
        
        # Save to CSV
        file_exists = os.path.exists('final_groups.csv')
        new_data.to_csv('final_groups.csv', mode='a', index=False, header=not file_exists)
        
        st.success(f"✅ Group '{group_name}' registered under {selected_supervisor}!")
        st.balloons()
        
        # Wait a moment then refresh to update lists
        st.rerun()

# --- DISPLAY SECTION ---
st.divider()
st.subheader("📋 Final Registered List")
if os.path.exists('final_groups.csv'):
    display_df = pd.read_csv('final_groups.csv')
    st.dataframe(display_df, use_container_width=True)
else:
    st.write("No groups have registered yet.")