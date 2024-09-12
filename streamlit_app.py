import streamlit as st

def main():
    st.title("Battery aFRR Potential Simulator")

    st.sidebar.header("Battery Parameters")
    # Battery specifications
    capacity = st.sidebar.number_input("Battery Capacity (MWh)", min_value=0.1, value=10.0)
    power = st.sidebar.number_input("Battery Power Rating (MW)", min_value=0.1, value=5.0)
    efficiency = st.sidebar.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
    availability = st.sidebar.slider("Availability (%)", min_value=0, max_value=100, value=95)

    st.sidebar.header("Market Parameters")
    # Market conditions
    afrr_price = st.sidebar.number_input("aFRR Price (€/MW/h)", min_value=0.0, value=50.0)
    operational_hours = st.sidebar.slider("Operational Hours per Day", min_value=1, max_value=24, value=24)

    # Calculations
    effective_power = power * (efficiency / 100) * (availability / 100)
    daily_afrr_capacity = effective_power * operational_hours
    daily_revenue = effective_power * afrr_price * operational_hours
    annual_revenue = daily_revenue * 365

    st.subheader("Simulation Results")
    st.write(f"**Effective Power Output (MW):** {effective_power:.2f}")
    st.write(f"**Daily aFRR Capacity Provided (MWh):** {daily_afrr_capacity:.2f}")
    st.write(f"**Daily Revenue (€):** {daily_revenue:.2f}")
    st.write(f"**Annual Revenue (€):** {annual_revenue:.2f}")

    st.subheader("Assumptions")
    st.markdown("""
    - **Effective Power Output** accounts for efficiency and availability losses.
    - **Constant aFRR Price** is assumed throughout the period.
    - **Battery participates** in the market every operational hour.
    - **No degradation** or maintenance costs are considered.
    """)

if __name__ == "__main__":
    main()