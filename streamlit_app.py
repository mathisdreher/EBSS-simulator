import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def main():
    # Set page configuration
    st.set_page_config(page_title="Flexcity Battery Revenue Simulator", layout="wide")

    # Flexcity Branding with Veolia Logo
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/48/Veolia_logo.svg", width=200)

    st.title("Estimate Your Battery Revenue with Flexcity in Belgium")

    st.markdown("""
    Welcome to Flexcity's Battery Revenue Simulator. Discover how much revenue your battery can generate
    by participating in the Belgian aFRR (Automatic Frequency Restoration Reserve) market with Flexcity.

    This tool allows you to explore different market scenarios, adjust assumptions, and see how partnering with Flexcity can maximize your investment.

    """)

    # Use tabs for better UX
    tabs = st.tabs(["Battery Specifications", "Operational Parameters", "Financial Parameters", "Market Scenarios", "Results"])

    with tabs[0]:
        st.header("Battery Specifications")

        # Use columns to organize inputs
        col1, col2 = st.columns(2)
        with col1:
            capacity = st.number_input("Battery Capacity (MWh)", min_value=0.1, value=2.0)
            efficiency = st.slider("Round-trip Efficiency (%)", min_value=70, max_value=100, value=90)
        with col2:
            power = st.number_input("Battery Power Rating (MW)", min_value=0.1, value=1.0)
            reserved_capacity_pct = st.slider("Reserved Capacity for Other Uses (%)", min_value=0, max_value=50, value=10)

    with tabs[1]:
        st.header("Operational Parameters")

        col1, col2 = st.columns(2)
        with col1:
            availability = st.slider("Availability (%)", min_value=0, max_value=100, value=95)
            activation_rate = st.slider("Average aFRR Activation Rate (%)", min_value=0, max_value=100, value=15)
        with col2:
            operational_life = st.number_input("Battery Operational Life (years)", min_value=1, value=15)
            # Additional operational parameters can be added here

    with tabs[2]:
        st.header("Financial Parameters")

        battery_cost = st.number_input("Battery Investment Cost (€ per MWh)", min_value=0.0, value=350000.0)
        # Other financial parameters can be added here

    with tabs[3]:
        st.header("Market Scenarios")

        st.markdown("""
        Select a predefined market scenario or create your own custom scenario by adjusting the parameters.
        """)

        scenario_options = ["Custom", "Optimistic", "Base Case", "Pessimistic"]
        selected_scenarios = st.multiselect("Select Scenarios to Display", options=scenario_options, default=["Base Case", "Custom"])

        scenarios = {}
        for scenario in selected_scenarios:
            with st.expander(f"{scenario} Scenario Settings", expanded=(scenario=="Custom")):
                st.write(f"Adjust the parameters for the {scenario} scenario.")

                if scenario == "Custom":
                    initial_electricity_cost = st.number_input("Initial Electricity Cost (€/MWh)", min_value=0.0, value=50.0, key=f"{scenario}_electricity_cost")
                    electricity_price_growth = st.number_input("Annual Electricity Price Growth (%)", value=2.0, key=f"{scenario}_electricity_growth")
                    initial_afrr_capacity_price = st.number_input("Initial aFRR Capacity Price (€/MW/h)", min_value=0.0, value=80.0, key=f"{scenario}_afrr_capacity_price")
                    afrr_capacity_price_growth = st.number_input("Annual aFRR Capacity Price Growth (%)", value=1.8, key=f"{scenario}_afrr_capacity_growth")
                    initial_afrr_activation_price = st.number_input("Initial aFRR Activation Price (€/MWh)", min_value=0.0, value=110.0, key=f"{scenario}_afrr_activation_price")
                    afrr_activation_price_growth = st.number_input("Annual aFRR Activation Price Growth (%)", value=2.2, key=f"{scenario}_afrr_activation_growth")
                else:
                    # Default scenario values
                    if scenario == "Optimistic":
                        initial_electricity_cost = 52.0
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
                        initial_electricity_cost = 48.0
                        electricity_price_growth = 2.5
                        initial_afrr_capacity_price = 75.0
                        afrr_capacity_price_growth = 0.5
                        initial_afrr_activation_price = 105.0
                        afrr_activation_price_growth = 1.0

                    # Allow user to modify default scenario parameters
                    initial_electricity_cost = st.number_input("Initial Electricity Cost (€/MWh)", min_value=0.0, value=initial_electricity_cost, key=f"{scenario}_electricity_cost")
                    electricity_price_growth = st.number_input("Annual Electricity Price Growth (%)", value=electricity_price_growth, key=f"{scenario}_electricity_growth")
                    initial_afrr_capacity_price = st.number_input("Initial aFRR Capacity Price (€/MW/h)", min_value=0.0, value=initial_afrr_capacity_price, key=f"{scenario}_afrr_capacity_price")
                    afrr_capacity_price_growth = st.number_input("Annual aFRR Capacity Price Growth (%)", value=afrr_capacity_price_growth, key=f"{scenario}_afrr_capacity_growth")
                    initial_afrr_activation_price = st.number_input("Initial aFRR Activation Price (€/MWh)", min_value=0.0, value=initial_afrr_activation_price, key=f"{scenario}_afrr_activation_price")
                    afrr_activation_price_growth = st.number_input("Annual aFRR Activation Price Growth (%)", value=afrr_activation_price_growth, key=f"{scenario}_afrr_activation_growth")

                # Store scenario parameters
                scenarios[scenario] = {
                    "initial_electricity_cost": initial_electricity_cost,
                    "electricity_price_growth": electricity_price_growth,
                    "initial_afrr_capacity_price": initial_afrr_capacity_price,
                    "afrr_capacity_price_growth": afrr_capacity_price_growth,
                    "initial_afrr_activation_price": initial_afrr_activation_price,
                    "afrr_activation_price_growth": afrr_activation_price_growth
                }

    with tabs[4]:
        st.header("Results")

        # Calculations

        # Adjust capacity for reserved percentage
        usable_capacity = capacity * (1 - reserved_capacity_pct / 100)

        # Effective power output considering efficiency and availability
        effective_power = min(power, usable_capacity * (efficiency / 100)) * (availability / 100)

        total_investment = capacity * battery_cost

        years = np.arange(1, operational_life + 1)

        # Prepare dataframes for each scenario
        results = {}

        for scenario in scenarios:
            params = scenarios[scenario]

            # Generate price trajectories
            electricity_prices = params["initial_electricity_cost"] * ((1 + params["electricity_price_growth"] / 100) ** (years - 1))
            afrr_capacity_prices = params["initial_afrr_capacity_price"] * ((1 + params["afrr_capacity_price_growth"] / 100) ** (years - 1))
            afrr_activation_prices = params["initial_afrr_activation_price"] * ((1 + params["afrr_activation_price_growth"] / 100) ** (years - 1))

            # Annual calculations
            annual_capacity_revenues = effective_power * afrr_capacity_prices * 24 * 365
            annual_energy_activated = effective_power * (activation_rate / 100) * 24 * 365
            annual_activation_revenues = annual_energy_activated * afrr_activation_prices
            annual_revenues = annual_capacity_revenues + annual_activation_revenues
            annual_energy_charged = annual_energy_activated / (efficiency / 100)
            annual_charging_costs = annual_energy_charged * electricity_prices
            net_annual_revenues = annual_revenues - annual_charging_costs

            cumulative_cash_flow = net_annual_revenues.cumsum() - total_investment
            payback_period = next((year for year, cash in zip(years, cumulative_cash_flow) if cash >= 0), None)

            # Store results
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
                'payback_period': payback_period
            }

        # Display results

        st.subheader("Cumulative Cash Flow Comparison")

        # Prepare data for plotting
        fig = px.line()

        for scenario in results:
            df = results[scenario]['data']
            fig.add_scatter(x=df['Year'], y=df['Cumulative Cash Flow (€)'], mode='lines+markers', name=scenario)

        fig.update_layout(title='Break-even Analysis for Different Scenarios',
                          xaxis_title='Year',
                          yaxis_title='Cumulative Cash Flow (€)')

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Payback Periods")
        payback_df = pd.DataFrame({
            'Scenario': [scenario for scenario in results],
            'Payback Period (years)': [results[scenario]['payback_period'] if results[scenario]['payback_period'] else 'Not within operational life' for scenario in results]
        })

        st.table(payback_df)

        st.subheader("Detailed Financial Projections")

        selected_scenario = st.selectbox("Select a scenario to view detailed projections", options=list(results.keys()))

        df = results[selected_scenario]['data']
        st.write(f"**Scenario:** {selected_scenario}")
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