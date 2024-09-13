import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def main():
    st.set_page_config(page_title="Battery Revenue Simulator", layout="wide")

    # Add Veolia logo
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/48/Veolia_logo.svg", width=200)

    st.title("Estimate Your Battery Revenue with Flexcity in Belgium")

    st.markdown("""
    Welcome to Flexcity's Battery Revenue Simulator. Discover how much revenue your battery can generate
    by participating in the Belgian aFRR (Automatic Frequency Restoration Reserve) market with Flexcity.

    This tool allows you to explore different market scenarios and see how partnering with Flexcity can maximize your investment.
    """)

    # Battery Specifications
    st.header("Battery Specifications")
    capacity = st.number_input("Battery Capacity (MWh)", min_value=0.1, value=2.0)
    power = st.number_input("Battery Power Rating (MW)", min_value=0.1, value=1.0)
    efficiency = st.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
    reserved_capacity_pct = st.slider("Reserved Capacity for Other Uses (%)", min_value=0, max_value=50, value=10)

    # Operational Parameters
    st.header("Operational Parameters")
    availability = st.slider("Availability (%)", min_value=0, max_value=100, value=95)
    activation_rate = st.slider("Average aFRR Activation Rate (%)", min_value=0, max_value=20, value=15)
    # Limit operational life to a maximum of 5 years
    operational_life_years = st.number_input("Battery Operational Life (years, max 5)", min_value=1, max_value=5, value=5)
    operational_life_months = operational_life_years * 12

    # Financial Parameters
    st.header("Financial Parameters")
    battery_cost = st.number_input("Battery Investment Cost (€ per MWh)", min_value=0.0, value=350000.0)

    # Market Scenario - Base Case by Default
    st.header("Market Scenario")
    st.write("Customize the market scenario by adjusting the parameters below.")

    # User-defined scenario parameters
    initial_electricity_cost = st.number_input("Initial Electricity Cost (€/MWh)", min_value=0.0, value=50.0)
    electricity_price_growth = st.number_input("Monthly Electricity Price Growth Rate (% per month)", value=0.15)
    initial_afrr_capacity_price = st.number_input("aFRR Capacity Price (€/MW/h)", min_value=0.0, value=80.0)
    afrr_capacity_price_growth = st.number_input("Monthly aFRR Capacity Price Growth Rate (% per month)", value=0.15)
    afrr_activation_price = st.number_input("aFRR Activation Price (€/MWh)", min_value=0.0, value=110.0)
    afrr_activation_price_growth = st.number_input("Monthly aFRR Activation Price Growth Rate (% per month)", value=0.18)

    scenario = "Base Case"

    # Calculations
    usable_capacity = capacity * (1 - reserved_capacity_pct / 100)
    effective_power = min(power, usable_capacity * (efficiency / 100)) * (availability / 100)
    total_investment = capacity * battery_cost

    # Prepare monthly periods
    total_months = int(operational_life_months)
    months = np.arange(1, total_months + 1)

    # Generate price trajectories on a monthly basis
    electricity_prices = initial_electricity_cost * ((1 + electricity_price_growth / 100) ** (months - 1))
    afrr_capacity_prices = initial_afrr_capacity_price * ((1 + afrr_capacity_price_growth / 100) ** (months - 1))
    afrr_activation_prices = afrr_activation_price * ((1 + afrr_activation_price_growth / 100) ** (months - 1))

    # Monthly calculations
    hours_per_month = 24 * 365 / 12
    monthly_capacity_revenues = effective_power * afrr_capacity_prices * hours_per_month
    monthly_energy_activated = effective_power * (activation_rate / 100) * hours_per_month
    monthly_activation_revenues = monthly_energy_activated * afrr_activation_prices
    monthly_revenues = monthly_capacity_revenues + monthly_activation_revenues
    monthly_energy_charged = monthly_energy_activated / (efficiency / 100)
    monthly_charging_costs = monthly_energy_charged * electricity_prices
    net_monthly_revenues = monthly_revenues - monthly_charging_costs
    cumulative_cash_flow = net_monthly_revenues.cumsum() - total_investment

    # Estimate payback period in months
    payback_period = None
    for i in range(len(cumulative_cash_flow)):
        if cumulative_cash_flow[i] >= 0:
            if i == 0:
                # Payback in first month
                fraction = (total_investment) / net_monthly_revenues[0]
                months_needed = int(fraction)
                payback_period = months_needed
            else:
                # Interpolate between months
                cash_flow_before = cumulative_cash_flow[i-1]
                cash_flow_after = cumulative_cash_flow[i]
                cash_needed = -cash_flow_before
                cash_generated_in_month = net_monthly_revenues[i]
                fraction = cash_needed / cash_generated_in_month
                months_needed = int(i + fraction)
                payback_period = months_needed
            break

    df = pd.DataFrame({
        'Month': months,
        'Electricity Price (€/MWh)': electricity_prices,
        'aFRR Capacity Price (€/MW/h)': afrr_capacity_prices,
        'aFRR Activation Price (€/MWh)': afrr_activation_prices,
        'Monthly Capacity Revenue (€)': monthly_capacity_revenues,
        'Monthly Activation Revenue (€)': monthly_activation_revenues,
        'Monthly Charging Cost (€)': monthly_charging_costs,
        'Net Monthly Revenue (€)': net_monthly_revenues,
        'Cumulative Cash Flow (€)': cumulative_cash_flow
    })

    # Display results
    st.header("Results")
    st.subheader("Cumulative Cash Flow")
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Month'],
        y=df['Cumulative Cash Flow (€)'],
        mode='lines+markers',
        name=scenario
    ))

    fig.update_layout(title='Cumulative Cash Flow Over Time',
                      xaxis_title='Month',
                      yaxis_title='Cumulative Cash Flow (€)')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payback Period")
    if payback_period is not None:
        st.write(f"**Estimated Payback Period:** {payback_period} months")
    else:
        st.write("**Estimated Payback Period:** Not within operational life")

    st.subheader("Detailed Financial Projections")
    # Remove the index and ensure 'Month' is the first column
    df.reset_index(drop=True, inplace=True)
    df = df[['Month', 'Electricity Price (€/MWh)', 'aFRR Capacity Price (€/MW/h)', 'aFRR Activation Price (€/MWh)',
             'Monthly Capacity Revenue (€)', 'Monthly Activation Revenue (€)', 'Monthly Charging Cost (€)',
             'Net Monthly Revenue (€)', 'Cumulative Cash Flow (€)']]
    st.dataframe(df.style.format('{:,.2f}'))

    st.markdown("""
    ### Understanding the Business Case

    Investing in battery storage and participating in the aFRR market can provide significant revenue streams.
    By partnering with Flexcity, you can maximize your battery's potential through expert market access and optimized operations.

    - **Capacity Revenue:** Earnings from being available to provide aFRR services.
    - **Activation Revenue:** Earnings from actual energy delivery during activations.
    - **Charging Costs:** Costs incurred from recharging the battery after activations.

    The cumulative cash flow analysis helps you understand when you can expect to recover your initial investment under the defined market conditions.

    ### Next Steps

    - **Customize Assumptions:** Adjust the parameters to reflect your expectations.
    - **Contact Flexcity:** [Get in touch](https://www.flexcity.energy/contact) for a personalized consultation and to learn how we can help you optimize your battery's performance.

    """)

if __name__ == "__main__":
    main()