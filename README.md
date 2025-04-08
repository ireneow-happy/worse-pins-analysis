
# 🧪 Wafer Probe Shift Analysis App

本應用為使用 Streamlit 打造的晶圓探針偏移分析工具，支援以 TD Order、Rim %、Imbalance 為核心的偏移趨勢分析與異常探針偵測。

---

## 🚀 功能亮點

### 📤 資料上傳
- 上傳 Excel（.xlsx）檔案（需含以下欄位：`DUT#`, `Pad #`, `Prox Up`, `Prox Down`, `Prox Left`, `Prox Right`, `TD Order`）

### 📊 探針偏移分析
- 判斷偏移方向（Shift Direction）
- 統計各方向出現次數與主要偏移方向（Dominant Direction）
- Rim 偏移次數與比例（On Rim Count / Rim %）

### 📈 TD Order 趨勢分析
- TD Order 對 Vert/Horz Imbalance 的皮爾森相關係數
- 每根針的偏移劣化速度（回歸斜率）
- 分段 Rim % 分析（TD Order Bins）

### 📌 特定針位分析
- Top Rim % 前幾高針位的 Rim 趨勢視覺化（TD Order 分段）

### 🎛️ 篩選儀表板
- 篩選 Rim %、TD Order 範圍、DUT、Pad
- 顯示篩選後結果與異常針位推薦（Rim % > 1%）

### 💡 互動介面強化
- 手動點選「🚀 執行分析」才開始運算
- 手動「🔍 執行條件篩選」才套用條件
- 自動標紅高 Rim% 的針位
- 分析中會顯示進度條 spinner

---

## 📦 安裝套件需求（requirements.txt）

```
pandas
streamlit
openpyxl
scipy
matplotlib
seaborn
```

---

## ▶️ 執行方式

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📂 檔案結構
- `app.py`：主程式（含所有互動分析功能）
- `requirements.txt`：環境需求
- `README.md`：本說明文件

---

## 🧠 備註
本程式可部署於本地或 [Streamlit Cloud](https://streamlit.io/cloud)，適用於測試資料品質評估、探針偏移追蹤、製程熱穩定性分析等用途。
