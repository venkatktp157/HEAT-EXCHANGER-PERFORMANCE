# Heat Exchanger Energy Efficiency & LLM Diagnostics Module

An interactive Streamlit application designed for process and thermal engineers to evaluate shell-and-tube / cross-flow heat exchanger performance against design parameters, enhanced with AI-driven diagnostic summaries via the Groq API.

## Features

- **Thermal & Hydraulic Calculations:** Automatically computes Heat Duty ($Q$), Corrected LMTD ($LMTD_{corr}$), Overall Heat Transfer Coefficient ($U$), Pressure Drops ($\Delta P$), Effectiveness ($\epsilon$), and Fouling Factor ($R_d$).
- **Flexible Area & Correction Inputs:** Compute heat transfer area ($A$) and correction factor ($F$) automatically or enter them manually.
- **Design vs. Operational Comparison:** Tabular side-by-side comparison of test/design metrics against real-time operational data.
- **Automated AI Performance Summaries:** Connects to Groq (`openai/gpt-oss-120b` model) to provide deterministic, expert-level diagnostic summaries highlighting thermal degradation, pressure drop anomalies, and recommended maintenance actions.

## Installation

1. **Clone the repository:**

   ```bash

   git clone [https://github.com/your-username/heat-exchanger-module.git](https://github.com/your-username/heat-exchanger-module.git)   
   cd heat-exchanger-module