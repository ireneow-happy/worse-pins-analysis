import pandas as pd
import streamlit as st

st.title("Wafer Probe Shift Analysis")

st.markdown("""
### 📐 計算公式與欄位定義：

- **Shift Direction 判斷**：取 `Prox Up`, `Prox Down`, `Prox Left`, `Prox Right` 中最小值所代表的方向。

\[ \text{Shift Direction} = \min(\text{Prox Up}, \text{Prox Down}, \text{Prox Left}, \text{Prox Right}) \]

- **Dominant Direction**：某一根針在所有觸點中最常出現的偏移方向
- **Dominant %**：Dominant 方向出現的次數除以該針總觸點數

- **On Rim Count**：觸點中有任一方向 Prox 為 0 的次數
- **Rim %**：On Rim Count 除以總觸點數，代表偏到 pad 邊緣的嚴重程度

#### ⬇️ 匯出欄位說明：
- `Dut`, `Pad`：探針對應的 DUT 和 Pad 編號
- `Up`, `Down`, `Left`, `Right`：各偏移方向出現次數
- `Total`：該針的總觸點數
- `Dominant`：主要偏移方向
- `Dominant %`：主要方向佔比
- `On Rim Count`：觸點在 pad 邊緣次數
- `Rim %`：偏到邊緣的比例
""")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
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
    st.download_button("Download Result as CSV", final_summary.to_csv(index=False), file_name="probe_shift_summary.csv")


if uploaded_file:
    # =====================================
    # 🔍 TD Order 偏移趨勢與劣化分析區段
    # =====================================
    st.markdown("### 🔍 TD Order Trend Analysis")

    # 1. 計算 Vert / Horz Imbalance
    df['Vert Imbalance'] = (df['Prox Up'] - df['Prox Down']).abs()
    df['Horz Imbalance'] = (df['Prox Left'] - df['Prox Right']).abs()

    # 2. 顯示相關係數
    st.markdown("#### 📊 Pearson Correlation")
    from scipy.stats import pearsonr
    vert_corr, _ = pearsonr(df['TD Order'], df['Vert Imbalance'])
    horz_corr, _ = pearsonr(df['TD Order'], df['Horz Imbalance'])
    st.write(f"**TD Order vs. Vert Imbalance**: r = {vert_corr:.3f}")
    st.write(f"**TD Order vs. Horz Imbalance**: r = {horz_corr:.3f}")

    # 3. 劣化速度：每根針的回歸斜率
    st.markdown("#### 🔼 Probe Degradation Rate (Slope)")
    from scipy.stats import linregress
    def compute_slope(group):
        if group['TD Order'].nunique() > 1:
            slope, _, _, _, _ = linregress(group['TD Order'], group['Vert Imbalance'])
            return slope
        return None

    slope_df = df.groupby('DUT+Pad').apply(compute_slope).dropna().reset_index()
    slope_df.columns = ['DUT+Pad', 'Vert Imbalance Slope']
    slope_df = slope_df.sort_values(by='Vert Imbalance Slope', ascending=False)
    st.dataframe(slope_df.head(10), use_container_width=True)


    # =====================================
    # 📉 On Rim % vs. TD Order 區段分析
    # =====================================
    st.markdown("### 📉 On Rim % vs. TD Order Bins")

    # 建立 TD Order 分段
    bins = [0, 20, 40, 60, 80, 1000]
    labels = ['1–20', '21–40', '41–60', '61–80', '81+']
    df['TD Bin'] = pd.cut(df['TD Order'], bins=bins, labels=labels)

    # 計算 On Rim 次數與比例
    df['On Rim'] = df[['Prox Up', 'Prox Down', 'Prox Left', 'Prox Right']].min(axis=1) == 0
    rim_by_bin = df.groupby('TD Bin')['On Rim'].agg(['sum', 'count'])
    rim_by_bin['On Rim %'] = rim_by_bin['sum'] / rim_by_bin['count'] * 100

    # 繪圖
    import matplotlib.pyplot as plt
    import seaborn as sns

    ---

