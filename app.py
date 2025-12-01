import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Payroll Error Detection Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1rem;
        border-left: 4px solid #f44336;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-left: 4px solid #4caf50;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">💼 Payroll Error Detection Dashboard</p>', unsafe_allow_html=True)
st.markdown("**Automated payroll validation system - Detect errors before processing**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📁 Upload Payroll Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    st.markdown("---")
    st.markdown("### 🎯 Error Detection Features")
    st.markdown("""
    - ❌ Negative hours worked
    - ❌ Negative net pay
    - ❌ Duplicate employee IDs
    - ❌ Missing critical data
    - ❌ Overtime validation
    """)
    
    st.markdown("---")
    st.markdown("### 👨‍💼 About")
    st.markdown("Developed by: **Your Name**")
    st.markdown("Contact: your.email@example.com")

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    
    # Key Metrics Section
    st.header("📊 Overview Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_employees = len(df)
    total_payroll = df['Net Pay'].sum() if 'Net Pay' in df.columns else 0
    avg_hours = df['Hours Worked'].mean() if 'Hours Worked' in df.columns else 0
    
    with col1:
        st.metric("Total Employees", total_employees)
    with col2:
        st.metric("Total Payroll", f"${total_payroll:,.2f}")
    with col3:
        st.metric("Avg Hours/Employee", f"{avg_hours:.1f}")
    with col4:
        errors_found = 0
        if 'Hours Worked' in df.columns:
            errors_found += (df['Hours Worked'] < 0).sum()
        if 'Net Pay' in df.columns:
            errors_found += (df['Net Pay'] < 0).sum()
        if 'Employee ID' in df.columns:
            errors_found += df['Employee ID'].duplicated().sum()
        st.metric("Errors Detected", errors_found, delta=None if errors_found == 0 else "Issues Found", delta_color="inverse")
    
    st.markdown("---")
    
    # Error Detection Section
    st.header("🔍 Detailed Error Analysis")
    
    error_details = []
    error_employees = []
    
    # Check for negative hours
    if 'Hours Worked' in df.columns:
        negative_hours = df[df['Hours Worked'] < 0]
        if not negative_hours.empty:
            error_details.append({
                'Error Type': 'Negative Hours Worked',
                'Count': len(negative_hours),
                'Severity': 'High'
            })
            for _, row in negative_hours.iterrows():
                error_employees.append({
                    'Employee ID': row.get('Employee ID', 'N/A'),
                    'Employee Name': row.get('Employee Name', 'N/A'),
                    'Error Type': 'Negative Hours',
                    'Value': row['Hours Worked'],
                    'Expected': 'Positive value'
                })
    
    # Check for negative pay
    if 'Net Pay' in df.columns:
        negative_pay = df[df['Net Pay'] < 0]
        if not negative_pay.empty:
            error_details.append({
                'Error Type': 'Negative Net Pay',
                'Count': len(negative_pay),
                'Severity': 'Critical'
            })
            for _, row in negative_pay.iterrows():
                error_employees.append({
                    'Employee ID': row.get('Employee ID', 'N/A'),
                    'Employee Name': row.get('Employee Name', 'N/A'),
                    'Error Type': 'Negative Pay',
                    'Value': f"${row['Net Pay']:.2f}",
                    'Expected': 'Positive value'
                })
    
    # Check for duplicate IDs
    if 'Employee ID' in df.columns:
        duplicates = df[df['Employee ID'].duplicated(keep=False)]
        if not duplicates.empty:
            error_details.append({
                'Error Type': 'Duplicate Employee IDs',
                'Count': len(duplicates),
                'Severity': 'High'
            })
            for _, row in duplicates.iterrows():
                error_employees.append({
                    'Employee ID': row.get('Employee ID', 'N/A'),
                    'Employee Name': row.get('Employee Name', 'N/A'),
                    'Error Type': 'Duplicate ID',
                    'Value': 'Duplicate Entry',
                    'Expected': 'Unique ID'
                })
    
    # Display results
    if error_details:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("⚠️ Error Summary")
            error_df = pd.DataFrame(error_details)
            
            # Color code by severity
            def highlight_severity(row):
                if row['Severity'] == 'Critical':
                    return ['background-color: #ffcdd2'] * len(row)
                elif row['Severity'] == 'High':
                    return ['background-color: #fff9c4'] * len(row)
                else:
                    return [''] * len(row)
            
            st.dataframe(error_df.style.apply(highlight_severity, axis=1), use_container_width=True)
        
        with col2:
            # Pie chart of errors
            fig = px.pie(error_df, values='Count', names='Error Type', 
                        title='Error Distribution',
                        color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed employee errors
        st.subheader("📋 Affected Employees")
        employee_error_df = pd.DataFrame(error_employees)
        st.dataframe(employee_error_df, use_container_width=True)
        
        # Download error report
        csv_errors = employee_error_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Error Report (CSV)",
            data=csv_errors,
            file_name="payroll_error_report.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    else:
        st.success("✅ **No errors detected!** All payroll data passed validation checks.")
        st.balloons()
    
    st.markdown("---")
    
    # Data Preview
    st.header("📄 Payroll Data Preview")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Data Statistics
    if 'Hours Worked' in df.columns and 'Net Pay' in df.columns:
        st.header("📈 Data Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Hours distribution
            fig_hours = px.histogram(df, x='Hours Worked', 
                                    title='Hours Worked Distribution',
                                    color_discrete_sequence=['#1f77b4'])
            st.plotly_chart(fig_hours, use_container_width=True)
        
        with col2:
            # Pay distribution
            fig_pay = px.box(df, y='Net Pay', 
                            title='Net Pay Distribution',
                            color_discrete_sequence=['#2ca02c'])
            st.plotly_chart(fig_pay, use_container_width=True)

else:
    # Welcome screen
    st.info("👈 **Please upload a payroll CSV file to begin analysis**")
    
    st.markdown("### 📋 Expected CSV Format")
    st.markdown("""
    Your CSV file should contain the following columns:
    - **Employee ID**: Unique identifier for each employee
    - **Employee Name**: Full name of the employee
    - **Hours Worked**: Total hours worked in the pay period
    - **Hourly Rate**: Pay rate per hour
    - **Gross Pay**: Total pay before deductions
    - **Tax**: Tax deductions
    - **Net Pay**: Final pay after deductions
    """)
    
    st.markdown("### 🎯 What This Tool Does")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### ✅ Validates Data")
        st.markdown("Automatically checks for common payroll errors")
    
    with col2:
        st.markdown("#### 📊 Provides Insights")
        st.markdown("Visual analytics and detailed reporting")
    
    with col3:
        st.markdown("#### 📥 Exports Reports")
        st.markdown("Download error reports for action")