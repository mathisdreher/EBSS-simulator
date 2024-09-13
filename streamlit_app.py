import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import optimize
import json
import io

# Set locale for currency formatting
import locale
locale.setlocale(locale.LC_ALL, '')

# Function to calculate NPV
def calculate_npv(rate, cash_flows):
    return np.npv(rate, cash_flows)

# Function to calculate IRR
def calculate_irr(cash_flows):
    return np.irr(cash_flows)

# Cache function to optimize performance
@st.cache(allow_output_mutation=True)
def load_real_market_data():
    # Placeholder function to simulate loading real market data
    # Replace with actual API calls to fetch real data
    # For demonstration, we'll use fixed data
    data = {
        'electricity_prices': pd.Series([50 + i*0.5 for i in range(15)]),
        'afrr_capacity_prices': pd.Series([80 + i*0.3 for i in range(15)]),
        'afrr_activation_prices': pd.Series([110 + i*0.4 for i in range(15)]),
    }
    return data

def main():
    # Set page configuration
    st.set_page_config(page_title="Flexcity Battery Revenue Simulator", layout="wide")

    # Load translations
    with open('translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Accessibility: Offer language selection (English, French, Dutch)
    language_options = ["English", "Français", "Nederlands"]
    language = st.sidebar.selectbox(translations["English"]["Select Language / Sélectionnez la langue / Selecteer Taal"], language_options)

    # Translation dictionary for multi-language support
    t = translations[language]

    # Load real market data (Placeholder function)
    real_market_data = load_real_market_data()

    # Use tabs for better UX
    tabs = st.tabs([t["Battery Specifications"], t["Operational Parameters"], t["Financial Parameters"], t["Market Scenarios"], t["Results"]])

    with tabs[0]:
        st.header(t["Battery Specifications"])

        # Use columns to organize inputs
        col1, col2 = st.columns(2)
        with col1:
            capacity = st.number_input(t["Battery Capacity (MWh)"], min_value=0.1, value=2.0)
            efficiency = st.slider(t["Round-trip Efficiency (%)"], min_value=70, max_value=100, value=90)
        with col2:
            power = st.number_input(t["Battery Power Rating (MW)"], min_value=0.1, value=1.0)
            reserved_capacity_pct = st.slider(t["Reserved Capacity for Other Uses (%)"], min_value=0, max_value=50, value=10)

        # Input validation
        if capacity <= 0:
            st.error(t["Error"] + ": " + t["Battery Capacity (MWh)"] + " > 0")
            st.stop()
        if power <= 0:
            st.error(t["Error"] + ": " + t["Battery Power Rating (MW)"] + " > 0")
            st.stop()
        if efficiency <= 0 or efficiency > 100:
            st.error(t["Error"] + ": " + t["Round-trip Efficiency (%)"] + " between 1 and 100")
            st.stop()

    with tabs[1]:
        st.header(t["Operational Parameters"])

        col1, col2 = st.columns(2)
        with col1:
            availability = st.slider(t["Availability (%)"], min_value=0, max_value=100, value=95)
            activation_rate = st.slider(t["Average aFRR Activation Rate (%)"], min_value=0, max_value=100, value=15)
        with col2:
            operational_life = st.number_input(t["Battery Operational Life (years)"], min_value=1, value=15)
            # Additional operational parameters can be added here

        if availability < 0 or availability > 100:
            st.error(t["Error"] + ": " + t["Availability (%)"] + " between 0 and 100")
            st.stop()
        if activation_rate < 0 or activation_rate > 100:
            st.error(t["Error"] + ": " + t["Average aFRR Activation Rate (%)"] + " between 0 and 100")
            st.stop()

    with tabs[2]:
        st.header(t["Financial Parameters"])

        battery_cost = st.number_input(t["Battery Investment Cost (€ per MWh)"], min_value=0.0, value=350000.0)
        # Other financial parameters can be added here

    with tabs[3]:
        st.header(t["Market Scenarios"])

        st.markdown(t["Select predefined market scenarios or create your own custom scenario by adjusting the parameters."])

        scenario_options = [t["Custom"], t["Optimistic"], t["Base Case"], t["Pessimistic"]]
        selected_scenarios = st.multiselect(t["Select Scenarios to Display"], options=scenario_options, default=[t["Base Case"], t["Custom"]])

        scenarios = {}
        for scenario in selected_scenarios:
            scenario_key = [key for key, value in t.items() if value == scenario][0]
            with st.expander(f"{scenario} {t['Scenario']} {t['Settings']}", expanded=(scenario==t["Custom"])):
                st.write(f"{t['Adjust the parameters for the']} {scenario.lower()} {t['scenario.']}")

                if scenario == t["Custom"]:
                    initial_electricity_cost = st.number_input(t["Initial Electricity Cost (€/MWh)"], min_value=0.0, value=real_market_data['electricity_prices'][0], key=f"{scenario}_electricity_cost")
                    electricity_price_growth = st.number_input(t["Annual Electricity Price Growth (%)"], value=2.0, key=f"{scenario}_electricity_growth")
                    initial_afrr_capacity_price = st.number_input(t["Initial aFRR Capacity Price (€/MW/h)"], min_value=0.0, value=real_market_data['afrr_capacity_prices'][0], key=f"{scenario}_afrr_capacity_price")
                    afrr_capacity_price_growth = st.number_input(t["Annual aFRR Capacity Price Growth (%)"], value=1.8, key=f"{scenario}_afrr_capacity_growth")
                    initial_afrr_activation_price = st.number_input(t["Initial aFRR Activation Price (€/MWh)"], min_value=0.0, value=real_market_data['afrr_activation_prices'][0], key=f"{scenario}_afrr_activation_price")
                    afrr_activation_price_growth = st.number_input(t["Annual aFRR Activation Price Growth (%)"], value=2.2, key=f"{scenario}_afrr_activation_growth")
                else:
                    # Default scenario values
                    if scenario == t["Optimistic"]:
                        initial_electricity_cost = real_market_data['electricity_prices'][0] * 1.05
                        electricity_price_growth = 1.2
                        initial_afrr_capacity_price = real_market_data['afrr_capacity_prices'][0] * 1.05
                        afrr_capacity_price_growth = 2.5
                        initial_afrr_activation_price = real_market_data['afrr_activation_prices'][0] * 1.05
                        afrr_activation_price_growth = 3.0
                    elif scenario == t["Base Case"]:
                        initial_electricity_cost = real_market_data['electricity_prices'][0]
                        electricity_price_growth = 1.8
                        initial_afrr_capacity_price = real_market_data['afrr_capacity_prices'][0]
                        afrr_capacity_price_growth = 1.8
                        initial_afrr_activation_price = real_market_data['afrr_activation_prices'][0]
                        afrr_activation_price_growth = 2.2
                    elif scenario == t["Pessimistic"]:
                        initial_electricity_cost = real_market_data['electricity_prices'][0] * 0.95
                        electricity_price_growth = 2.5
                        initial_afrr_capacity_price = real_market_data['afrr_capacity_prices'][0] * 0.95
                        afrr_capacity_price_growth = 0.5
                        initial_afrr_activation_price = real_market_data['afrr_activation_prices'][0] * 0.95
                        afrr_activation_price_growth = 1.0

                    # Allow user to modify default scenario parameters
                    initial_electricity_cost = st.number_input(t["Initial Electricity Cost (€/MWh)"], min_value=0.0, value=initial_electricity_cost, key=f"{scenario}_electricity_cost")
                    electricity_price_growth = st.number_input(t["Annual Electricity Price Growth (%)"], value=electricity_price_growth, key=f"{scenario}_electricity_growth")
                    initial_afrr_capacity_price = st.number_input(t["Initial aFRR Capacity Price (€/MW/h)"], min_value=0.0, value=initial_afrr_capacity_price, key=f"{scenario}_afrr_capacity_price")
                    afrr_capacity_price_growth = st.number_input(t["Annual aFRR Capacity Price Growth (%)"], value=afrr_capacity_price_growth, key=f"{scenario}_afrr_capacity_growth")
                    initial_afrr_activation_price = st.number_input(t["Initial aFRR Activation Price (€/MWh)"], min_value=0.0, value=initial_afrr_activation_price, key=f"{scenario}_afrr_activation_price")
                    afrr_activation_price_growth = st.number_input(t["Annual aFRR Activation Price Growth (%)"], value=afrr_activation_price_growth, key=f"{scenario}_afrr_activation_growth")

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
        st.header(t["Results"])

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

            # Financial Metrics
            discount_rate = 0.05  # 5% discount rate
            cash_flows = [-total_investment] + net_annual_revenues.tolist()
            npv = calculate_npv(discount_rate, cash_flows)
            irr = calculate_irr(cash_flows)

            # Store results
            df = pd.DataFrame({
                t['Year']: years,
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
                'npv': npv,
                'irr': irr
            }

        # Display results

        st.subheader(t["Cumulative Cash Flow Comparison"])

        # Prepare data for plotting
        fig = go.Figure()

        for scenario in results:
            df = results[scenario]['data']
            fig.add_trace(go.Scatter(
                x=df[t['Year']],
                y=df['Cumulative Cash Flow (€)'],
                mode='lines+markers',
                name=scenario
            ))

        fig.update_layout(title=t['Break-even Analysis for Different Scenarios'],
                          xaxis_title=t['Year'],
                          yaxis_title=t['Cumulative Cash Flow (€)'])

        st.plotly_chart(fig, use_container_width=True)

        st.subheader(t["Payback Periods"])
        payback_data = {
            t['Scenario']: [],
            t['Payback Period (years)']: [],
            t['NPV at 5% Discount Rate']: [],
            t['IRR']: []
        }
        for scenario in results:
            payback = results[scenario]['payback_period']
            npv = results[scenario]['npv']
            irr = results[scenario]['irr']
            payback_text = f"{payback}" if payback else t['Not within operational life']
            npv_text = f"€{npv:,.2f}"
            irr_text = f"{irr * 100:.2f}%" if irr is not None else "N/A"
            payback_data[t['Scenario']].append(scenario)
            payback_data[t['Payback Period (years)']].append(payback_text)
            payback_data[t['NPV at 5% Discount Rate']].append(npv_text)
            payback_data[t['IRR']].append(irr_text)

        payback_df = pd.DataFrame(payback_data)
        st.table(payback_df)

        st.subheader(t["Detailed Financial Projections"])

        selected_scenario = st.selectbox(t["Select a scenario to view detailed projections"], options=list(results.keys()))

        df = results[selected_scenario]['data']
        st.write(f"**{t['Scenario']}:** {selected_scenario}")
        st.dataframe(df.style.format('{:,.2f}'))

        # Data Export and Sharing
        st.subheader(t["Data Export and Sharing"])
        export_format = st.selectbox(t["Select export format"], ["CSV", "Excel"])
        if export_format == "CSV":
            # Export all scenarios
            combined_df = pd.concat([results[scenario]['data'].assign(Scenario=scenario) for scenario in results])
            csv = combined_df.to_csv(index=False).encode('utf-8')
            st.download_button(label=t["Download CSV"], data=csv, file_name='all_scenarios_financial_projections.csv', mime='text/csv')
        else:
            combined_df = pd.concat([results[scenario]['data'].assign(Scenario=scenario) for scenario in results])
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for scenario in results:
                    results[scenario]['data'].to_excel(writer, sheet_name=scenario, index=False)
                writer.save()
                processed_data = output.getvalue()
            st.download_button(label=t["Download Excel"], data=processed_data, file_name='all_scenarios_financial_projections.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        st.markdown(f"""
        ### {t["Understanding the Business Case"]}

        Investing in battery storage and participating in the aFRR market can provide significant revenue streams.
        By partnering with Flexcity, you can maximize your battery's potential through expert market access and optimized operations.

        - **Capacity Revenue:** Earnings from being available to provide aFRR services.
        - **Activation Revenue:** Earnings from actual energy delivery during activations.
        - **Charging Costs:** Costs incurred from recharging the battery after activations.

        The cumulative cash flow analysis helps you understand when you can expect to recover your initial investment under different market conditions.

        ### {t["Next Steps"]}

        - **Customize Assumptions:** Adjust the parameters to reflect your expectations.
        - **Compare Scenarios:** Analyze how different market trends impact your investment.
        - **{t["Contact Flexcity"]}:** [Get in touch](https://www.flexcity.energy/contact) for a personalized consultation and to learn how we can help you optimize your battery's performance.

        """)

    # Accessibility and Localization: Provide an option to enlarge text
    if st.sidebar.checkbox(t["Enlarge Text"]):
        st.markdown("""
        <style>
        body {
            font-size: 18px;
        }
        </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()