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

st.write("""Heat Exchangers can deteriorate over time due to off-design operation, fouling, 
scaling, or corrosion. This tool periodically assesses thermal duty, heat transfer coefficients ($U$), 
effectiveness ($\epsilon$), and hydraulic pressure drops ($\Delta P$) for both Shell & Tube and Plate Exchangers.
""")

# ---------------------------------------------------------
# 1. Equipment Selection & Metadata Inputs
# ---------------------------------------------------------
st.write("## Metadata & Operational Configuration")

he_type = st.selectbox(
    "Select Heat Exchanger Type:",
    ["Shell & Tube Heat Exchanger (STHE)", "Plate Heat Exchanger (PHE)"]
)

st.write("### Design Data Inputs (from Test/Spec Reports)")

col1, col2 = st.columns(2)

with col1:
    flow_type = st.selectbox(
        "Flow Configuration:", ["Counterflow", "Parallel"]
    )
    if he_type == "Shell & Tube Heat Exchanger (STHE)":
        N = st.number_input("No. of Shell Side Passes (N)", min_value=1, value=1)
        M = st.number_input("No. of Tube Side Passes (M)", min_value=1, value=1)
    else:
        N = st.number_input("No. of Hot Side Passes", min_value=1, value=1)
        M = st.number_input("No. of Cold Side Passes", min_value=1, value=1)

    Qd = st.number_input(
        "Total Design Heat Duty (kW)", min_value=1.0, value=25623.0, format="%.2f"
    )
    Ud = st.number_input(
        "Overall Heat Transfer Coefficient U_d (Design/Service) (kW/m²-K)",
        min_value=0.001,
        value=7.235 if he_type == "Plate Heat Exchanger (PHE)" else 1.178,
        format="%.4f",
    )
    # --- ADD FOULING MARGIN FIELD HERE ---
    fouling_margin = st.number_input(
        "Design Fouling Margin (%)", min_value=0.0, max_value=50.0, value=15.0, step=1.0, format="%.1f"
    )

# Compute clean theoretical U-value based on margin
U_clean = Ud * (1.0 + (fouling_margin / 100.0))

with col2:
    ΔPh = st.number_input(
        "Hot Fluid Side Pressure Drop Design (bar)", min_value=0.01, value=1.34, format="%.2f"
    )
    ΔPc = st.number_input(
        "Cold Fluid Side Pressure Drop Design (bar)", min_value=0.01, value=0.95, format="%.2f"
    )
    ΔTh = st.number_input("Hot Fluid Temp Range (°C)", min_value=0.01, value=45.0, format="%.2f")
    ΔTc = st.number_input("Cold Fluid Temp Range (°C)", min_value=0.01, value=25.0, format="%.2f")
    lmtdc = st.number_input("Corrected LMTD Design (°C)", min_value=0.01, value=83.8, format="%.2f")

st.write("### Operation Data Inputs")

oc1, oc2, oc3 = st.columns(3)

with oc1:
    Win = st.number_input("Hot Fluid Flow Inlet (kg/hr)", min_value=1.0, value=719800.0, format="%.2f")
    win = st.number_input("Cold Fluid Flow Inlet (kg/hr)", min_value=1.0, value=881150.0, format="%.2f")

with oc2:
    Thin = st.number_input("Hot Fluid Temp Inlet (°C)", min_value=1.0, value=145.0, format="%.2f")
    Thout = st.number_input("Hot Fluid Temp Outlet (°C)", min_value=1.0, value=102.0, format="%.2f")
    Tcin = st.number_input("Cold Fluid Temp Inlet (°C)", min_value=1.0, value=25.5, format="%.2f")
    Tcout = st.number_input("Cold Fluid Temp Outlet (°C)", min_value=1.0, value=49.0, format="%.2f")

with oc3:
    Pin = st.number_input("Hot Fluid Pressure Inlet (bar g)", min_value=0.01, value=4.1, format="%.2f")
    Pout = st.number_input("Hot Fluid Pressure Outlet (bar g)", min_value=0.01, value=2.8, format="%.2f")
    pin = st.number_input("Cold Fluid Pressure Inlet (bar g)", min_value=0.01, value=6.2, format="%.2f")
    pout = st.number_input("Cold Fluid Pressure Outlet (bar g)", min_value=0.01, value=5.1, format="%.2f")

