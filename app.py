#!/usr/bin/env python
# coding: utf-8

import math
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from groq import Groq

# ---------------------------------------------------------
# Streamlit Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="ENERGY EFFICIENCY MODULE-HEAT EXCHANGERS", layout="wide"
)

st.title("ENERGY EFFICIENCY MODULE-HEAT EXCHANGERS")
st.subheader("HEAT EXCHANGER PERFORMANCE ASSESSMENT")

st.write("""Heat Exchanger can deteriorate with time, off design operations and other interferences such as fouling, 
scaling, corrosion etc., can affect its performance. It is necessary to assess periodically the heat exchanger performance in
order to maintain them at a high efficiency level.

The objective of performance assessment is to determine the heat exchanger duty, overall heat transfer coefficient, heat 
exchanger effectiveness, process/utility side pressure drop. Any deviation from the design will indicate occurence of fouling.
""")

# ---------------------------------------------------------
# Metadata & User Inputs
# ---------------------------------------------------------
st.write("## Heat Exchanger(Unmixed fluids)-Metadata Information")
st.write("### Design Data Inputs-from Test Reports")

flow_type = st.selectbox(
    "Select the Heat Exchanger Flow type:", ["Counterflow", "Parallel"]
)
N = st.number_input("No.of Shell Side passes", min_value=1, value=1)
M = st.number_input("No.of Tube Side passes", min_value=1, value=1)

Qd = st.number_input(
    "Total Design Heat Duty(KW)", min_value=1.0, value=25623.0, format="%.2f"
)
ΔPh = st.number_input(
    "Hot fluid side pressured drop(bar)",
    min_value=0.01,
    value=1.34,
    format="%.2f",
)
ΔPc = st.number_input(
    "Cold fluid side pressured drop(bar)",
    min_value=0.01,
    value=0.95,
    format="%.2f",
)
ΔTh = st.number_input(
    "Temp.range Hot fluid(°C)", min_value=0.01, value=45.0, format="%.2f"
)
ΔTc = st.number_input(
    "Temp.range Cold fluid(°C)", min_value=0.01, value=25.0, format="%.2f"
)
lmtdc = st.number_input(
    "Corrected LMTD(°C)", min_value=0.01, value=83.8, format="%.2f"
)
Ud = st.number_input(
    "Overall Heat Transfer Coefficient U (KW/m2-K)",
    min_value=0.001,
    value=1.178,
    format="%.4f",
)

st.write("### Operation Data Inputs")

Win = st.number_input(
    "Hot fluid flow-Inlet(kg/hr)", min_value=1.0, value=719800.0, format="%.2f"
)
win = st.number_input(
    "Cold fluid flow-Inlet(kg/hr)", min_value=1.0, value=881150.0, format="%.2f"
)
Thin = st.number_input(
    "Hot fluid temp.-Inlet(°C)", min_value=1.0, value=145.0, format="%.2f"
)
Thout = st.number_input(
    "Hot fluid temp.-Outlet(°C)", min_value=1.0, value=102.0, format="%.2f"
)
Tcin = st.number_input(
    "Cold fluid temp.-Inlet(°C)", min_value=1.0, value=25.5, format="%.2f"
)
Tcout = st.number_input(
    "Cold fluid temp.-Outlet(°C)", min_value=1.0, value=49.0, format="%.2f"
)
Pin = st.number_input(
    "Hot fluid pressure-Inlet(bar g)",
    min_value=0.01,
    value=4.1,
    format="%.2f",
)
Pout = st.number_input(
    "Hot fluid pressure-Outlet(bar g)",
    min_value=0.01,
    value=2.8,
    format="%.2f",
)
pin = st.number_input(
    "Cold fluid pressure-Inlet(bar g)",
    min_value=0.01,
    value=6.2,
    format="%.2f",
)
pout = st.number_input(
    "Cold fluid pressure-Outlet(bar g)",
    min_value=0.01,
    value=5.1,
    format="%.2f",
)

st.write("### Fluid properties")
Cph = st.number_input(
    "Hot fluid specific heat capacity(KJ/kg°C)",
    min_value=0.0,
    value=2.847,
    format="%.5f",
)
Cpc = st.number_input(
    "Cold fluid specific heat capacity(KJ/kg°C)",
    min_value=0.0,
    value=4.187,
    format="%.5f",
)
λh = st.number_input(
    "Latent heat of condensation of a hot condensing vapour(KJ/kg)",
    min_value=0.0,
    format="%.5f",
)
λc = st.number_input(
    "Latent heat of Vaporisation(KJ/kg)", min_value=0.0, format="%.5f"
)

