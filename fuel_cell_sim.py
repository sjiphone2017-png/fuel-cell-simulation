import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fuel Cell Virtual Lab", layout="wide")

st.title("محاكاة خلية وقود هيدروجين — Virtual Lab 🔋")

# Sidebar inputs
st.sidebar.header("ضوابط المحاكاة")
E0 = st.sidebar.number_input("جهد نووي نظري E₀ (V)", value=1.23, step=0.01, format="%.3f")
i0 = st.sidebar.number_input("تيار تبادلي i₀ (A/cm²)", value=1e-4, format="%.6f")
a = st.sidebar.number_input("عامل التفعيل a (V)", value=0.06, step=0.01)
R = st.sidebar.number_input("المقاومة الداخلية R (Ω·cm²)", value=0.2, step=0.01)
B = st.sidebar.number_input("ثابت خسارة التركيز B (V)", value=0.02, step=0.01)
i_lim = st.sidebar.number_input("تيار حدّي i_lim (A/cm²)", value=2.0, step=0.1)
area = st.sidebar.number_input("مساحة الخلية (cm²)", value=50.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.write("تجربة سريعة")
current_choice = st.sidebar.selectbox("اختر التيار لتفاصيل", ("0.1*i_lim","0.5*i_lim","0.9*i_lim","مخصص"))
custom_i = st.sidebar.number_input("تيار مخصص (A/cm²)", value=0.5, step=0.01)

# Build current array
i_vals = np.linspace(0.01, i_lim*0.99, 200)

def V_act(i):
    return a * np.log(i / i0 + 1.0)

def V_ohm(i):
    return i * R

def V_conc(i):
    x = np.clip(1 - i / i_lim, 1e-6, 1.0)
    return -B * np.log(x)

def V_total(i):
    return E0 - V_act(i) - V_ohm(i) - V_conc(i)

V_vals = V_total(i_vals)
Power_vals = V_vals * i_vals * area

fig, ax = plt.subplots(figsize=(6,4))
ax.plot(i_vals, V_vals)
ax.set_xlabel("Current density (A/cm²)")
ax.set_ylabel("Cell voltage (V)")
ax.set_title("Polarization curve (V vs i)")
ax.grid(True)

fig2, ax2 = plt.subplots(figsize=(6,4))
ax2.plot(i_vals, Power_vals)
ax2.set_xlabel("Current density (A/cm²)")
ax2.set_ylabel("Power (W)")
ax2.set_title("Power vs Current density")
ax2.grid(True)

col1, col2 = st.columns(2)
with col1:
    st.pyplot(fig)
with col2:
    st.pyplot(fig2)

df = pd.DataFrame({
    "i (A/cm²)": np.round(i_vals, 4),
    "V (V)": np.round(V_vals, 4),
    "Power (W)": np.round(Power_vals, 4)
})
st.dataframe(df.head(10))

if current_choice == "0.1*i_lim":
    sel_i = 0.1 * i_lim
elif current_choice == "0.5*i_lim":
    sel_i = 0.5 * i_lim
elif current_choice == "0.9*i_lim":
    sel_i = 0.9 * i_lim
else:
    sel_i = custom_i

sel_V = V_total(sel_i)
sel_P = sel_V * sel_i * area
st.markdown("### قراءة نقطة")
st.write(f"تيار اختيارى = {sel_i:.4f} A/cm²  — جهد الخلية = {sel_V:.4f} V  — القدرة ≈ {sel_P:.3f} W")

csv = df.to_csv(index=False).encode('utf-8')
st.download_button("نزيل بيانات المحاكاة (CSV)", data=csv, file_name="fuel_cell_sim.csv", mime="text/csv")

st.markdown("---")
st.markdown("### ملاحظات")
st.write("- هذا نموذج تبسيطي لشرح الفكرة في مشروع جامعي.\n- يمكن تحسين الدقة بإدخال بيانات تجريبية أو نماذج كيميائية/كهربائية أدق.")
