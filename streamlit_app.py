import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def main():
    st.title("Battery Revenue Simulator")

    # Battery Specifications
    st.header("Battery Specifications")
    capacity = st.number_input("Battery Capacity (MWh)", min_value=0.1, value=2.0)
    power = st.number_input("Battery Power Rating (MW)", min_value=0.1, value=1.0)
    efficiency = st.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
    reserved_capacity_pct = st.slider("Reserved Capacity for Other Uses (%)", min_value=0, max_value=50, value=10)

    # Operational Parameters
    st.header("Operational Parameters")
    availability = st.slider("Availability (%)", min_value=0, max_value=100, value=95)
    activation_rate = st.slider("Average aFRR Activation Rate (%)", min_value=0, max_value=100, value=15)
    operational_life = st.number_input("Battery Operational Life (years)", min_value=1, value=5)

    # Financial Parameters
    st.header("Financial Parameters")
    battery_cost = st.number_input("Battery Investment Cost (€ per MWh)", min_value=0.0, value=350000.0)

    # Market Scenarios
    st.header("Market Scenarios")
    scenario_options = ["Optimistic", "Base Case", "Pessimistic"]
    selected_scenarios = st.multiselect("Select Scenarios to Display", options=scenario_options, default=["Base Case"])

    scenarios = {}
    for scenario in selected_scenarios:
        if scenario == "Optimistic":
            initial_electricity_cost = 55.0
            electricity_price_growth = 1.2
            initial_afrr_capacity_price = 85.0
            afrr_capacity_price_growth = 2.5
            initial_afrr_activation_price = 115.0
            afrr_activation_price_growth = 3.0
        elif scenario == "Base Case":
            initial_electricity_cost = 50.0
            electricity_price_growth = 1.8
            initial_afrr_capacity_price = 80.0
            afrr_capacity_price_growth = 1.8
            initial_afrr_activation_price = 110.0
            afrr_activation_price_growth = 2.2
        elif scenario == "Pessimistic":
            initial_electricity_cost = 45.0
            electricity_price_growth = 2.5
            initial_afrr_capacity_price = 75.0
            afrr_capacity_price_growth = 0.5
            initial_afrr_activation_price = 105.0
            afrr_activation_price_growth = 1.0

        scenarios[scenario] = {
            "initial_electricity_cost": initial_electricity_cost,
            "electricity_price_growth": electricity_price_growth,
            "initial_afrr_capacity_price": initial_afrr_capacity_price,
            "afrr_capacity_price_growth": afrr_capacity_price_growth,
            "initial_afrr_activation_price": initial_afrr_activation_price,
            "afrr_activation_price_growth": afrr_activation_price_growth
        }

    # Calculations
    usable_capacity = capacity * (1 - reserved_capacity_pct / 100)
    effective_power = min(power, usable_capacity * (efficiency / 100)) * (availability / 100)
    total_investment = capacity * battery_cost
    years = np.arange(1, operational_life + 1)
    results = {}

    for scenario in scenarios:
        params = scenarios[scenario]
        electricity_prices = params["initial_electricity_cost"] * ((1 + params["electricity_price_growth"] / 100) ** (years - 1))
        afrr_capacity_prices = params["initial_afrr_capacity_price"] * ((1 + params["afrr_capacity_price_growth"] / 100) ** (years - 1))
        afrr_activation_prices = params["initial_afrr_activation_price"] * ((1 + params["afrr_activation_price_growth"] / 100) ** (years - 1))
        annual_capacity_revenues = effective_power * afrr_capacity_prices * 24 * 365
        annual_energy_activated = effective_power * (activation_rate / 100) * 24 * 365
        annual_activation_revenues = annual_energy_activated * afrr_activation_prices
        annual_revenues = annual_capacity_revenues + annual_activation_revenues
        annual_energy_charged = annual_energy_activated / (efficiency / 100)
        annual_charging_costs = annual_energy_charged * electricity_prices
        net_annual_revenues = annual_revenues - annual_charging_costs
        cumulative_cash_flow = net_annual_revenues.cumsum() - total_investment
        payback_period = next((year for year, cash in zip(years, cumulative_cash_flow) if cash >= 0), None)
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
        results[scenario] = {
            'data': df,
            'payback_period': payback_period,
        }

    # Display results
    st.header("Results")
    st.subheader("Cumulative Cash Flow Comparison")
    fig = go.Figure()

    for scenario in results:
        df = results[scenario]['data']
        fig.add_trace(go.Scatter(
            x=df['Year'],
            y=df['Cumulative Cash Flow (€)'],
            mode='lines+markers',
            name=scenario
        ))

    fig.update_layout(title='Break-even Analysis for Different Scenarios',
                      xaxis_title='Year',
                      yaxis_title='Cumulative Cash Flow (€)')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payback Periods")
    payback_data = {
        'Scenario': [],
        'Payback Period (years)': [],
    }
    for scenario in results:
        payback = results[scenario]['payback_period']
        payback_text = f"{payback}" if payback else 'Not within operational life'
        payback_data['Scenario'].append(scenario)
        payback_data['Payback Period (years)'].append(payback_text)

    payback_df = pd.DataFrame(payback_data)
    st.table(payback_df)

    st.subheader("Detailed Financial Projections")
    selected_scenario = st.selectbox("Select a scenario to view detailed projections", options=list(results.keys()))
    df = results[selected_scenario]['data']
    st.write(f"**Scenario:** {selected_scenario}")
    st.dataframe(df.style.format('{:,.2f}'))

if __name__ == "__main__":
    main()