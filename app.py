import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# --- PAGE CONFIG ---
st.set_page_config(page_title="BPCL NIP/UIP Automation", layout="wide")
st.title("⛽ BPCL NIP/UIP Engineering Automation (Nashik Territory)")

# --- INPUTS ---
with st.sidebar:
    st.header("1. Site Dimensions")
    frontage = st.number_input("Frontage (m)", value=60.0)
    depth = st.number_input("Depth (m)", value=70.0)
    fill_depth = st.number_input("Avg Filling Depth (m)", value=1.0)
    
    st.header("2. NIP/UIP Factors")
    f1 = st.number_input("Factor 1 (Market/Service)", value=1.145, format="%.3f")
    f2 = st.number_input("Factor 2 (Taxes/Contingency)", value=1.025, format="%.3f")

# --- CORE CALCULATIONS (Civil & Statutory) ---
total_area = frontage * depth
wall_rm = (2 * depth) + frontage + (frontage - 30) # Precise wall logic minus 30m openings
bldg_base_cost = 1403674.0 # From B0 Standard
rvi_base_cost = 1443133.0  # From RVI Rates sheet

# --- NIP CATEGORY MAPPING ---
# These match the "Sub Heads" in your NIP_UIP_Entry.csv
nip_data = [
    {"Sub Head": "Land Development", "Base Amount": (total_area * fill_depth * 344.0) + (wall_rm * 4540.71)},
    {"Sub Head": "RO Premise (Driveway/Misc)", "Base Amount": (total_area * 646.44) + 250000.0},
    {"Sub Head": "Sales Building (B0 Type)", "Base Amount": bldg_base_cost},
    {"Sub Head": "Tanks & Pipelines (Standard)", "Base Amount": 916000.0}, # Estimated standard for 15+20KL
    {"Sub Head": "Canopy", "Base Amount": 2292290.0},
    {"Sub Head": "Electrical Equipments", "Base Amount": 150762.15},
    {"Sub Head": "RVI & Signages", "Base Amount": rvi_base_cost},
    {"Sub Head": "Approach Road (BPCL Owned)", "Base Amount": 504429.75},
]

# Create DataFrame
df_nip = pd.DataFrame(nip_data)

# Apply Factors
df_nip['Factor 1'] = f1
df_nip['Factor 2'] = f2
df_nip['Final Amount'] = df_nip['Base Amount'] * f1 * f2

# --- UI LAYOUT ---
tab1, tab2, tab3 = st.tabs(["📋 NIP/UIP Summary", "📐 Layout Drawing", "🔍 Detail BOQ"])

with tab1:
    st.subheader("Investment Breakdown (NIP_UIP Entry Format)")
    # Formatting for currency
    st.dataframe(df_nip.style.format({
        "Base Amount": "₹{:,.2f}",
        "Final Amount": "₹{:,.2f}",
        "Factor 1": "{:.3f}",
        "Factor 2": "{:.3f}"
    }))
    
    total_inv = df_nip['Final Amount'].sum()
    st.metric("Total Projected Project Cost", f"₹ {total_inv:,.2f}")
    
    st.download_button("📥 Export NIP Entry Data", df_nip.to_csv(index=False), "NIP_UIP_Data.csv")

with tab2:
    st.subheader("Automated Site Layout")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.add_patch(Rectangle((0, 0), frontage, depth, fill=False, lw=2, color='black'))
    # Standard Building Placement
    ax.add_patch(Rectangle((4, depth-15-5), 9.23, 5, color='blue', alpha=0.3, label="B0 Building"))
    # PESO Clearance
    ax.add_patch(Rectangle((4, 4), frontage-8, depth-8, fill=False, ls='--', color='red', label="4M Clearance"))
    
    ax.set_aspect('equal')
    ax.legend()
    st.pyplot(fig)

with tab3:
    st.subheader("Underlying SOR Data (Nashik 1419)")
    st.info("The amounts in Tab 1 are derived using standard service numbers (7006847, 7006154, etc.) from the Nashik SOR.")
    st.write(f"Calculated Boundary Wall Length: **{wall_rm:.2f} RM**")
    st.write(f"Calculated Driveway Area: **{total_area:.2f} M2**")