st.write("### Fluid Properties")
fp1, fp2 = st.columns(2)

with fp1:
    Cph = st.number_input("Hot Fluid Specific Heat Capacity (kJ/kg-°C)", min_value=0.0, value=2.847, format="%.5f")
    Cpc = st.number_input("Cold Fluid Specific Heat Capacity (kJ/kg-°C)", min_value=0.0, value=4.187, format="%.5f")

with fp2:
    λh = st.number_input("Latent Heat of Condensation (kJ/kg)", min_value=0.0, value=0.0, format="%.5f")
    λc = st.number_input("Latent Heat of Vaporisation (kJ/kg)", min_value=0.0, value=0.0, format="%.5f")

# ---------------------------------------------------------
# 2. Heat Transfer Area (A) Determination
# ---------------------------------------------------------
st.write("---")
st.write("### Heat Transfer Area (A) Calculation")

if he_type == "Shell & Tube Heat Exchanger (STHE)":
    calculation_mode = st.radio(
        "How do you want to provide the Heat Transfer Area (A) m²?",
        ("Calculate A (Tube Geometry)", "Input A Manually"),
    )

    if calculation_mode == "Calculate A (Tube Geometry)":
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            D = st.number_input("Outer Diameter of Tubes (mm)", min_value=1.0, value=25.4, format="%.2f")
        with ac2:
            n = st.number_input("No. of Tubes", min_value=1, value=460)
        with ac3:
            l = st.number_input("Length of Tubes (mm)", min_value=1, value=7211)
        A = n * math.pi * D * l / 10**6
    else:
        A = st.number_input("Enter Heat Transfer Area (A in m²)", min_value=1.0, value=264.4, format="%.2f")

else:  # Plate Heat Exchanger (PHE)
    calculation_mode = st.radio(
        "How do you want to provide the Heat Transfer Area (A) m²?",
        ("Calculate A (Plate Geometry)", "Input A Manually"),
    )

    if calculation_mode == "Calculate A (Plate Geometry)":
        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1:
            Np = st.number_input("Total Number of Plates (N_p)", min_value=3, value=50)
        with pc2:
            W_p = st.number_input("Effective Plate Width (m)", min_value=0.1, value=0.4, format="%.3f")
        with pc3:
            L_p = st.number_input("Effective Plate Vertical Height (m)", min_value=0.1, value=1.0, format="%.3f")
        with pc4:
            phi = st.number_input("Corrugation Enlargement Factor (φ)", min_value=1.0, value=1.18, format="%.2f")
        
        # Effective thermal plates = Total plates - 2 end plates
        N_thermal = max(1, Np - 2)
        A = N_thermal * (W_p * L_p * phi)
    else:
        A = st.number_input("Enter Effective Plate Surface Area (A in m²)", min_value=1.0, value=22.5, format="%.2f")

st.info(f"**Final Calculated Heat Transfer Area (A):** `{A:.4f} m²`")

# ---------------------------------------------------------
# 3. Thermal & Hydraulic Calculations
# ---------------------------------------------------------
# Duty Calculations
Qh = Win * Cph * (Thin - Thout) / 3600.0  # kW
Qc = win * Cpc * (Tcout - Tcin) / 3600.0  # kW
qs = max(Qh, Qc)

qh = Win * λh / 3600.0
qc = Win * λc / 3600.0
ql = max(qh, qc)

Q = max(qs, ql)

# Pressure drops and Temp ranges
Δph = Pin - Pout
Δpc = pin - pout
Δth = Thin - Thout
Δtc = Tcout - Tcin

# LMTD Calculation
lmtd = 1.0
if flow_type == "Counterflow":
    if Thout <= Tcin or Thin <= Tcout:
        st.error("Counterflow: Invalid Values - Check Input Temperatures")
    else:
        numerator = (Thin - Tcout) - (Thout - Tcin)
        denominator = math.log((Thin - Tcout) / (Thout - Tcin))
        lmtd = numerator / denominator
