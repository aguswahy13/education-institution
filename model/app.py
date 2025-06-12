import streamlit as st
import joblib
import numpy as np

st.set_page_config(page_title="Student Dropout Prediction", layout="centered")

# --- Load Model ---
model = joblib.load(r"model/rdf_model.joblib")
scaler = joblib.load(r"model/scaler.pkl")

def predict_status(inputs):
    input_array = np.array(inputs).reshape(1, -1)
    input_array = scaler.transform(input_array)
    prediction = model.predict(input_array)
    return prediction

# --- Sidebar Info ---
with st.sidebar:
    st.title("📊 About this app")
    st.markdown("""
    Predict the status of a student (Dropout, Enrolled, Graduate) based on academic and personal factors.
    - **Inputs:** Grades, Enrollment, Fees, etc.
    - **Model:** Random Forest Classifier
    """)
    st.info("All inputs are confidential.")

st.markdown(
    "<h1 style='text-align: center; color: #4F8BF9;'>🎓 Student Dropout Prediction Dashboard</h1>",
    unsafe_allow_html=True
)

st.write("---")

# --- Input Form ---
with st.form(key="prediction_form"):
    st.subheader("Enter Student Data")

    col1, col2 = st.columns(2)

    with col1:
        curricular_units_2nd_sem_approved = st.number_input(
            '2nd Sem: Units Approved', min_value=0, max_value=30, value=15)
        curricular_units_2nd_sem_grade = st.number_input(
            '2nd Sem: Average Grade', min_value=0, max_value=20, value=15)
        curricular_units_2nd_sem_enrolled = st.number_input(
            '2nd Sem: Units Enrolled', min_value=0, max_value=30, value=20)
        tuition_fees_up_to_date = st.selectbox(
            'Tuition Fees Up-to-Date?', [1, 0], format_func=lambda x: 'Yes' if x == 1 else 'No')

    with col2:
        curricular_units_1st_sem_approved = st.number_input(
            '1st Sem: Units Approved', min_value=0, max_value=30, value=15)
        curricular_units_1st_sem_grade = st.number_input(
            '1st Sem: Average Grade', min_value=0, max_value=20, value=15)
        curricular_units_1st_sem_enrolled = st.number_input(
            '1st Sem: Units Enrolled', min_value=0, max_value=30, value=20)
        scholarship_holder = st.selectbox(
            'Scholarship Holder?', [1, 0], format_func=lambda x: 'Yes' if x == 1 else 'No')

    admission_grade = st.slider('Admission Grade', min_value=0.0, max_value=200.0, value=5.0, step=0.1)
    displaced = st.selectbox('Displaced?', [1, 0], format_func=lambda x: 'Yes' if x == 1 else 'No')

    submitted = st.form_submit_button("🔮 Predict Status")

input_data = [
    curricular_units_2nd_sem_approved,
    curricular_units_2nd_sem_grade,
    curricular_units_1st_sem_approved,
    curricular_units_1st_sem_grade,
    tuition_fees_up_to_date,
    scholarship_holder,
    curricular_units_2nd_sem_enrolled,
    curricular_units_1st_sem_enrolled,
    admission_grade,
    displaced
]

# --- Prediction Output ---
if submitted:
    prediction = predict_status(input_data)
    status_dict = {0: 'Dropout', 1: 'Enrolled', 2: 'Graduate'}
    color_dict = {'Dropout': '#e74c3c', 'Enrolled': '#f1c40f', 'Graduate': '#27ae60'}

    # Handle both single-class and probability output
    if prediction.ndim == 1:
        predicted_status_index = prediction[0]
    else:
        predicted_status_index = np.argmax(prediction, axis=1)[0]
    predicted_status = status_dict[predicted_status_index]
    color = color_dict[predicted_status]

    st.markdown(
        f"""
        <div style='padding: 2rem; border-radius: 20px; background-color: {color}22; border-left: 6px solid {color}; text-align: center; margin-top: 2rem;'>
            <h2 style='color: {color};'>Prediction Result</h2>
            <p style='font-size: 2rem; font-weight: bold;'>{predicted_status}</p>
        </div>
        """, unsafe_allow_html=True
    )

    st.write("---")
    st.caption("🔒 Model prediction is for academic support only. Always double-check with an advisor.")
