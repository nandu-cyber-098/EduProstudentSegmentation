import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="EduPro Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    file = "EduPro Online Platform.xlsx"

    users = pd.read_excel(file, sheet_name="Users")
    courses = pd.read_excel(file, sheet_name="Courses")
    transactions = pd.read_excel(file, sheet_name="Transactions")

    df = transactions.merge(users, on="UserID")
    df = df.merge(courses, on="CourseID")

    return users, courses, transactions, df

users, courses, transactions, df = load_data()

# Title
st.title("EduPro Live Analytics Dashboard")
st.markdown("### Student Segmentation and Personalized Recommendation System")

# Sidebar Filters
st.sidebar.header("Filters")

selected_category = st.sidebar.multiselect(
    "Select Course Category",
    options=df["CourseCategory"].unique(),
    default=df["CourseCategory"].unique()
)

selected_gender = st.sidebar.multiselect(
    "Select Gender",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

filtered_df = df[
    (df["CourseCategory"].isin(selected_category)) &
    (df["Gender"].isin(selected_gender))
]

# KPI Section
st.subheader("Platform Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Users", filtered_df["UserID"].nunique())
k2.metric("Total Courses", filtered_df["CourseID"].nunique())
k3.metric("Transactions", len(filtered_df))
k4.metric("Revenue", f"₹{filtered_df['Amount'].sum():,.2f}")

# Enrollment by Category
st.subheader("Enrollments by Category")

cat = filtered_df.groupby("CourseCategory").size().reset_index(name="Enrollments")

fig1 = px.bar(
    cat,
    x="CourseCategory",
    y="Enrollments",
    title="Course Enrollments"
)

st.plotly_chart(fig1, use_container_width=True)

# Revenue by Category
st.subheader("Revenue by Category")

rev = filtered_df.groupby("CourseCategory")["Amount"].sum().reset_index()

fig2 = px.bar(
    rev,
    x="CourseCategory",
    y="Amount",
    title="Revenue Analysis"
)

st.plotly_chart(fig2, use_container_width=True)

# Learner Explorer
st.subheader("Learner Profile Explorer")

uid = st.selectbox(
    "Select UserID",
    filtered_df["UserID"].unique()
)

user_data = filtered_df[filtered_df["UserID"] == uid]

if not user_data.empty:

    st.write("### Learner Information")

    st.dataframe(
        user_data[
            ["UserID", "Age", "Gender"]
        ].drop_duplicates()
    )

    preferred_category = user_data["CourseCategory"].mode()[0]
    preferred_level = user_data["CourseLevel"].mode()[0]

    total_spend = user_data["Amount"].sum()
    total_courses = user_data["CourseID"].nunique()

    # Segmentation Logic
    if total_spend > 5000 and total_courses >= 5:
        segment = "High Value Learner"

    elif total_courses <= 2:
        segment = "Beginner Learner"

    elif total_spend < 500:
        segment = "Budget Learner"

    else:
        segment = "Explorer"

    st.write("### Learner Segment")
    st.success(segment)

    st.write("### Learner Preferences")
    st.write("Preferred Category:", preferred_category)
    st.write("Preferred Level:", preferred_level)

    # Recommendations
    st.subheader("Personalized Recommendations")

    recommendations = courses[
        (courses["CourseCategory"] == preferred_category) &
        (courses["CourseLevel"] == preferred_level)
    ].sort_values(
        by="CourseRating",
        ascending=False
    ).head(5)

    st.dataframe(
        recommendations[
            [
                "CourseName",
                "CourseCategory",
                "CourseLevel",
                "CourseRating"
            ]
        ]
    )

# Segment Visualization
st.subheader("Segment Analytics")

segment_counts = {
    "High Value Learner": 0,
    "Beginner Learner": 0,
    "Budget Learner": 0,
    "Explorer": 0
}

for uid in filtered_df["UserID"].unique():

    temp = filtered_df[filtered_df["UserID"] == uid]

    spend = temp["Amount"].sum()
    courses_count = temp["CourseID"].nunique()

    if spend > 5000 and courses_count >= 5:
        segment_counts["High Value Learner"] += 1

    elif courses_count <= 2:
        segment_counts["Beginner Learner"] += 1

    elif spend < 500:
        segment_counts["Budget Learner"] += 1

    else:
        segment_counts["Explorer"] += 1

segment_df = pd.DataFrame({
    "Segment": list(segment_counts.keys()),
    "Count": list(segment_counts.values())
})

fig3 = px.pie(
    segment_df,
    names="Segment",
    values="Count",
    title="Learner Segments"
)

st.plotly_chart(fig3, use_container_width=True)

# Final Insight
st.subheader("Project Conclusion")

st.info(
    "This dashboard demonstrates how learner analytics and personalized recommendations can improve engagement, retention, and learner satisfaction for EduPro."
)