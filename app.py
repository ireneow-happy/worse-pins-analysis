
import pandas as pd
import streamlit as st

st.title("Wafer Probe Shift Analysis")

st.markdown("""
### 📐 計算公式與欄位定義：

- **Shift Direction 判斷**：取 `Prox Up`, `Prox Down`, `Prox Left`, `Prox Right` 中最小值所代表的方向。
- **Dominant Direction**：某一根針在所有觸點中最常出現的偏移方向
- **Dominant %**：Dominant 方向出現的次數除以該針總觸點數
- **On Rim Count**：觸點中有任一方向 Prox 為 0 的次數
- **Rim %**：On Rim Count 除以總測試次數，代表偏到 pad 邊緣的嚴重程度
""")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

# ✅ 初始化分析狀態
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

# ✅ 按鈕：執行分析
if uploaded_file and not st.session_state.analyzed:
    if st.button("🚀 執行分析"):
        st.session_state.analyzed = True

# ✅ 進行分析（已按下按鈕才會跑）
if st.session_state.analyzed:

    with st.spinner("分析中...請稍候"):

        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy.stats import pearsonr, linregress

        df = pd.read_excel(uploaded_file)
        df = df.dropna(subset=['DUT#', 'Pad #'])
        df['DUT+Pad'] = df['DUT#'].astype(int).astype(str) + '+' + df['Pad #'].astype(int).astype(str)

        def detect_shift_direction(row):
            directions = {
                'Up': row['Prox Up'],
                'Down': row['Prox Down'],
                'Left': row['Prox Left'],
                'Right': row['Prox Right']
            }
            return min(directions, key=directions.get)

        df['Shift Direction'] = df.apply(detect_shift_direction, axis=1)
        direction_summary = df.groupby(['DUT+Pad', 'Shift Direction']).size().unstack(fill_value=0)
        direction_summary['Total'] = direction_summary.sum(axis=1)
        direction_columns = ['Up', 'Down', 'Left', 'Right']
        direction_summary['Dominant'] = direction_summary[direction_columns].idxmax(axis=1)
        direction_summary['Dominant %'] = direction_summary[direction_columns].max(axis=1) / direction_summary['Total']

        df['On Rim'] = df[['Prox Up', 'Prox Down', 'Prox Left', 'Prox Right']].min(axis=1) == 0
        rim_summary = df.groupby('DUT+Pad')['On Rim'].agg(['sum', 'count'])
        rim_summary['Rim %'] = rim_summary['sum'] / rim_summary['count']
        rim_summary = rim_summary.rename(columns={'sum': 'On Rim Count', 'count': 'Total Count'})

        direction_summary = direction_summary.reset_index()
        direction_summary[['Dut', 'Pad']] = direction_summary['DUT+Pad'].str.split('+', expand=True)
        final_summary = direction_summary.merge(rim_summary, on='DUT+Pad', how='left')
        final_summary = final_summary[['Dut', 'Pad', 'Up', 'Down', 'Left', 'Right', 'Total', 'Dominant', 'Dominant %', 'On Rim Count', 'Total Count', 'Rim %']]
        final_summary = final_summary.sort_values(by='Rim %', ascending=False)

        st.subheader("Probe Shift Summary")
        st.dataframe(final_summary)

        st.markdown("### 🔍 TD Order Trend Analysis")
        df['Vert Imbalance'] = (df['Prox Up'] - df['Prox Down']).abs()
        df['Horz Imbalance'] = (df['Prox Left'] - df['Prox Right']).abs()
        vert_corr, _ = pearsonr(df['TD Order'], df['Vert Imbalance'])
        horz_corr, _ = pearsonr(df['TD Order'], df['Horz Imbalance'])
        st.write(f"**TD Order vs. Vert Imbalance**: r = {vert_corr:.3f}")
        st.write(f"**TD Order vs. Horz Imbalance**: r = {horz_corr:.3f}")
