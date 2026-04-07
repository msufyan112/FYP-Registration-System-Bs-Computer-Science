import streamlit as st
import pandas as pd
import os

# --- PATH LOGIC ---
current_dir = os.path.dirname(os.path.abspath(__file__))
students_path = os.path.join(current_dir, 'students.csv')
groups_path = os.path.join(current_dir, 'final_groups.csv')

# --- CONFIGURATION ---
st.set_page_config(page_title="FYP Registration Portal", page_icon="🎓", layout="centered")

# --- ADMIN CREDENTIALS ---
FORM_NAME = "FYPREGISTRATION"

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
            background-color: rgba(0, 0, 0, 0.4) !important; 
            padding: 30px !important;
            border-radius: 15px !important;
            border: 2px solid rgba(255, 255, 255, 0.5) !important;
            backdrop-filter: blur(8px);
        }}
        .main-table-container {{
            background-color: rgba(0, 0, 0, 0.4);
            padding: 20px;
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(8px);
            margin-top: 20px;
        }}
        h1, h2, h3, label, p, .stMarkdown {{
            color: white !important;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 1);
        }}
        label {{ font-weight: bold !important; }}
        .stAlert {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_custom_style()

# --- DATA LOADING ---
def load_data():
    if not os.path.exists(students_path):
        st.error(f"Error: '{students_path}' not found!")
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
        except Exception:
            pass
    return all_students, assigned_students

supervisors_list = ["Dr. Anwar Muhammad", "Dr. Waseeq ul Islam Zafar", "Mr. Usman Rafi"]
all_students, assigned_students = load_data()

# --- SIDEBAR ADMIN & LOGOUT LOGIC ---
st.sidebar.title("Registration Portal")

if 'is_host' not in st.session_state:
    st.session_state.is_host = False

if not st.session_state.is_host:
    secret_input = st.sidebar.text_input("Host Login", placeholder="Enter password...", type="password")
    if secret_input == FORM_NAME:
        st.session_state.is_host = True
        st.rerun()
    elif secret_input != "":
        st.sidebar.error("Access Denied")
else:
    st.sidebar.success("Host Mode Active")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.is_host = False
        st.rerun()
    
    st.sidebar.subheader("🛠️ Admin Controls")
    if st.sidebar.button("🗑️ Clear All Registrations"):
        if os.path.exists(groups_path):
            os.remove(groups_path)
            st.rerun()

is_host = st.session_state.is_host

# --- UI DESIGN ---
st.title("🎓 FYP Registration Portal")
st.markdown("### Final Year Project Group & Supervisor Selection")

# --- THE REGISTRATION FORM ---
with st.form("registration_form", clear_on_submit=True):
    st.subheader("1. Project Details")
    group_name = st.text_input("Project Title / Group Name", placeholder="Enter your project title...")
    
    st.write("**Supervisor Priorities (Select three unique supervisors)**")
    c1, c2, c3 = st.columns(3)
    with c1:
        s1 = st.selectbox("1st Choice (Highest)", ["-- Select --"] + supervisors_list, key="s1_reg")
    with c2:
        s2 = st.selectbox("2nd Choice", ["-- Select --"] + supervisors_list, key="s2_reg")
    with c3:
        s3 = st.selectbox("3rd Choice (Lowest)", ["-- Select --"] + supervisors_list, key="s3_reg")
    
    st.divider()
    st.subheader("2. Group Members")
    available = sorted([s for s in all_students if s not in assigned_students])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        m1 = st.selectbox("Member 1 (Leader)", ["-- Select --"] + available, key="m1_reg")
    with col2:
        m2 = st.selectbox("Member 2", ["-- Select --"] + available, key="m2_reg")
    with col3:
        m3 = st.selectbox("Member 3 (Optional)", ["-- Select --", "None"] + available, key="m3_reg")

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

    if is_host:
        with st.expander("📝 Host: Edit Existing Registration"):
            row_idx = st.number_input("Enter Row Number to Edit", min_value=1, max_value=len(df_display), step=1)
            target_data = df.iloc[int(row_idx)-1]
            
            with st.form("edit_form"):
                st.write(f"Editing Row {row_idx}")
                edit_name = st.text_input("Edit Title", value=target_data["Group Name"])
                
                e_c1, e_c2, e_c3 = st.columns(3)
                
                # --- SAFE INDEX SEARCH FOR SUPERVISORS ---
                def get_idx(val, lst, default=0):
                    try: return lst.index(val)
                    except: return default

                edit_s1 = e_c1.selectbox("1st Choice", supervisors_list, index=get_idx(target_data["1st Choice"], supervisors_list))
                edit_s2 = e_c2.selectbox("2nd Choice", supervisors_list, index=get_idx(target_data["2nd Choice"], supervisors_list))
                edit_s3 = e_c3.selectbox("3rd Choice", supervisors_list, index=get_idx(target_data["3rd Choice"], supervisors_list))
                
                e_m1, e_m2, e_m3 = st.columns(3)
                edit_m1 = e_m1.selectbox("Member 1", all_students, index=get_idx(target_data["Member 1"], all_students))
                edit_m2 = e_m2.selectbox("Member 2", all_students, index=get_idx(target_data["Member 2"], all_students))
                
                # --- FIXED: SAFE INDEX SEARCH FOR MEMBER 3 ---
                m3_raw = target_data["Member 3"]
                m3_val = str(m3_raw) if pd.notna(m3_raw) and m3_raw != "" else "None"
                
                if m3_val == "None":
                    m3_idx = 0
                else:
                    try:
                        m3_idx = all_students.index(m3_val) + 1
                    except ValueError:
                        m3_idx = 0
                
                edit_m3 = e_m3.selectbox("Member 3", ["None"] + all_students, index=m3_idx)

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Save Changes"):
                    df.iloc[int(row_idx)-1] = [edit_name, edit_s1, edit_s2, edit_s3, edit_m1, edit_m2, edit_m3 if edit_m3 != "None" else ""]
                    df.to_csv(groups_path, index=False)
                    st.rerun()
                if b2.form_submit_button("❌ Delete This Row"):
                    df = df.drop(df.index[int(row_idx)-1])
                    df.to_csv(groups_path, index=False)
                    st.rerun()

    st.markdown('<div class="main-table-container">', unsafe_allow_html=True)
    st.dataframe(df_display, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No groups registered yet.")
