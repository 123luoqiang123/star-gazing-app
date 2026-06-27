import streamlit as st
from src.data_fetcher import fetch_city_data
from src.score_calculator import calculate_scores
from src.visualizer import (
    create_map, create_bar_chart, create_radar_chart,
    create_bortle_chart, create_aqi_chart,
    create_cloud_chart, create_elevation_chart
)

st.set_page_config(
    page_title="🌌 中国观星圣地推荐",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== 深色主题 CSS =====
st.markdown("""
<style>
    /* 全局背景 */
    .stApp, .stApp > header, .stApp > footer {
        background: #080c18 !important;
    }
    .main > div {
        background: transparent !important;
    }
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background: #050810 !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #f0f4ff !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background: rgba(255,255,255,0.08) !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #f0f4ff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
    }
    /* 顶部导航栏 */
    header[data-testid="stHeader"] {
        background: #050810 !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    }
    header[data-testid="stHeader"] * {
        color: #f0f4ff !important;
    }
    header[data-testid="stHeader"] button {
        background: transparent !important;
        color: #f0f4ff !important;
    }
    header[data-testid="stHeader"] button:hover {
        background: rgba(255,255,255,0.05) !important;
    }
    /* 通用透明 */
    .stMarkdown, .stPlotlyChart, .stDataFrame, .stExpander, .stTabs {
        background: transparent !important;
    }
    .stExpander > div:first-child {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
    }
    /* 全局文字 */
    html, body, .stMarkdown, .stText, .stCaption, .stDataFrame {
        color: #f0f4ff !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f0f4ff !important;
        text-shadow: 0 0 30px rgba(100,180,255,0.15);
    }
    p, li, span, div {
        color: #e0e8f5 !important;
    }
    /* 指标卡片 */
    .metric-card {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 16px;
        padding: 20px 16px;
        border: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(8px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        text-align: center;
    }
    .metric-card h3 {
        color: #f0f4ff !important;
        margin-bottom: 8px;
    }
    .metric-card p {
        color: #e0e8f5 !important;
    }
    hr {
        border-color: rgba(255,255,255,0.06) !important;
    }
    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.12);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌌 中国最佳观星地点分析与推荐系统")
st.markdown("> 综合 **光污染(Bortle)**、**空气质量(AQI)**、**云量** 和 **海拔**，智能评估观星适宜性。")

# ---- 侧边栏 ----
with st.sidebar:
    st.header("⚙️ 参数设置")
    use_mock = st.radio("数据模式", ["模拟数据 (快速演示)", "真实API (需密钥)"], index=0)
    use_mock_flag = True if use_mock == "模拟数据 (快速演示)" else False

    st.divider()
    st.subheader("🎛️ 权重调节")
    w1 = st.slider("光污染权重", 0.0, 1.0, 0.35)
    w2 = st.slider("云量权重", 0.0, 1.0, 0.25)
    w3 = st.slider("空气质量权重", 0.0, 1.0, 0.20)
    w4 = st.slider("海拔权重", 0.0, 1.0, 0.20)
    total = w1 + w2 + w3 + w4
    if total > 0:
        w1, w2, w3, w4 = w1/total, w2/total, w3/total, w4/total
    st.caption(f"当前权重：光污染 {w1:.0%}，云量 {w2:.0%}，AQI {w3:.0%}，海拔 {w4:.0%}")

# ---- 数据加载与计算 ----
@st.cache_data(ttl=3600)
def load_and_calc(use_mock, w1, w2, w3, w4):
    raw_df = fetch_city_data(use_mock)
    scored_df = calculate_scores(raw_df)
    scored_df['total_score'] = (
        scored_df['light_score'] * w1 +
        scored_df['cloud_score'] * w2 +
        scored_df['aqi_score'] * w3 +
        scored_df['elevation_score'] * w4
    )
    scored_df = scored_df.sort_values('total_score', ascending=False).reset_index(drop=True)
    scored_df['rating'] = scored_df['total_score'].apply(
        lambda s: '★★★★★' if s >= 85 else ('★★★★☆' if s >= 70 else ('★★★☆☆' if s >= 55 else ('★★☆☆☆' if s >= 40 else '★☆☆☆☆')))
    )
    return scored_df

df = load_and_calc(use_mock_flag, w1, w2, w3, w4)

# ---- Top 3 ----
st.subheader("🏆 观星圣地 Top 3")
col1, col2, col3 = st.columns(3)
top3 = df.head(3)
for idx, (_, row) in enumerate(top3.iterrows()):
    with [col1, col2, col3][idx]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>#{idx+1} {row['city']}</h3>
            <p style="font-size:38px; font-weight:700; margin:8px 0;">{row['total_score']:.1f}</p>
            <p style="font-size:26px; margin:4px 0;">{row['rating']}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ---- 主图表区域 ----
left_col, right_col = st.columns([5.5, 4.5])

with left_col:
    st.plotly_chart(create_map(df), use_container_width=True, config={'displayModeBar': False})
    st.plotly_chart(create_radar_chart(df, top_n=5), use_container_width=True, config={'displayModeBar': False})

with right_col:
    st.plotly_chart(create_bar_chart(df), use_container_width=True, config={'displayModeBar': False})
    with st.expander("📋 查看详细数据表"):
        # ---- 自定义 HTML 表格（强制黑底白字） ----
        display_cols = ['city', 'bortle', 'aqi', 'cloud_cover', 'elevation', 'total_score', 'rating']
        
        # 定义列名映射（让表头更友好）
        col_names = {
            'city': '城市',
            'bortle': '光污染',
            'aqi': 'AQI',
            'cloud_cover': '云量(%)',
            'elevation': '海拔(m)',
            'total_score': '综合得分',
            'rating': '评级'
        }
        
        # 构建 HTML 表格
        html = """
        <div style="overflow-x: auto; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; background-color: #080c18; color: #e0e8f5;">
                <thead>
                    <tr style="background-color: #1a1f2e; border-bottom: 2px solid rgba(255,255,255,0.08);">
        """
        for col in display_cols:
            html += f"<th style='padding: 10px 12px; text-align: left; color: #f0f4ff; font-weight: 600;'>{col_names.get(col, col)}</th>"
        html += "</tr></thead><tbody>"
        
        for idx, row in df[display_cols].iterrows():
            bg_color = "#0d1222" if idx % 2 == 0 else "#080c18"
            html += f"<tr style='background-color: {bg_color}; border-bottom: 1px solid rgba(255,255,255,0.04);'>"
            for col in display_cols:
                value = row[col]
                if isinstance(value, float):
                    value = f"{value:.2f}"
                if col == 'rating':
                    html += f"<td style='padding: 8px 12px; color: #FFD700;'>{value}</td>"
                else:
                    html += f"<td style='padding: 8px 12px; color: #e0e8f5;'>{value}</td>"
            html += "</tr>"
        
        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)

# ---- 四个维度指标分析（2×2网格） ----
st.divider()
st.subheader("📊 各维度指标详细分析")

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    st.plotly_chart(create_bortle_chart(df), use_container_width=True, config={'displayModeBar': False})

with row1_col2:
    st.plotly_chart(create_aqi_chart(df), use_container_width=True, config={'displayModeBar': False})

with row2_col1:
    st.plotly_chart(create_cloud_chart(df), use_container_width=True, config={'displayModeBar': False})

with row2_col2:
    st.plotly_chart(create_elevation_chart(df), use_container_width=True, config={'displayModeBar': False})

st.caption("💡 左侧边栏可调节各指标权重，实时影响评分结果")