import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Flexcity Branding (you can customize this with your logo and colors)
    st.image("flexcity_logo.png", width=200)  # Replace with the path to Flexcity's logo
    st.title("Estimate Your Battery Revenue with Flexcity in Belgium")

    st.markdown("""
    Welcome to Flexcity's Battery Revenue Simulator. Discover how much revenue your battery can generate
    by participating in the Belgian aFRR (Automatic Frequency Restoration Reserve) market with Flexcity.
    """)

    st.sidebar.header("Your Battery Specifications")
    # Battery specifications
    capacity = st.sidebar.number_input("Battery Capacity (MWh)", min_value=0.1, value=2.0)
    power = st.sidebar.number_input("Battery Power Rating (MW)", min_value=0.1, value=1.0)
    efficiency = st.sidebar.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
    reserved_capacity_pct = st.sidebar.slider("Reserved Capacity for Other Uses (%)", min_value=0, max_value=50, value=10)

    st.sidebar.header("Operational Parameters")
    # Operational conditions
    availability = st.sidebar.slider("Availability (%)", min_value=0, max_value=100, value=95)
    operational_days = st.sidebar.slider("Operational Days per Year", min_value=1, max_value=365, value=350)

    st.sidebar.header("Market Parameters")
    # Market conditions specific to Belgium
    afrr_price = st.sidebar.number_input("Average aFRR Price (€/MW/h)", min_value=0.0, value=75.0)
    electricity_cost = st.sidebar.number_input("Average Electricity Cost (€/MWh)", min_value=0.0, value=50.0)

    # Calculations
    # Adjust capacity for reserved percentage
    usable_capacity = capacity * (1 - reserved_capacity_pct / 100)

    # Effective power output considering efficiency and availability
    effective_power = min(power, usable_capacity * (efficiency / 100)) * (availability / 100)

    # Daily revenue from aFRR services
    daily_revenue = effective_power * afrr_price * 24  # Assuming participation 24 hours a day

    # Annual estimations
    annual_revenue = daily_revenue * operational_days

    # Cost to recharge the battery per day
    daily_energy_used = effective_power * 24 / (efficiency / 100)
    daily_charging_cost = daily_energy_used * electricity_cost
    annual_charging_cost = daily_charging_cost * operational_days

    # Net annual revenue
    net_annual_revenue = annual_revenue - annual_charging_cost

    st.subheader("Your Estimated Annual Revenue with Flexcity")
    st.markdown(f"""
    - **Effective Power Output:** {effective_power:.2f} MW
    - **Annual Revenue from aFRR:** €{annual_revenue:,.2f}
    - **Annual Charging Cost:** €{annual_charging_cost:,.2f}
    - **Net Annual Revenue:** €{net_annual_revenue:,.2f}
    """)

    # Visualization
    labels = ['Net Revenue', 'Charging Cost']
    sizes = [net_annual_revenue, annual_charging_cost]
    colors = ['#4CAF50', '#FF5722']

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    st.pyplot(fig1)

    st.markdown("""
    ### Why Partner with Flexcity?

    - **Maximize Your Revenue:** Flexcity optimizes your battery operations to capture the highest possible revenue.
    - **Expert Market Access:** With deep knowledge of the Belgian energy market, we navigate the complexities for you.
    - **End-to-End Support:** From installation to market participation, Flexcity provides comprehensive support.

    ### Get in Touch

    Interested in unlocking your battery's full potential? [Contact us](https://www.flexcity.energy/contact) for a personalized consultation.
    """)

    # Optional: Include a contact form (requires additional setup)
    # st.sidebar.header("Get a Detailed Report")
    # email = st.sidebar.text_input("Your Email Address")
    # if st.sidebar.button("Send Me a Detailed Report"):
    #     # Code to send an email with detailed report
    #     st.sidebar.success("Detailed report sent to your email!")

if __name__ == "__main__":
    main()