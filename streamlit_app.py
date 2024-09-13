import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Flexcity Branding with Veolia Logo
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/48/Veolia_logo.svg", width=200)
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

    st.sidebar.header("Financial Parameters")
    battery_cost = st.sidebar.number_input("Battery Investment Cost (€ per MWh)", min_value=0.0, value=400000.0)
    operational_life = st.sidebar.number_input("Battery Operational Life (years)", min_value=1, value=10)

    st.sidebar.header("Operational Parameters")
    # Operational conditions
    availability = st.sidebar.slider("Availability (%)", min_value=0, max_value=100, value=95)
    activation_rate = st.sidebar.slider("Average aFRR Activation Rate (%)", min_value=0, max_value=100, value=10)

    st.sidebar.header("Electricity Price Assumptions")
    # Electricity price evolution
    initial_electricity_cost = st.sidebar.number_input("Initial Electricity Cost (€/MWh)", min_value=0.0, value=50.0)
    annual_electricity_price_change = st.sidebar.number_input("Annual Electricity Price Change (%)", min_value=-100.0, max_value=100.0, value=2.0)

    st.sidebar.header("aFRR Price Assumptions")
    # aFRR price evolution
    initial_afrr_capacity_price = st.sidebar.number_input("Initial aFRR Capacity Price (€/MW/h)", min_value=0.0, value=75.0)
    annual_afrr_capacity_price_change = st.sidebar.number_input("Annual aFRR Capacity Price Change (%)", min_value=-100.0, max_value=100.0, value=1.0)
    initial_afrr_activation_price = st.sidebar.number_input("Initial aFRR Activation Price (€/MWh)", min_value=0.0, value=100.0)
    annual_afrr_activation_price_change = st.sidebar.number_input("Annual aFRR Activation Price Change (%)", min_value=-100.0, max_value=100.0, value=1.5)

    # Adjust capacity for reserved percentage
    usable_capacity = capacity * (1 - reserved_capacity_pct / 100)

    # Effective power output considering efficiency and availability
    effective_power = min(power, usable_capacity * (efficiency / 100)) * (availability / 100)

    # Initialize lists to store yearly data
    years = np.arange(1, operational_life + 1)
    annual_capacity_revenues = []
    annual_activation_revenues = []
    annual_charging_costs = []
    net_annual_revenues = []
    cumulative_cash_flow = []

    total_investment = capacity * battery_cost
    cumulative_cash = -total_investment  # Initial investment

    # Calculate prices over the years
    electricity_prices = initial_electricity_cost * ((1 + annual_electricity_price_change / 100) ** (years - 1))
    afrr_capacity_prices = initial_afrr_capacity_price * ((1 + annual_afrr_capacity_price_change / 100) ** (years - 1))
    afrr_activation_prices = initial_afrr_activation_price * ((1 + annual_afrr_activation_price_change / 100) ** (years - 1))

    for i in range(operational_life):
        # Annual capacity revenue
        annual_capacity_revenue = effective_power * afrr_capacity_prices[i] * 24 * 365
        # Annual activation revenue
        annual_energy_activated = effective_power * (activation_rate / 100) * 24 * 365
        annual_activation_revenue = annual_energy_activated * afrr_activation_prices[i]
        # Total annual revenue
        annual_revenue = annual_capacity_revenue + annual_activation_revenue
        # Annual charging cost
        annual_energy_charged = annual_energy_activated / (efficiency / 100)
        annual_charging_cost = annual_energy_charged * electricity_prices[i]
        # Net annual revenue
        net_annual_revenue = annual_revenue - annual_charging_cost
        # Update cumulative cash flow
        cumulative_cash += net_annual_revenue

        # Append to lists
        annual_capacity_revenues.append(annual_capacity_revenue)
        annual_activation_revenues.append(annual_activation_revenue)
        annual_charging_costs.append(annual_charging_cost)
        net_annual_revenues.append(net_annual_revenue)
        cumulative_cash_flow.append(cumulative_cash)

    # Calculate payback period
    payback_period = None
    for i, cash in enumerate(cumulative_cash_flow):
        if cash >= 0:
            payback_period = years[i]
            break

    # Prepare DataFrame for display
    data = {
        'Year': years,
        'Electricity Price (€/MWh)': electricity_prices,
        'aFRR Capacity Price (€/MW/h)': afrr_capacity_prices,
        'aFRR Activation Price (€/MWh)': afrr_activation_prices,
        'Annual Capacity Revenue (€)': annual_capacity_revenues,
        'Annual Activation Revenue (€)': annual_activation_revenues,
        'Annual Charging Cost (€)': annual_charging_costs,
        'Net Annual Revenue (€)': net_annual_revenues,
        'Cumulative Cash Flow (€)': cumulative_cash_flow
    }
    df = pd.DataFrame(data)

    # Display Results
    st.subheader("Your Estimated Revenues and Costs Over Operational Life")
    st.dataframe(df.style.format({'Electricity Price (€/MWh)': '{:,.2f}',
                                  'aFRR Capacity Price (€/MW/h)': '{:,.2f}',
                                  'aFRR Activation Price (€/MWh)': '{:,.2f}',
                                  'Annual Capacity Revenue (€)': '{:,.2f}',
                                  'Annual Activation Revenue (€)': '{:,.2f}',
                                  'Annual Charging Cost (€)': '{:,.2f}',
                                  'Net Annual Revenue (€)': '{:,.2f}',
                                  'Cumulative Cash Flow (€)': '{:,.2f}'}))

    st.subheader("ROI Analysis")
    st.markdown(f"""
    - **Total Investment Cost:** €{total_investment:,.2f}
    - **Payback Period:** {payback_period if payback_period else 'Not within operational life'} years
    """)

    # Break-even Analysis Graph
    fig, ax = plt.subplots()
    ax.plot(years, cumulative_cash_flow, marker='o', linestyle='-')
    ax.axhline(0, color='gray', linewidth=0.8)
    ax.set_xlabel('Years')
    ax.set_ylabel('Cumulative Cash Flow (€)')
    ax.set_title('Break-even Analysis with Price Evolution')
    ax.grid(True)

    st.pyplot(fig)

    st.markdown("""
    ### Why Partner with Flexcity?

    - **Maximize Your Revenue:** Flexcity optimizes your battery operations to capture the highest possible revenue.
    - **Expert Market Access:** With deep knowledge of the Belgian energy market and Elia's regulations, we navigate the complexities for you.
    - **End-to-End Support:** From installation to market participation, Flexcity provides comprehensive support.

    ### Get in Touch

    Interested in unlocking your battery's full potential? [Contact us](https://www.flexcity.energy/contact) for a personalized consultation.
    """)

if __name__ == "__main__":
    main()