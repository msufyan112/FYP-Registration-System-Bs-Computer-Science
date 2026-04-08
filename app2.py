import streamlit as st
import pandas as pd
import os

# --- PATH LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
students_path = os.path.join(current_dir, 'students.csv')
groups_path = os.path.join(current_dir, 'final_groups.csv')

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓", layout="centered")
FORM_NAME = "FYPREGISTRATION"

# --- SESSION STATE INITIALIZATION ---
if 'is_host' not in st.session_state:
    st.session_state.is_host = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = False

# --- BACKGROUND & STYLING ---
def add_custom_style():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://images.unsplash.com/photo-1517694712202-14dd9538aa97");
            background-attachment: fixed;
            background-size: cover;
        }}
        [data-testid="stForm"] {{
            background-color: rgba(0, 0, 0, 0.6) !important; 
            padding: 30px !important;
            border-radius: 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            backdrop-filter: blur(10px);
        }}
        .main-table-container {{
            background-color: rgba(0, 0, 0, 0.6);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            margin-top: 20px;
        }}
        h1, h2, h3, label, p, .stMarkdown {{
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_custom_style()

# --- HELPER FUNCTIONS ---
def load_data():
    if not os.path.exists(students_path):
        return [], []
    all_students_df = pd.read_csv(students_path)
    all_students = sorted(all_students_df['Name'].tolist())
    assigned_students = []
    if os.path.exists(groups_path):
        try:
            df = pd.read_csv(groups_path)
            for col in ['Member 1', 'Member 2', 'Member 3']:
                if col in df.columns:
                    assigned_students.extend(df[col].dropna().tolist())
        except: pass
    return all_students, assigned_students

def get_idx(val, lst, default=0):
    try:
        return lst.index(val)
    except (ValueError, KeyError):
        return default

# --- DATA LOADING ---
supervisors_list = ["Dr. Muhammad Anwar", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]
all_students, assigned_students = load_data()

# --- TOP NAVIGATION / LOGIN LOGIC ---
col_title, col_login = st.columns([4, 1])

with col_login:
    if not st.session_state.is_host:
        if st.button("🔐 Host Login"):
            st.session_state.show_login = not st.session_state.show_login
    else:
        if st.button("🚪 Logout"):
            st.session_state.is_host = False
            st.session_state.show_login = False
            st.rerun()

# --- LOGIN SECTION ---
if st.session_state.show_login and not st.session_state.is_host:
    with st.form("login_form"):
        password = st.text_input("Enter Host Password", type="password")
        if st.form_submit_button("Login"):
            if password == FORM_NAME:
                st.session_state.is_host = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("Incorrect Password")

# --- ADMIN CONTROLS ---
if st.session_state.is_host:
    st.info("🛠️ Host Mode Active")
    if st.button("🗑️ Clear All Registrations"):
        if os.path.exists(groups_path):
            os.remove(groups_path)
            st.rerun()

st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")

# --- REGISTRATION FORM ---
with st.form("registration_form", clear_on_submit=True):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name")
    
    st.write("**Supervisor Priorities**")
    c1, c2, c3 = st.columns(3)
    s1 = c1.selectbox("1st Choice", ["-- Select --"] + supervisors_list, key="reg_s1")
    s2 = c2.selectbox("2nd Choice", ["-- Select --"] + supervisors_list, key="reg_s2")
    s3 = c3.selectbox("3rd Choice", ["-- Select --"] + supervisors_list, key="reg_s3")
    
    st.divider()
    st.subheader("2. Group Members")
    available = sorted([s for s in all_students if s not in assigned_students])
    
    col1, col2, col3 = st.columns(3)
    m1 = col1.selectbox("Member 1 (Leader)", ["-- Select --"] + available, key="reg_m1")
    m2 = col2.selectbox("Member 2", ["-- Select --"] + available, key="reg_m2")
    m3 = col3.selectbox("Member 3 (Optional)", ["-- Select --", "None"] + available, key="reg_m3")

    submit = st.form_submit_button("Submit Registration")

if submit:
    selected_sups = [s for s in [s1, s2, s3] if s != "-- Select --"]
    current_members = [m for m in [m1, m2, m3] if m not in ["-- Select --", "None"]]
    
    if not group_name or len(selected_sups) < 3:
        st.error("⚠️ Please fill in all details.")
    elif len(set(selected_sups)) < 3:
        st.error("⚠️ Supervisor choices must be unique.")
    elif len(current_members) < 2:
        st.error("⚠️ At least 2 members required.")
    else:
        new_row = {
            "Group Name": group_name,
            "1st Choice": s1, "2nd Choice": s2, "3rd Choice": s3,
            "Member 1": m1, "Member 2": m2, "Member 3": m3 if m3 != "None" else ""
        }
        pd.DataFrame([new_row]).to_csv(groups_path, mode='a', index=False, header=not os.path.exists(groups_path))
        st.success("✅ Registered!")
        st.rerun()

# --- DISPLAY & EDIT SECTION ---
st.divider()
st.subheader("📋 Registered Groups")

if os.path.exists(groups_path):
    df = pd.read_csv(groups_path)
    df_display = df.copy()
    df_display.index = df_display.index + 1

    if st.session_state.is_host:
        with st.expander("📝 Edit Registration"):
            row_idx = st.number_input("Row Number", min_value=1, max_value=len(df), step=1)
            target_data = df.iloc[int(row_idx)-1]
            
            with st.form("edit_form"):
                e_name = st.text_input("Edit Title", value=target_data["Group Name"])
                
                ec1, ec2, ec3 = st.columns(3)
                es1 = ec1.selectbox("1st Choice", supervisors_list, index=get_idx(target_data["1st Choice"], supervisors_list))
                es2 = ec2.selectbox("2nd Choice", supervisors_list, index=get_idx(target_data["2nd Choice"], supervisors_list))
                es3 = ec3.selectbox("3rd Choice", supervisors_list, index=get_idx(target_data["3rd Choice"], supervisors_list))
                
                em1_opt = all_students
                em2_opt = all_students
                em3_opt = ["None"] + all_students

                em1_val = target_data["Member 1"]
                em2_val = target_data["Member 2"]
                em3_raw = target_data["Member 3"]
                em3_val = str(em3_raw) if pd.notna(em3_raw) and str(em3_raw).strip() != "" else "None"

                emc1, emc2, emc3 = st.columns(3)
                em1 = emc1.selectbox("Member 1", em1_opt, index=get_idx(em1_val, em1_opt))
                em2 = emc2.selectbox("Member 2", em2_opt, index=get_idx(em2_val, em2_opt))
                em3 = emc3.selectbox("Member 3", em3_opt, index=get_idx(em3_val, em3_opt))

                btn_save = st.form_submit_button("💾 Save Changes")
                btn_del = st.form_submit_button("❌ Delete Registration")

                if btn_save:
                    df.iloc[int(row_idx)-1] = [e_name, es1, es2, es3, em1, em2, em3 if em3 != "None" else ""]
                    df.to_csv(groups_path, index=False)
                    st.rerun()
                
                if btn_del:
                    df = df.drop(df.index[int(row_idx)-1])
                    df.to_csv(groups_path, index=False)
                    st.rerun()

    st.markdown('<div class="main-table-container">', unsafe_allow_html=True)
    st.dataframe(df_display, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No groups registered yet.")
    
