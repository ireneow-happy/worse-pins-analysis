# Wafer Probe Shift Analysis (Streamlit App)

This app analyzes probe shift directions and proximity-to-pad-rim issues for wafer probing data.

## 📥 Features
- Determine dominant shift direction (Up, Down, Left, Right)
- Identify probes with high tendency to land near pad rim
- Export results to CSV
- Upload Excel (.xlsx) files directly

## 📐 Calculations
- **Shift Direction** is determined by the minimum of Prox Up/Down/Left/Right
- **On Rim**: A probe is considered on pad rim if any Prox value = 0
- **Dominant %**: Ratio of dominant shift direction to total measurements
- **Rim %**: Ratio of on-rim events to total measurements

## 🏁 How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📂 Input Format
Excel file must contain columns:
- `DUT#`, `Pad #`, `Prox Up`, `Prox Down`, `Prox Left`, `Prox Right`
