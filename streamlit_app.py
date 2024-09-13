import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/48/Veolia_logo.svg", width=200)
    st.title("Estimate Your Battery Revenue with Flexcity in Belgium")

    # Battery Specifications
    capacity = st.sidebar.number_input("Battery Capacity (MWh)", min_value=0.1, value=2.0)
    power = st.sidebar.number_input("Battery Power Rating (MW)", min_value=0.1, value=1.0)
    efficiency = st.sidebar.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
    reserved_capacity_pct = st.sidebar.slider("Reserved Capacity for Other Uses (%)", min_value=0, max_value=50, value=10)

    # Financial Parameters
    battery_cost = st.sidebar.number_input("Battery Investment Cost (€ per MWh)", min_value=0.0, value=350000.0)
    operational_life = st.sidebar.number_input("Battery Operational Life (years)", min_value=1, value=15)

    # Operational Parameters
    availability = st.sidebar.slider("Availability (%)", min_value=0, max_value=100, value=95)
    activation_rate = st.sidebar.slider("Average aFRR Activation Rate (%)", min_value=0, max_value=100, value=15)

    # Price Scenarios
    scenario = st.sidebar.selectbox("Select Price Scenario", options=["Optimistic", "Base Case", "Pessimistic"])

    # Define market assumptions for the scenarios
    scenarios = {
        "Optimistic": {
            "electricity_price_growth": 1.2,    # Annual growth in electricity prices
            "afrr_capacity_price_growth": 2.5,  # Annual growth in aFRR capacity prices
            "afrr_activation_price_growth": 3.0,  # Annual growth in aFRR activation prices
            "initial_electricity_cost": 52.0,   # €/MWh
            "initial_afrr_capacity_price": 85.0, # €/MW/h
            "initial_afrr_activation_price": 115.0,  # €/MWh
        },
        "Base Case": {
            "electricity_price_growth": 1.8,
            "afrr_capacity_price_growth": 1.8,
            "afrr_activation_price_growth": 2.2,
            "initial_electricity_cost": 50.0,
            "initial_afrr_capacity_price": 80.0,
            "initial_afrr_activation_price": 110.0,
        },
        "Pessimistic": {
            "electricity_price_growth": 2.5,
            "afrr_capacity_price_growth": 0.5,
            "afrr_activation_price_growth": 1.0,
            "initial_electricity_cost": 48.0,
            "initial_afrr_capacity_price": 75.0,
            "initial_afrr_activation_price": 105.0,
        }
    }

    selected_scenario = scenarios[scenario]

    # Effective power output considering efficiency and availability
    usable_capacity = capacity * (1 - reserved_capacity_pct / 100)
    effective_power = min(power, usable_capacity * (efficiency / 100)) * (availability / 100)

    # Generate price trajectories based on the selected scenario
    years = np.arange(1, operational_life + 1)
    electricity_prices = selected_scenario["initial_electricity_cost"] * ((1 + selected_scenario["electricity_price_growth"] / 100) ** (years - 1))
    afrr_capacity_prices = selected_scenario["initial_afrr_capacity_price"] * ((1 + selected_scenario["afrr_capacity_price_growth"] / 100) ** (years - 1))
    afrr_activation_prices = selected_scenario["initial_afrr_activation_price"] * ((1 + selected_scenario["afrr_activation_price_growth"] / 100) ** (years - 1))

    # Annual capacity revenue, activation revenue, and charging costs
    annual_capacity_revenues = effective_power * afrr_capacity_prices * 24 * 365
    annual_energy_activated = effective_power * (activation_rate / 100) * 24 * 365
    annual_activation_revenues = annual_energy_activated * afrr_activation_prices
    annual_revenues = annual_capacity_revenues + annual_activation_revenues
    annual_energy_charged = annual_energy_activated / (efficiency / 100)
    annual_charging_costs = annual_energy_charged * electricity_prices
    net_annual_revenues = annual_revenues - annual_charging_costs

    # Cumulative cash flow and payback period
    cumulative_cash_flow = net_annual_revenues.cumsum() - (capacity * battery_cost)
    payback_period = years[np.where(cumulative_cash_flow >= 0)[0]]
    payback_period = payback_period[0] if len(payback_period) > 0 else np.nan

    # Prepare DataFrame for display
    df = pd.DataFrame({
        'Year': years,
        'Electricity Price (€/MWh)': electricity_prices,
        'aFRR Capacity Price (€/MW/h)': afrr_capacity_prices,
        'aFRR Activation Price (€/MWh)': afrr_activation_prices,
        'Annual Capacity Revenue (€)': annual_capacity_revenues,
        'Annual Activation Revenue (€)': annual_activation_revenues,
        'Annual Charging Cost (€)': annual_charging_costs,
        'Net Annual Revenue (€)': net_annual_revenues,
        'Cumulative Cash Flow (€)': cumulative_cash_flow
    })

    # Display results
    st.subheader(f"Scenario: {scenario}")
    st.dataframe(df.style.format({
        'Electricity Price (€/MWh)': '{:,.2f}',
        'aFRR Capacity Price (€/MW/h)': '{:,.2f}',
        'aFRR Activation Price (€/MWh)': '{:,.2f}',
        'Annual Capacity Revenue (€)': '{:,.2f}',
        'Annual Activation Revenue (€)': '{:,.2f}',
        'Annual Charging Cost (€)': '{:,.2f}',
        'Net Annual Revenue (€)': '{:,.2f}',
        'Cumulative Cash Flow (€)': '{:,.2f}'
    }))

    st.subheader("ROI and Payback Period")
    st.markdown(f"**Total Investment Cost:** €{capacity * battery_cost:,.2f}")
    if not np.isnan(payback_period):
        st.markdown(f"**Payback Period:** {payback_period:.0f} years")
    else:
        st.markdown("**Payback Period:** Not within operational life")

    # Break-even analysis graph
    fig, ax = plt.subplots()
    ax.plot(years, cumulative_cash_flow, marker='o')
    ax.axhline(0, color='gray', linewidth=0.8)
    ax.set_xlabel('Years')
    ax.set_ylabel('Cumulative Cash Flow (€)')
    ax.set_title('Break-even Analysis')
    ax.grid(True)
    st.pyplot(fig)

if __name__ == "__main__":
    main()