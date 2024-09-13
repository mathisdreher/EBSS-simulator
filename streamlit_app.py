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
    activation_rate = st.slider("Average aFRR Activation Rate (%)", min_value=0, max_value=100, value=15)
    # Limit operational life to a maximum of 5 years
    operational_life = st.number_input("Battery Operational Life (years, max 5)", min_value=1, max_value=5, value=5)

    # Financial Parameters
    st.header("Financial Parameters")
    battery_cost = st.number_input("Battery Investment Cost (€ per MWh)", min_value=0.0, value=350000.0)

    # Market Scenarios
    st.header("Market Scenarios")
    st.write("The following scenarios are provided to help you assess different market conditions.")

    scenario_options = ["Optimistic", "Base Case", "Pessimistic"]
    # Show all scenarios by default
    selected_scenarios = scenario_options

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

    # Prepare quarterly periods
    total_quarters = operational_life * 4
    quarters = np.arange(1, total_quarters + 1)
    years = quarters / 4

    results = {}

    for scenario in scenarios:
        params = scenarios[scenario]

        # Generate price trajectories on a quarterly basis
        annual_electricity_prices = params["initial_electricity_cost"] * ((1 + params["electricity_price_growth"] / 100) ** (years - 1))
        quarterly_electricity_prices = np.repeat(annual_electricity_prices / 4, 1)
        
        annual_afrr_capacity_prices = params["initial_afrr_capacity_price"] * ((1 + params["afrr_capacity_price_growth"] / 100) ** (years - 1))
        quarterly_afrr_capacity_prices = np.repeat(annual_afrr_capacity_prices / 4, 1)
        
        annual_afrr_activation_prices = params["initial_afrr_activation_price"] * ((1 + params["afrr_activation_price_growth"] / 100) ** (years - 1))
        quarterly_afrr_activation_prices = np.repeat(annual_afrr_activation_prices / 4, 1)

        # Quarterly calculations
        hours_per_quarter = 24 * 365 / 4
        quarterly_capacity_revenues = effective_power * quarterly_afrr_capacity_prices * hours_per_quarter
        quarterly_energy_activated = effective_power * (activation_rate / 100) * hours_per_quarter
        quarterly_activation_revenues = quarterly_energy_activated * quarterly_afrr_activation_prices
        quarterly_revenues = quarterly_capacity_revenues + quarterly_activation_revenues
        quarterly_energy_charged = quarterly_energy_activated / (efficiency / 100)
        quarterly_charging_costs = quarterly_energy_charged * quarterly_electricity_prices
        net_quarterly_revenues = quarterly_revenues - quarterly_charging_costs
        cumulative_cash_flow = net_quarterly_revenues.cumsum() - total_investment

        # Estimate payback period in months
        payback_period = None
        for i in range(len(cumulative_cash_flow)):
            if cumulative_cash_flow[i] >= 0:
                if i == 0:
                    # Payback in first quarter
                    fraction = (total_investment) / net_quarterly_revenues[0]
                    months = int(fraction * 3)
                    payback_period = months
                else:
                    # Interpolate between quarters
                    cash_flow_before = cumulative_cash_flow[i-1]
                    cash_flow_after = cumulative_cash_flow[i]
                    cash_needed = -cash_flow_before
                    cash_generated_in_quarter = net_quarterly_revenues[i]
                    fraction = cash_needed / cash_generated_in_quarter
                    months = int((i) * 3 + fraction * 3)
                    payback_period = months
                break

        df = pd.DataFrame({
            'Quarter': quarters,
            'Year': years,
            'Net Quarterly Revenue (€)': net_quarterly_revenues,
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

        # Add payback period annotation
        payback_months = results[scenario]['payback_period']
        if payback_months is not None:
            payback_year = payback_months / 12
            fig.add_vline(x=payback_year, line_dash="dash", line_color=fig.data[-1].line.color)
            fig.add_annotation(x=payback_year, y=0, text=f"{scenario} Payback: {payback_months} months", showarrow=True, arrowhead=1, yshift=10)

    fig.update_layout(title='Break-even Analysis for Different Scenarios',
                      xaxis_title='Year',
                      yaxis_title='Cumulative Cash Flow (€)')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Payback Periods")
    payback_data = {
        'Scenario': [],
        'Payback Period (months)': [],
    }
    for scenario in results:
        payback = results[scenario]['payback_period']
        payback_text = f"{payback} months" if payback else 'Not within operational life'
        payback_data['Scenario'].append(scenario)
        payback_data['Payback Period (months)'].append(payback_text)

    payback_df = pd.DataFrame(payback_data)
    st.table(payback_df)

    st.subheader("Detailed Financial Projections")
    selected_scenario = st.selectbox("Select a scenario to view detailed projections", options=list(results.keys()))
    df = results[selected_scenario]['data']
    st.write(f"**Scenario:** {selected_scenario}")
    # Remove the index and ensure 'Quarter' and 'Year' are the first columns
    df.reset_index(drop=True, inplace=True)
    df = df[['Quarter', 'Year', 'Net Quarterly Revenue (€)', 'Cumulative Cash Flow (€)']]
    st.dataframe(df.style.format('{:,.2f}'))

    st.markdown("""
    ### Understanding the Business Case

    Investing in battery storage and participating in the aFRR market can provide significant revenue streams.
    By partnering with Flexcity, you can maximize your battery's potential through expert market access and optimized operations.

    - **Capacity Revenue:** Earnings from being available to provide aFRR services.
    - **Activation Revenue:** Earnings from actual energy delivery during activations.
    - **Charging Costs:** Costs incurred from recharging the battery after activations.

    The cumulative cash flow analysis helps you understand when you can expect to recover your initial investment under different market conditions.

    ### Next Steps

    - **Customize Assumptions:** Adjust the parameters to reflect your expectations.
    - **Compare Scenarios:** Analyze how different market trends impact your investment.
    - **Contact Flexcity:** [Get in touch](https://www.flexcity.energy/contact) for a personalized consultation and to learn how we can help you optimize your battery's performance.

    """)

if __name__ == "__main__":
    main()