# ---------------------------------------------------------
# Heat Exchanger Area (A)
# ---------------------------------------------------------
calculation_mode = st.radio(
    "How do you want to provide the Heat Transfer Area (A) m²?",
    ("Calculate A", "Input A Manually"),
)

if calculation_mode == "Calculate A":
    D = st.number_input(
        "Outer Diameter of tubes(mm)", min_value=1.0, value=25.4, format="%.2f"
    )
    n = st.number_input("No.of Tubes", min_value=1, value=460)
    l = st.number_input("Length of tubes(mm)", min_value=1, value=7211)
    A = n * math.pi * D * l / 10**6
elif calculation_mode == "Input A Manually":
    A = st.number_input(
        "Enter the Heat Transfer Area (A, in m²)",
        min_value=1.0,
        value=264.4,
        format="%.2f",
    )

st.write(f"Final Heat Transfer Area (A): {A:.4f} m²")

# ---------------------------------------------------------
# Thermal & Hydraulic Calculations
# ---------------------------------------------------------
Qh = Win * Cph * (Thin - Thout) / 3600  # kW
Qc = win * Cpc * (Tcout - Tcin) / 3600  # kW
qs = max(Qh, Qc)

qh = Win * λh / 3600
qc = Win * λc / 3600
ql = max(qh, qc)

Q = max(qs, ql)

Δph = Pin - Pout
Δpc = pin - pout

Δth = Thin - Thout
Δtc = Tcout - Tcin

# LMTD Calculation
lmtd = 1.0
if flow_type == "Counterflow":
    if Thout <= Tcin or Thin <= Tcout:
        st.error(
            "Counterflow: Invalid Values - Check Input values of Temperatures"
        )
    else:
        numerator = (Thin - Tcout) - (Thout - Tcin)
        denominator = math.log((Thin - Tcout) / (Thout - Tcin))
        lmtd = numerator / denominator
elif flow_type == "Parallel":
    if Thout <= Tcout or Thin <= Tcin:
        st.error(
            "Parallel flow: Invalid Values - Check Input values of Temperatures"
        )
    else:
        numerator = (Thin - Tcin) - (Thout - Tcout)
        denominator = math.log((Thin - Tcin) / (Thout - Tcout))
        lmtd = numerator / denominator

# Dimensionless constants P and R
R = (
    (Thin - Thout) / (Tcout - Tcin)
    if (Tcout > Tcin and Thin > Thout)
    else 0.1
)
P = (Tcout - Tcin) / (Thin - Tcin) if (Tcout > Tcin and Thin > Tcin) else 0.1

# Correction Factor F
f_mode = st.radio(
    "How do you want to provide the Correction Factor (F)?",
    ("Calculate F", "Input F Manually"),
)

F = 1.0
if f_mode == "Calculate F":
    try:
        if R != 1:
            α = ((1 - R * P) / (1 - P)) ** (1 / N)
            S = (α - 1) / (α - R)
            num = math.sqrt(R**2 + 1) * math.log((1 - S) / (1 - R * S))
            den_term = (2 - S * (R + 1 - math.sqrt(R**2 + 1))) / (
                2 - S * (R + 1 + math.sqrt(R**2 + 1))
            )
            den = (R - 1) * math.log(den_term)
            F = num / den
        else:
            S = P / (N * (N - 1) * P) if N > 1 else P
            num = S * math.sqrt(2)
            den_term = (2 - S * (2 - math.sqrt(2))) / (
                2 - S * (2 + math.sqrt(2))
            )
            den = (1 - S) * math.log(den_term)
            F = num / den
    except Exception:
        F = 1.0
elif f_mode == "Input F Manually":
    F = st.number_input(
        "Enter Correction Factor (F)",
        min_value=0.01,
        max_value=1.0,
        value=1.0,
        format="%.4f",
    )

lmtd_corr = F * lmtd
U = Q / (A * lmtd_corr) if (A * lmtd_corr) > 0 else 0.0

# ---------------------------------------------------------
# Heat Exchanger Effectiveness & Capacity Ratio Calculation
# ---------------------------------------------------------

# 1. Calculate sensible heat capacity rates (kW/°C)
Ch = Win * Cph / 3600.0
Cc = win * Cpc / 3600.0

# 2. Account for phase change (condensing steam or boiling fluid)
if λh > 0:
    # Hot fluid condenses (isothermal), C_hot -> infinity
    Cmin = Cc
    Cmax = float("inf")
    r = 0.0
elif λc > 0:
    # Cold fluid boils (isothermal), C_cold -> infinity
    Cmin = Ch
    Cmax = float("inf")
    r = 0.0