elif flow_type == "Parallel":
    if Thout <= Tcout or Thin <= Tcin:
        st.error("Parallel flow: Invalid Values - Check Input Temperatures")
    else:
        numerator = (Thin - Tcin) - (Thout - Tcout)
        denominator = math.log((Thin - Tcin) / (Thout - Tcout))
        lmtd = numerator / denominator

# Dimensionless constants P and R
R = (Thin - Thout) / (Tcout - Tcin) if (Tcout > Tcin and Thin > Thout) else 0.1
P = (Tcout - Tcin) / (Thin - Tcin) if (Tcout > Tcin and Thin > Tcin) else 0.1

# Correction Factor F
if he_type == "Plate Heat Exchanger (PHE)":
    f_mode = st.radio(
        "How do you want to provide the Correction Factor (F)?",
        ("Default PHE Factor (F = 0.95)", "Calculate F (Multi-pass PHE)", "Input F Manually"),
    )
else:
    f_mode = st.radio(
        "How do you want to provide the Correction Factor (F)?",
        ("Calculate F", "Input F Manually"),
    )

F = 1.0
if f_mode == "Default PHE Factor (F = 0.95)":
    F = 0.95
elif f_mode == "Calculate F" or f_mode == "Calculate F (Multi-pass PHE)":
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
    F = st.number_input("Enter Correction Factor (F)", min_value=0.01, max_value=1.0, value=0.98 if he_type == "Plate Heat Exchanger (PHE)" else 1.0, format="%.4f")

lmtd_corr = F * lmtd
U = Q / (A * lmtd_corr) if (A * lmtd_corr) > 0 else 0.0

# ---------------------------------------------------------
# Effectiveness & Capacity Ratio Calculation (Fixed for Phase-Change)
# ---------------------------------------------------------
Ch = Win * Cph / 3600.0
Cc = win * Cpc / 3600.0

if λh > 0:
    Cmin = Cc
    Cmax = float("inf")
    r = 0.0
elif λc > 0:
    Cmin = Ch
    Cmax = float("inf")
    r = 0.0
else:
    Cmin = min(Ch, Cc)
    Cmax = max(Ch, Cc)
    r = Cmin / Cmax if Cmax > 0 else 0.0

Tmax = Thin - Tcin
if Thin <= Tcin:
    st.error("Qmax: Invalid Values - Check Input Temperatures")
    Qmax = 1.0
    E = 0.0
else:
    Qmax = Cmin * Tmax
    E = Q / Qmax if Qmax > 0 else 0.0

# Fouling Resistance (Rd)
Rd = (1 / U - 1 / Ud) if (U > 0 and Ud > 0) else 0.0

# ---------------------------------------------------------
# Data Table & Results
# ---------------------------------------------------------
st.write("---")
st.write("### Assessment Results")

table_data = [
    ["Parameters", "Units", "Operation Data", "Design Data"],
    ["Heat Exchanger Type", "-", he_type, he_type],
    ["Duty (Q)", "kW", f"{Q:.2f}", f"{Qd:.2f}"],
    ["Hot Fluid Pressure Drop ΔPh", "bar", f"{Δph:.2f}", f"{ΔPh:.2f}"],
    ["Cold Fluid Pressure Drop ΔPc", "bar", f"{Δpc:.2f}", f"{ΔPc:.2f}"],
    ["Temp Range Hot Fluid", "°C", f"{Δth:.2f}", f"{ΔTh:.2f}"],
    ["Temp Range Cold Fluid", "°C", f"{Δtc:.2f}", f"{ΔTc:.2f}"],
    ["Corrected LMTD", "°C", f"{lmtd_corr:.2f}", f"{lmtdc:.2f}"],
    ["Heat Transfer Coefficient U", "kW/m²-K", f"{U:.3f}", f"{Ud:.3f}"],
]

columns = table_data[0]
data = table_data[1:]
df = pd.DataFrame(data, columns=columns)
st.dataframe(df, use_container_width=True)