#### 📊 Rim 發生率分段統計
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=rim_by_bin.index, y=rim_by_bin['On Rim %'], ax=ax, palette="viridis")
    ax.set_title("On Rim % vs. TD Order Bins (All Probes)")
    ax.set_ylabel("On Rim %")
    ax.set_xlabel("TD Order Bins")
    
    ax.grid(True, axis='y')
    st.pyplot(fig)

    # 顯示數據表格
    rim_by_bin = rim_by_bin.rename(columns={'sum': 'On Rim次數', 'count': '總測試數'})
    st.dataframe(rim_by_bin.reset_index())


    # =====================================
    # 🔍 個別探針的 Rim % 趨勢分析
    # =====================================
    st.subheader("Rim % Trend for Specific Probe")

    unique_probes = df['DUT+Pad'].unique()
    


    # =====================================
    # 🔝 Rim % 前幾高針位的趨勢分析（按 TD Order 區段）
    # =====================================
    st.markdown("### 🔝 Top Rim % Probes vs. TD Order")

    # 計算 Rim % 前幾高的針
    rim_probes = df.copy()
    rim_probes['On Rim'] = rim_probes[['Prox Up', 'Prox Down', 'Prox Left', 'Prox Right']].min(axis=1) == 0
    rim_rank = rim_probes.groupby('DUT+Pad')['On Rim'].agg(['sum', 'count'])
    rim_rank['On Rim %'] = rim_rank['sum'] / rim_rank['count']
    top_rim_probes = rim_rank.sort_values(by='On Rim %', ascending=False).head(10).index.tolist()

    selected_top_probe = st.selectbox("Select Top Rim % Probe", top_rim_probes)

    if selected_top_probe:
        probe_df2 = df[df['DUT+Pad'] == selected_top_probe]
        probe_df2['TD Bin'] = pd.cut(probe_df2['TD Order'], bins=bins, labels=labels)
        probe_df2['On Rim'] = probe_df2[['Prox Up', 'Prox Down', 'Prox Left', 'Prox Right']].min(axis=1) == 0
        probe_rim2 = probe_df2.groupby('TD Bin')['On Rim'].agg(['sum', 'count'])
        probe_rim2['On Rim %'] = probe_rim2['sum'] / probe_rim2['count'] * 100
        probe_rim2 = probe_rim2.rename(columns={'sum': 'On Rim次數', 'count': '總測試數'})

        st.markdown(f"#### 📌 {selected_top_probe} Rim % by TD Order Bin")
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        sns.barplot(x=probe_rim2.index, y=probe_rim2['On Rim %'], ax=ax3, palette="rocket")
        ax3.set_title(f"On Rim % Trend for Probe {selected_top_probe}")
        ax3.set_ylabel("On Rim %")
        ax3.set_xlabel("TD Order Bins")
        ax3.grid(True, axis='y')
        st.pyplot(fig3)
        st.dataframe(probe_rim2.reset_index())


    # =====================================
    # 🎨 表格標示：Rim % > 1% 標紅
    # =====================================
    def highlight_rim(val):
        if isinstance(val, (int, float)) and val > 1:
            return 'background-color: #ffcccc'
        return ''

    st.markdown("### 📋 Full Probe Rim Table with Highlighting")
    styled_table = final_summary.style.applymap(highlight_rim, subset=['Rim %'])
    st.dataframe(styled_table, use_container_width=True)


    # =====================================
    # 🧭 資料篩選與異常針位儀表板
    # =====================================
    st.markdown("### 🎛️ Filter Dashboard & Anomaly Detection")

    # Sidebar 篩選參數
    with st.sidebar:
        st.header("🔎 篩選條件")

        # Rim % 範圍
        rim_min, rim_max = st.slider("Rim % 範圍", min_value=0.0, max_value=10.0, value=(0.0, 2.0), step=0.1)

        # TD Order 範圍
        td_min, td_max = int(df['TD Order'].min()), int(df['TD Order'].max())
        td_range = st.slider("TD Order 範圍", min_value=td_min, max_value=td_max, value=(td_min, td_max), step=1)

        # DUT 和 Pad 篩選（可選）
        unique_duts = sorted(df['DUT#'].dropna().astype(int).unique())
        selected_dut = st.selectbox("選擇 DUT", options=["All"] + [str(d) for d in unique_duts])
        selected_pad = st.text_input("輸入 Pad #（留空則不篩選）", "")

    # 應用篩選條件
    filtered_df = df.copy()
    filtered_df = filtered_df[(filtered_df['TD Order'] >= td_range[0]) & (filtered_df['TD Order'] <= td_range[1])]
    filtered_summary = final_summary[(final_summary['Rim %'] >= rim_min / 100) & (final_summary['Rim %'] <= rim_max / 100)]

    if selected_dut != "All":
        filtered_summary = filtered_summary[filtered_summary['Dut'] == selected_dut]
    if selected_pad.strip():
        filtered_summary = filtered_summary[filtered_summary['Pad'] == selected_pad.strip()]

    st.markdown("#### 📋 篩選後結果")
    st.dataframe(filtered_summary)

    # 顯示異常針位（推薦）
    st.markdown("#### 🚨 異常針位推薦（Rim % > 1%）")
    anomaly_df = final_summary[final_summary['Rim %'] > 0.01]
    st.dataframe(anomaly_df)