else:
    # Standard sensible heat exchange
    Cmin = min(Ch, Cc)
    Cmax = max(Ch, Cc)
    r = Cmin / Cmax if Cmax > 0 else 0.0

# 3. Calculate Maximum Heat Transfer & Effectiveness
Tmax = Thin - Tcin

if Thin <= Tcin:
    st.error("Qmax: Invalid Values - Check Input values of Temperatures")
    Qmax = 1.0
    E = 0.0
else:
    Qmax = Cmin * Tmax
    E = Q / Qmax if Qmax > 0 else 0.0

# Display results in Streamlit
st.markdown(f"**Effectiveness of Heat Exchanger ($\epsilon$):** `{E:.4f}`")
st.markdown(f"**Heat Capacity Ratio ($r$):** `{r:.4f}`")

# Fouling Factor
Rd = (1 / U - 1 / Ud) if (U > 0 and Ud > 0) else 0.0

# ---------------------------------------------------------
# Data Table
# ---------------------------------------------------------
st.write("### Results")

table_data = [
    ["Parameters", "Units", "Operation Data", "Design Data"],
    ["Duty(Q)", "KW", f"{Q:.2f}", f"{Qd:.2f}"],
    ["Hot fluid side Pressure drop ΔPh", "bar", f"{Δph:.2f}", f"{ΔPh:.2f}"],
    ["Cold fluid side Pressure drop ΔPc", "bar", f"{Δpc:.2f}", f"{ΔPc:.2f}"],
    ["Temperature Range Hot fluid", "°C", f"{Δth:.2f}", f"{ΔTh:.2f}"],
    ["Temperature Range Cold fluid", "°C", f"{Δtc:.2f}", f"{ΔTc:.2f}"],
    ["Corrected LMTD ", "°C", f"{lmtd_corr:.2f}", f"{lmtdc:.2f}"],
    ["Heat Transfer Coefficient U", "KW/m2-K", f"{U:.3f}", f"{Ud:.3f}"],
]

columns = table_data[0]
data = table_data[1:]
df = pd.DataFrame(data, columns=columns)
st.dataframe(df)

st.markdown(f"**Fouling Factor ($R_d$):** `{Rd:.4f} m²K/kW`")
st.markdown(f"**Effectiveness ($\epsilon$):** `{E:.2f}`")

# ---------------------------------------------------------
# Groq LLM Evaluation Integration
# ---------------------------------------------------------
st.write("---")
st.write("### AI Performance Diagnostic Summary")

# Retrieve API key securely from environment or secrets
api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.info(
        "💡 Add your `GROQ_API_KEY` to environment variables or Streamlit secrets to generate automated LLM diagnostics."
    )
else:
    if st.button("Generate AI Assessment Summary"):
        with st.spinner("Analyzing operational KPIs..."):
            try:
                # Setup Groq Client
                client = Groq(api_key=api_key)

                # Prepare deterministic structured prompt with KPIs
                prompt_content = f"""
You are an expert chemical process and mechanical engineer specializing in thermal equipment diagnostics.

Evaluate the following Heat Exchanger operational metrics against design benchmarks:

Operational Summary:
- Flow Configuration: {flow_type}
- Heat Duty (Q): Operating = {Q:.2f} kW | Design = {Qd:.2f} kW
- Heat Transfer Coefficient (U): Operating = {U:.3f} kW/m²-K | Design = {Ud:.3f} kW/m²-K
- Hot Side Pressure Drop (ΔPh): Operating = {Δph:.2f} bar | Design = {ΔPh:.2f} bar
- Cold Side Pressure Drop (ΔPc): Operating = {Δpc:.2f} bar | Design = {ΔPc:.2f} bar
- Corrected LMTD: Operating = {lmtd_corr:.2f} °C | Design = {lmtdc:.2f} °C
- Calculated Fouling Factor (Rd): {Rd:.4f} m²-K/kW
- Heat Exchanger Effectiveness (E): {E:.2f}

Instructions:
1. Provide a concise, deterministic 3-to-4 bullet point technical summary evaluating the performance.
2. Explicitly note thermal degradation (U-value drop), hydraulic deviations (pressure drop changes), and fouling severity.
3. Recommend specific maintenance actions (e.g., thermal cleaning, backflushing, inspection) if performance has deteriorated.
4. Keep the tone objective, analytical, and professional.
"""

                # Query Groq API
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise industrial energy efficiency analyst.",
                        },
                        {"role": "user", "content": prompt_content},
                    ],
                    temperature=0.1,  # Low temperature for deterministic output
                    max_tokens=1000,
                )

                # Output response
                st.markdown(completion.choices[0].message.content)

            except Exception as e:
                st.error(f"Failed to generate evaluation from Groq API: {e}")