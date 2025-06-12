import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Load and prepare data ---
@st.cache_data
def load_data():
    # Adjust file path as needed; in Streamlit Cloud include the file in your repo and use a relative path
    df = pd.read_excel('data.xlsx')
    # Clean and standardize column names
    df.columns = df.columns.str.strip()

    # Map categorical codes to labels using actual Excel column names
    marital_map = {1: 'Single', 2: 'Married', 3: 'Widower', 4: 'Divorced', 5: 'Facto Union', 6: 'Legally Separated'}
    df['Marital Status'] = df['Marital_status'].map(marital_map)
    df['Gender'] = df['Gender'].map({0: 'Female', 1: 'Male'})
    df['Scholarship'] = df['Scholarship_holder'].map({0: 'No', 1: 'Yes'})
    df['Special Needs'] = df['Educational_special_needs'].map({0: 'No', 1: 'Yes'})
    df['Debtor'] = df['Debtor'].map({0: 'No', 1: 'Yes'})
    df['Tuition Up-to-date'] = df['Tuition_fees_up_to_date'].map({0: 'No', 1: 'Yes'})
    df['International'] = df['International'].map({0: 'No', 1: 'Yes'})

    # Compute first-semester completion rate
    if {'Curricular_units_1st_sem_enrolled', 'Curricular_units_1st_sem_approved'}.issubset(df.columns):
        df['Completion Rate %'] = (
            df['Curricular_units_1st_sem_approved'] /
            df['Curricular_units_1st_sem_enrolled']
        ) * 100

    return df

# Load data
data = load_data()

# --- Sidebar filters ---
st.sidebar.header('🔎 Filters')
# Course
courses = sorted(data['Course'].astype(str).unique())
sel_courses = st.sidebar.multiselect('Course', courses, default=courses)
# Gender
genders = sorted(data['Gender'].unique())
sel_gender = st.sidebar.multiselect('Gender', genders, default=genders)
# Age at enrollment
min_age, max_age = int(data['Age_at_enrollment'].min()), int(data['Age_at_enrollment'].max())
sel_age = st.sidebar.slider('Age at Enrollment', min_age, max_age, (min_age, max_age))
# Scholarship holder
sch_opts = sorted(data['Scholarship'].unique())
sel_sch = st.sidebar.multiselect('Scholarship Holder', sch_opts, default=sch_opts)
# Special educational needs
sn_opts = sorted(data['Special Needs'].unique())
sel_sn = st.sidebar.multiselect('Special Educational Needs', sn_opts, default=sn_opts)

# Apply filters
df = data[
    data['Course'].astype(str).isin(sel_courses) &
    data['Gender'].isin(sel_gender) &
    data['Age_at_enrollment'].between(sel_age[0], sel_age[1]) &
    data['Scholarship'].isin(sel_sch) &
    data['Special Needs'].isin(sel_sn)
]

# --- Dashboard Title ---
st.title('🎓 Student Performance Monitoring Dashboard')

# --- Key Performance Indicators ---
st.subheader('📊 Overview Metrics')
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Students', len(df))
if 'Admission_grade' in df.columns:
    col2.metric('Avg Admission Grade', f"{df['Admission_grade'].mean():.1f}")
if 'Curricular_units_1st_sem_grade' in df.columns:
    col3.metric('Avg 1st Sem Grade', f"{df['Curricular_units_1st_sem_grade'].mean():.1f}")
if 'Completion Rate %' in df.columns:
    col4.metric('Avg Completion Rate (%)', f"{df['Completion Rate %'].mean():.1f}%")

# --- Economic Context ---
st.subheader('🌎 Economic Context')
ec1, ec2, ec3 = st.columns(3)
ec1.metric('Unemployment Rate (%)', f"{data['Unemployment_rate'].iloc[0]:.1f}")
ec2.metric('Inflation Rate (%)', f"{data['Inflation_rate'].iloc[0]:.1f}")
ec3.metric('GDP', f"{data['GDP'].iloc[0]:,.0f}")

st.markdown('---')

# --- Academic Performance ---
st.subheader('📈 Academic Performance')
if 'Admission_grade' in df.columns:
    fig_ag = px.histogram(df, x='Admission_grade', nbins=20, title='Admission Grade Distribution')
    st.plotly_chart(fig_ag, use_container_width=True)
if {'Previous_qualification_grade', 'Curricular_units_1st_sem_grade'}.issubset(df.columns):
    fig_sc = px.scatter(
        df,
        x='Previous_qualification_grade',
        y='Curricular_units_1st_sem_grade',
        color='Status',
        trendline='ols',
        title='Prev Qual Grade vs 1st Sem Grade'
    )
    st.plotly_chart(fig_sc, use_container_width=True)

# --- Dropout Rates by Key Factors ---
st.subheader('🚩 Dropout Rates by Key Factors')
key_feats = [
    ('Marital Status', 'Marital Status'),
    ('Scholarship Holder', 'Scholarship'),
    ('Special Educational Needs', 'Special Needs'),
    ('Debtor', 'Debtor'),
    ('Tuition Up-to-date', 'Tuition Up-to-date'),
    ('Gender', 'Gender'),
    ('International', 'International')
]
for title, col in key_feats:
    if col in df.columns and 'Status' in df.columns:
        grp = (
            df.groupby(col)['Status']
              .value_counts(normalize=True)
              .mul(100)
              .rename('pct')
              .reset_index()
        )
        df_drop = grp[grp['Status'] == 'Dropout']
        fig = px.bar(df_drop, x=col, y='pct', title=f'Dropout Rate by {title}')
        fig.update_layout(yaxis_title='Dropout Rate (%)')
        st.plotly_chart(fig, use_container_width=True)

st.markdown('---')

# --- Course Level Summaries ---
st.subheader('✔️ Course Level Summaries')
if 'Completion Rate %' in df.columns:
    cr = df.groupby('Course')['Completion Rate %'].mean().reset_index()
    fig_cr = px.bar(cr, x='Course', y='Completion Rate %', title='Avg Completion Rate by Course')
    st.plotly_chart(fig_cr, use_container_width=True)

# Status distribution by Course
grouped = (
    df.groupby('Course')['Status']
      .value_counts(normalize=True)
      .mul(100)
      .rename('pct')
      .reset_index()
)
fig_td = px.bar(
    grouped,
    x='Course',
    y='pct',
    color='Status',
    barmode='group',
    title='Status Distribution by Course'
)
st.plotly_chart(fig_td, use_container_width=True)

st.caption('Interactive dashboard for monitoring key factors influencing student performance.')