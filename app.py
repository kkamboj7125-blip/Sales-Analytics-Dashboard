import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f172a; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #0f172a 100%);
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e293b, #0f3460);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label { color: #94a3b8 !important; font-size: 13px !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 26px !important; font-weight: 700 !important; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .section-header {
        background: linear-gradient(90deg, #1a56db, #0891b2);
        padding: 8px 16px; border-radius: 8px;
        margin: 16px 0 8px 0; color: white;
        font-weight: 700; font-size: 16px;
    }
    .footer { text-align: center; color: #475569; font-size: 12px; margin-top: 30px; padding: 10px; border-top: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv", encoding="latin1")
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, format='mixed')
    df['Ship Date']  = pd.to_datetime(df['Ship Date'],  dayfirst=True, format='mixed')
    df['Year']       = df['Order Date'].dt.year
    df['Month']      = df['Order Date'].dt.month
    df['Month Name'] = df['Order Date'].dt.strftime('%b')
    df['Quarter']    = df['Order Date'].dt.quarter.map({1:'Q1',2:'Q2',3:'Q3',4:'Q4'})
    df['Ship Days']  = (df['Ship Date'] - df['Order Date']).dt.days
    return df

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")
    st.markdown("---")
    years      = sorted(df['Year'].unique())
    sel_years  = st.multiselect("📅 Year",     years,                     default=years)
    regions    = sorted(df['Region'].unique())
    sel_reg    = st.multiselect("🗺️ Region",   regions,                   default=regions)
    cats       = sorted(df['Category'].unique())
    sel_cats   = st.multiselect("📦 Category", cats,                      default=cats)
    segs       = sorted(df['Segment'].unique())
    sel_segs   = st.multiselect("👥 Segment",  segs,                      default=segs)
    st.markdown("---")
    st.info(f"**Records:** {len(df):,}\n\n**Period:** {df['Order Date'].min().strftime('%b %Y')} – {df['Order Date'].max().strftime('%b %Y')}")
    st.markdown('<p style="color:#475569;font-size:12px;text-align:center;">Built by Khushi | Data Analytics</p>', unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
fdf = df[
    (df['Year'].isin(sel_years)) &
    (df['Region'].isin(sel_reg)) &
    (df['Category'].isin(sel_cats)) &
    (df['Segment'].isin(sel_segs))
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Sales Analytics Dashboard")
st.markdown('<p style="color:#64748b;font-size:15px;">Interactive Business Intelligence Dashboard | Superstore Sales Analysis</p>', unsafe_allow_html=True)
st.markdown("---")

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Key Performance Indicators</div>', unsafe_allow_html=True)

total_sales   = fdf['Sales'].sum()
total_orders  = fdf.shape[0]
avg_order     = fdf['Sales'].mean()
top_region    = fdf.groupby('Region')['Sales'].sum().idxmax()
top_category  = fdf.groupby('Category')['Sales'].sum().idxmax()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Total Sales",    f"${total_sales:,.0f}")
k2.metric("🛒 Total Orders",   f"{total_orders:,}")
k3.metric("💵 Avg Order Value",f"${avg_order:,.0f}")
k4.metric("🏆 Top Region",     top_region)
k5.metric("📦 Top Category",   top_category)

st.markdown("---")

# ── ROW 1: Sales Trend + Category Pie ─────────────────────────────────────────
st.markdown('<div class="section-header">📉 Sales Trends</div>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    monthly = fdf.groupby(['Year','Month','Month Name'])['Sales'].sum().reset_index().sort_values(['Year','Month'])
    monthly['Period'] = monthly['Month Name'] + ' ' + monthly['Year'].astype(str)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly['Period'], y=monthly['Sales'],
        name='Sales', line=dict(color='#00d4ff', width=2.5),
        fill='tozeroy', fillcolor='rgba(0,212,255,0.1)'))
    fig.update_layout(title='Monthly Sales Trend', paper_bgcolor='#1e293b',
        plot_bgcolor='#0f172a', font_color='#94a3b8', height=320,
        xaxis=dict(gridcolor='#1e293b', tickangle=45), yaxis=dict(gridcolor='#334155'))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    cat_data = fdf.groupby('Category')['Sales'].sum().reset_index()
    fig2 = px.pie(cat_data, values='Sales', names='Category', title='Sales by Category',
        color_discrete_sequence=['#00d4ff','#1a56db','#06d6a0'], hole=0.5)
    fig2.update_layout(paper_bgcolor='#1e293b', font_color='#94a3b8', height=320)
    fig2.update_traces(textfont_color='white')
    st.plotly_chart(fig2, use_container_width=True)

# ── ROW 2: Region + Sub-Category ──────────────────────────────────────────────
st.markdown('<div class="section-header">🗺️ Regional & Product Analysis</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    reg = fdf.groupby('Region')['Sales'].sum().reset_index().sort_values('Sales')
    fig3 = px.bar(reg, x='Sales', y='Region', orientation='h',
        title='Sales by Region', color='Sales',
        color_continuous_scale=['#1a56db','#00d4ff'])
    fig3.update_layout(paper_bgcolor='#1e293b', plot_bgcolor='#0f172a',
        font_color='#94a3b8', height=300,
        xaxis=dict(gridcolor='#334155'), yaxis=dict(gridcolor='#1e293b'))
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    subcat = fdf.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
    fig4 = px.bar(subcat, x='Sub-Category', y='Sales',
        title='Top 10 Sub-Categories', color='Sales',
        color_continuous_scale=['#1a56db','#00d4ff','#06d6a0'])
    fig4.update_layout(paper_bgcolor='#1e293b', plot_bgcolor='#0f172a',
        font_color='#94a3b8', height=300,
        xaxis=dict(gridcolor='#1e293b', tickangle=30), yaxis=dict(gridcolor='#334155'))
    st.plotly_chart(fig4, use_container_width=True)

# ── ROW 3: Segment + Quarterly ────────────────────────────────────────────────
st.markdown('<div class="section-header">👥 Segment & Quarterly Performance</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    seg = fdf.groupby('Segment')['Sales'].sum().reset_index()
    fig5 = px.bar(seg, x='Segment', y='Sales', title='Sales by Customer Segment',
        color='Segment', color_discrete_sequence=['#00d4ff','#1a56db','#06d6a0'])
    fig5.update_layout(paper_bgcolor='#1e293b', plot_bgcolor='#0f172a',
        font_color='#94a3b8', height=300, showlegend=False,
        xaxis=dict(gridcolor='#1e293b'), yaxis=dict(gridcolor='#334155'))
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    qtr = fdf.groupby(['Year','Quarter'])['Sales'].sum().reset_index()
    qtr['Label'] = qtr['Year'].astype(str) + ' ' + qtr['Quarter']
    fig6 = px.line(qtr, x='Label', y='Sales', color='Quarter',
        title='Quarterly Sales Trend', markers=True,
        color_discrete_sequence=['#00d4ff','#1a56db','#06d6a0','#ffd166'])
    fig6.update_layout(paper_bgcolor='#1e293b', plot_bgcolor='#0f172a',
        font_color='#94a3b8', height=300,
        xaxis=dict(gridcolor='#1e293b', tickangle=30), yaxis=dict(gridcolor='#334155'),
        legend=dict(bgcolor='#1e293b'))
    st.plotly_chart(fig6, use_container_width=True)

# ── ROW 4: Top States + Shipping ──────────────────────────────────────────────
st.markdown('<div class="section-header">🏆 Top States & Shipping Analysis</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)

with c7:
    states = fdf.groupby('State')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
    fig7 = px.bar(states, x='Sales', y='State', orientation='h',
        title='Top 10 States by Sales', color='Sales',
        color_continuous_scale=['#1a56db','#00d4ff'])
    fig7.update_layout(paper_bgcolor='#1e293b', plot_bgcolor='#0f172a',
        font_color='#94a3b8', height=350,
        xaxis=dict(gridcolor='#334155'), yaxis=dict(gridcolor='#1e293b'))
    st.plotly_chart(fig7, use_container_width=True)

with c8:
    ship = fdf.groupby('Ship Mode')['Sales'].sum().reset_index()
    fig8 = px.pie(ship, values='Sales', names='Ship Mode',
        title='Sales by Shipping Mode', hole=0.4,
        color_discrete_sequence=['#00d4ff','#1a56db','#06d6a0','#ffd166'])
    fig8.update_layout(paper_bgcolor='#1e293b', font_color='#94a3b8', height=350)
    fig8.update_traces(textfont_color='white')
    st.plotly_chart(fig8, use_container_width=True)

# ── ROW 5: Data Table ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Data Explorer</div>', unsafe_allow_html=True)
show_cols = ['Order ID','Order Date','Customer Name','Segment','Category','Sub-Category','Region','State','Sales','Ship Mode']
available = [c for c in show_cols if c in fdf.columns]
disp = fdf[available].copy()
disp['Sales'] = disp['Sales'].round(2)
st.dataframe(
    disp.head(100).style.background_gradient(subset=['Sales'], cmap='Blues'),
    use_container_width=True, height=320
)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div class="footer">
    📊 Sales Analytics Dashboard &nbsp;|&nbsp;
    Built by <b>Khushi</b> &nbsp;|&nbsp;
    B.Tech CSE 2023–2027 &nbsp;|&nbsp;
    Tools: Python • Pandas • Plotly • Streamlit
</div>
""", unsafe_allow_html=True)
