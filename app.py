import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from models.predictor import predict_project_risk, predict_financial_risk
from db import save_prediction
st.set_page_config(page_title="PBIS | Predictive Business Intelligence", page_icon="📊", layout="wide")
DATA = Path(__file__).parent / "data" / "sample_data.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA)

df = load_data()
st.sidebar.title("PBIS")
st.sidebar.caption("Predictive Business Intelligence System")
page = st.sidebar.radio("Navigation", ["Overview", "Project Risk", "Financial Risk", "Data Explorer"])
st.sidebar.markdown("---")
st.sidebar.caption("Demo version • Synthetic data")
st.title("Predictive Business Intelligence System")
st.caption("Early-warning insights to help businesses act before problems escalate.")


def show_result(result, probability_label, reasons):
    p = result["probability"]
    c1, c2 = st.columns(2)
    c1.metric(probability_label, f"{p:.0%}")
    c2.metric("Risk level", result["risk_level"])
    st.progress(max(0.0, min(1.0, p)))
    st.markdown("**Why did the model flag these inputs?**")
    if reasons:
        for reason in reasons:
            st.write("- " + reason)
    else:
        st.write("- No rule-based warning threshold was triggered; continue monitoring.")
    st.markdown("**Suggested actions**")
    for action in result["recommendations"]:
        st.write("- " + action)
    st.caption("Demo prediction only: model trained on synthetic data. Validate with real historical company data before operational use.")

if page == "Overview":
    st.subheader("Executive overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projects monitored", len(df))
    c2.metric("High project risks", int((df["project_risk_label"] == 1).sum()))
    c3.metric("Average completion", f'{df["completion_pct"].mean():.1f}%')
    c4.metric("Average cost variance", f'{df["cost_variance_pct"].mean():.1f}%')
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(df, x="project_name", y="completion_pct", title="Project completion (%)"), use_container_width=True)
    with right:
        st.plotly_chart(px.scatter(df, x="completion_pct", y="days_remaining", size="cost_variance_pct", color="project_risk_label", hover_name="project_name", title="Project status and remaining time", labels={"project_risk_label":"Historical risk label"}), use_container_width=True)
    st.subheader("Early warning list")
    for _, row in df.iterrows():
        risk = predict_project_risk(row)
        if risk["risk_level"] in ("High", "Medium"):
            st.warning(f'{row["project_name"]}: {risk["risk_level"]} risk — estimated delay probability {risk["probability"]:.0%}')

elif page == "Project Risk":
    st.subheader("Project delay prediction")
    st.write("Enter project details, then click Predict project risk.")
    with st.form("project_prediction_form"):
        project_name = st.text_input("Project name", "New project")
        a, b = st.columns(2)
        with a:
            completion = st.number_input("Completion (%)", min_value=0.0, max_value=100.0, value=50.0, step=1.0)
            days = st.number_input("Days remaining", min_value=1, max_value=365, value=30, step=1)
        with b:
            weekly_progress = st.number_input("Weekly progress rate (0.1–2.0)", min_value=0.1, max_value=2.0, value=0.5, step=0.05, help="1.0 means the planned weekly progress rate; below 0.5 indicates slow progress in this demo model.")
            cost_variance = st.number_input("Cost variance (%)", min_value=-20.0, max_value=100.0, value=10.0, step=1.0)
        submitted = st.form_submit_button("Predict project risk", type="primary")
    if submitted:
        row = {"completion_pct": completion, "days_remaining": days, "weekly_progress": weekly_progress, "cost_variance_pct": cost_variance}
        result = predict_project_risk(row)
        reasons = []
        if weekly_progress < 0.5: reasons.append("Weekly progress rate is below 0.5.")
        if cost_variance > 18: reasons.append("Cost variance is above 18%.")
        if days < 45 and completion < 55: reasons.append("Less than 45 days remain while completion is below 55%.")
        st.success(f"Prediction completed for: {project_name}")
        show_result(result, "Estimated delay probability", reasons)

        save_prediction(
            module="Project Risk",
            entity_name=project_name,
            probability=result["probability"],
            risk_level=result["risk_level"],
            inputs=row,
            reasons=reasons,
            recommendations=result["recommendations"]
        )

elif page == "Financial Risk":
    st.subheader("Financial risk prediction")
    st.write("Enter monthly financial figures, then click Predict financial risk.")
    with st.form("financial_prediction_form"):
        a, b = st.columns(2)
        with a:
            revenue = st.number_input("Monthly revenue", min_value=1.0, value=200000.0, step=5000.0)
            expenses = st.number_input("Monthly expenses", min_value=0.0, value=170000.0, step=5000.0)
        with b:
            cash = st.number_input("Current cash balance", min_value=0.0, value=50000.0, step=5000.0)
            debt = st.number_input("Total debt", min_value=0.0, value=80000.0, step=5000.0)
        submitted = st.form_submit_button("Predict financial risk", type="primary")
    if submitted:
        row = {"monthly_revenue": revenue, "monthly_expenses": expenses, "cash_balance": cash, "debt": debt}
        result = predict_financial_risk(row)
        reasons = []
        if expenses / revenue > 0.9: reasons.append("Expenses exceed 90% of monthly revenue.")
        if cash < expenses * 0.18: reasons.append("Cash balance is below 18% of monthly expenses.")
        if debt / revenue > 0.65: reasons.append("Debt exceeds 65% of monthly revenue.")
        show_result(result, "Estimated financial risk", reasons)

else:
    st.subheader("Sample company data")
    st.dataframe(df, use_container_width=True)
    st.download_button("Download sample CSV", df.to_csv(index=False), "pbis_sample_data.csv", "text/csv")

st.markdown("---")
st.caption("PBIS MVP • Synthetic demonstration data • Predictions require validation before real-world use.")