res1, res2, res3 = st.columns(3)
res1.metric("Effectiveness (ε)", f"{E:.4f}")
res2.metric("Capacity Ratio (r)", f"{r:.4f}")
res3.metric("Fouling Resistance (Rd)", f"{Rd:.4f} m²K/kW")

# ---------------------------------------------------------
# 4. Context-Aware Groq LLM Diagnostics
# ---------------------------------------------------------
st.write("---")
st.write("### AI Performance Diagnostic Summary")

api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.info("💡 Add your `GROQ_API_KEY` to environment variables or Streamlit secrets for AI diagnostics.")
else:
    if st.button("Generate AI Assessment Summary"):
        with st.spinner("Analyzing operational KPIs with Groq LLM..."):
            try:
                client = Groq(api_key=api_key)

                # Calculate percentage drop from clean baseline
                u_drop_percent = ((U_clean - U) / U_clean) * 100.0 if U_clean > 0 else 0.0

                prompt_content = f"""
You are an expert thermal process engineer. Evaluate the operational metrics of this {he_type}:

Equipment Details & Design Benchmarks:
- Equipment Type: {he_type}
- Flow Configuration: {flow_type} (F = {F:.3f})
- Thermal Duty (Q): Operating = {Q:.2f} kW | Design = {Qd:.2f} kW
- Service Heat Transfer Coeff (U_d): {Ud:.3f} kW/m²-K
- Clean Heat Transfer Coeff (U_clean): {U_clean:.3f} kW/m²-K (includes {fouling_margin:.1f}% Design Fouling Margin)
- Current Operating U-Value (U_op): {U:.3f} kW/m²-K (Thermal Drop vs Clean = {u_drop_percent:.1f}%)
- Hot Side Pressure Drop (ΔPh): Operating = {Δph:.2f} bar | Design = {ΔPh:.2f} bar
- Cold Side Pressure Drop (ΔPc): Operating = {Δpc:.2f} bar | Design = {ΔPc:.2f} bar
- Corrected LMTD: Operating = {lmtd_corr:.2f} °C | Design = {lmtdc:.2f} °C
- Calculated Fouling Resistance (Rd): {Rd:.4f} m²-K/kW
- Thermal Effectiveness (E): {E:.4f}

Diagnostic Instructions:
1. **Diagnostic Summary (3-4 bullet points):**
   - **Fouling Margin Assessment:** Evaluate `U_op` against `U_d` and `U_clean`. If `U_op >= U_d` (drop <= {fouling_margin:.1f}%), explicitly state that performance is within the {fouling_margin:.1f}% design fouling allowance and NO immediate cleaning is required. If `U_op < U_d`, state that the design margin is EXHAUSTED.
   - **Hydraulic Comparison:** Compare operating ΔP against design values to detect flow restrictions or channel clogging.
   - **Maintenance Recommendation:** Recommend specific maintenance actions (e.g., CIP chemical cleaning or plate inspection for PHE; tube rodding/bundle pulling for STHE) ONLY if the fouling margin is exhausted or ΔP is abnormally elevated.

2. **Brief Engineering Insight (1 short paragraph, 2-3 sentences max):**
   - Provide a quick physical explanation connecting the thermal metrics (U-value, LMTD, Rd, Effectiveness, Capacity ratio) to operational root causes (e.g., fluid velocity drops, thermal boundary layer buildup, or bio-fouling vs. scaling behavior).

Maintain an objective, technical tone without fluff or length padding."""

                target_model = "openai/gpt-oss-120b"  # Production model on Groq

                completion = client.chat.completions.create(
                    model=target_model,
                    messages=[
                        {"role": "system", "content": "You are a precise industrial energy efficiency analyst."},
                        {"role": "user", "content": prompt_content},
                    ],
                    temperature=0.1,
                    max_tokens=1000,
                )

                ai_response = completion.choices[0].message.content
                if ai_response:
                    st.markdown(ai_response)
                else:
                    st.warning("Received an empty response from LLM provider.")

            except Exception as e:
                st.error(f"Failed to generate evaluation from Groq API: {e}")