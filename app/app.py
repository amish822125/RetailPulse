import os
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==================================================
# 1. PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="RetailPulse | Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Data is the UCI Online Retail dataset (UK, Dec 2010 - Dec 2011): values are in GBP.
# The ₹ symbol in the Excel file was only formatting; no conversion was done.
CURRENCY = "£"

# Colour theme per page: (banner start, banner end, chart accent)
THEME = {
    "Overview": ("#1d4ed8", "#7c3aed", "#3b82f6"),
    "Demand Prediction": ("#7c3aed", "#db2777", "#a855f7"),
    "Model Performance": ("#0f766e", "#16a34a", "#22c55e"),
    "Sales Analytics": ("#b45309", "#eab308", "#f59e0b"),
    "Inventory Insights": ("#c2410c", "#f97316", "#fb923c"),
    "Customer Analytics": ("#be185d", "#2563eb", "#ec4899"),
}

PALETTE = ["#3b82f6", "#8b5cf6", "#22c55e", "#f59e0b", "#ef4444",
           "#06b6d4", "#ec4899", "#84cc16", "#f97316", "#14b8a6"]

# ==================================================
# 2. THEME
# ==================================================
st.markdown("""
<style>
.stApp { background: #0b1120; color: #e5e7eb; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
    border-right: 1px solid #263247;
}
.brand-container { padding: 12px 10px 18px 10px; }
.brand-logo {
    display:inline-flex; width:46px; height:46px; align-items:center; justify-content:center;
    border-radius:14px; background:linear-gradient(135deg,#2563eb,#7c3aed);
    font-size:25px; margin-bottom:12px; box-shadow:0 5px 20px rgba(37,99,235,.25);
}
.brand-name { color:#f8fafc; font-size:23px; font-weight:800; letter-spacing:1px; margin:0; }
.brand-subtitle { color:#94a3b8; font-size:12px; margin-top:4px; }
.sidebar-section { color:#64748b; font-size:10px; font-weight:800; letter-spacing:1.5px; margin:18px 0 8px 5px; }

[data-testid="stSidebar"] [data-testid="stRadio"] > div { gap:7px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background:transparent; border:1px solid transparent; border-radius:10px;
    padding:9px 11px; transition:all .2s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#1e293b; border-color:#334155; }
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display:none; }
[data-testid="stSidebar"] [data-testid="stRadio"] label p { color:#cbd5e1; font-size:13px; font-weight:600; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background:linear-gradient(90deg,#1d4ed8,#3730a3); border:1px solid #3b82f6;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p { color:#fff; }

.status-card { background:#172235; border:1px solid #29364c; border-radius:10px; padding:12px; margin-top:18px; }
.status-title { color:#94a3b8; font-size:10px; letter-spacing:1px; font-weight:700; }
.status-text { color:#e2e8f0; font-size:12px; margin-top:7px; }
.status-dot { display:inline-block; width:8px; height:8px; background:#22c55e; border-radius:50%; margin-right:7px; }

h1, h2, h3 { color:#f8fafc !important; }
p, label { color:#cbd5e1; }

/* Hero banner */
.hero {
    background: linear-gradient(120deg, #1d4ed8 0%, #7c3aed 60%, #db2777 100%);
    border-radius: 18px; padding: 26px 30px; margin-bottom: 18px;
    box-shadow: 0 10px 40px rgba(79,70,229,.25);
}
.hero h1 { color:#fff !important; margin:0; font-size:30px; }
.hero p { color:#e0e7ff; margin:6px 0 0 0; font-size:14px; }

/* KPI cards */
.kpi {
    background: linear-gradient(145deg,#172235,#111c2e);
    border:1px solid #29364c; border-radius:14px; padding:16px 18px;
    border-top:3px solid var(--accent,#3b82f6);
}
.kpi-label { color:#94a3b8; font-size:12px; font-weight:600; letter-spacing:.5px; }
.kpi-value { color:#f8fafc; font-size:26px; font-weight:800; margin-top:4px; }
.kpi-sub { color:#64748b; font-size:11px; margin-top:2px; }

/* Insight box */
.insight {
    background:#13203a; border:1px solid #29467a; border-left:4px solid #3b82f6;
    border-radius:10px; padding:12px 16px; margin-bottom:10px; color:#dbeafe; font-size:14px;
}

[data-testid="stMetric"] {
    background:linear-gradient(145deg,#172235,#111c2e); border:1px solid #29364c;
    padding:18px; border-radius:12px;
}
[data-testid="stMetricValue"] { color:#60a5fa; }

.stButton button, .stFormSubmitButton button {
    background:linear-gradient(90deg,#2563eb,#4f46e5); color:white; border-radius:8px;
    border:none; padding:8px 18px; font-weight:600;
}
.stDownloadButton button { background:#172235; color:#93c5fd; border:1px solid #3b82f6; border-radius:8px; }

[data-testid="stPlotlyChart"] {
    background:#0f1a2e; border:1px solid #29364c; border-radius:14px;
    padding:6px 6px 0 6px; margin-bottom:12px;
}
.kpi { min-height:112px; }
button[data-baseweb="tab"] { font-weight:600; }
hr { border-color:#263247; }
</style>
""", unsafe_allow_html=True)

# ==================================================
# 3. PATHS
# ==================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "demand_model.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "models", "demand_feature_columns.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "RetailPulse_Processed.csv")


# ==================================================
# 4. LOAD
# ==================================================
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH), joblib.load(FEATURE_PATH)


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


try:
    model, feature_columns = load_model()
    original_df = load_data()
except Exception as e:
    st.error(f"Unable to load project files: {e}")
    st.stop()

# ==================================================
# 5. HELPERS
# ==================================================
def money(v):
    return f"{CURRENCY}{v:,.2f}"


def short_money(v):
    if abs(v) >= 1e6:
        return f"{CURRENCY}{v/1e6:.2f}M"
    if abs(v) >= 1e3:
        return f"{CURRENCY}{v/1e3:.1f} K"
    return f"{CURRENCY}{v:,.0f}"


def kpi(label, value, sub="", accent="#3b82f6"):
    st.markdown(
        f"""<div class="kpi" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div></div>""",
        unsafe_allow_html=True,
    )


def style(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=64, b=10),
        height=height,
        font=dict(color="#cbd5e1"),
        colorway=PALETTE,
        title_font=dict(size=16, color="#f8fafc"),
    )
    fig.update_xaxes(gridcolor="#1e293b")
    fig.update_yaxes(gridcolor="#1e293b")
    return fig


def hbar(series, title, color=None, height=400):
    color = color or THEME.get(page, THEME["Overview"])[2]
    d = series.rename_axis("label").rename("value").reset_index()
    d = d.sort_values("value")
    fig = px.bar(d, x="value", y="label", orientation="h", title=title)
    fig.update_traces(marker_color=color, hovertemplate="%{y}<br>%{x:,.2f}<extra></extra>")
    fig.update_layout(xaxis_title="", yaxis_title="")
    return style(fig, height)


def donut(series, title, height=400):
    d = series.rename_axis("label").rename("value").reset_index()
    fig = px.pie(d, names="label", values="value", hole=0.55, title=title)
    fig.update_traces(textinfo="percent", marker=dict(line=dict(color="#0b1120", width=2)))
    return style(fig, height)


def empty_message():
    st.warning("No records found for the selected filters. Please change your filters.")


def hero(title, subtitle):
    c1, c2, _ = THEME.get(page, THEME["Overview"])
    st.markdown(f'<div class="hero" style="background:linear-gradient(120deg,{c1},{c2})">'
                f'<h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def predict_demand(country, product, month, year, prices):
    """Predict demand for one or more unit prices."""
    prices = list(prices)
    n = len(prices)
    data = pd.DataFrame({
        "Country": [country] * n,
        "Description": [product] * n,
        "Month": [month] * n,
        "Year": [year] * n,
        "Sum of UnitPrice": prices,
    })
    enc = pd.get_dummies(data, columns=["Country", "Description", "Month"], dtype=int)
    enc = enc.reindex(columns=feature_columns, fill_value=0)
    return np.maximum(0, model.predict(enc))


def unseen_inputs(country, product, month):
    """Input columns that are not among the model's trained features.
    Such values silently become 0 after reindex()."""
    cols = [f"Country_{country}", f"Description_{product}", f"Month_{month}"]
    return [c for c in cols if c not in feature_columns]


# ==================================================
# 6. MONTH FILTER
# ==================================================
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
month_values = original_df["Month"].dropna().astype(str).str.strip()
available_months = [m for m in month_order if m in month_values.unique()]
if not available_months:
    available_months = sorted(month_values.unique().tolist(),
                              key=lambda x: int(x) if x.isdigit() else x)

# ==================================================
# 7. SIDEBAR
# ==================================================
page_options = [
    "📊  Overview", "🔮  Demand Prediction", "🧠  Model Performance",
    "📈  Sales Analytics", "📦  Inventory Insights", "👥  Customer Analytics",
]
page_mapping = {
    "📊  Overview": "Overview", "🔮  Demand Prediction": "Demand Prediction",
    "🧠  Model Performance": "Model Performance", "📈  Sales Analytics": "Sales Analytics",
    "📦  Inventory Insights": "Inventory Insights", "👥  Customer Analytics": "Customer Analytics",
}

with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-logo">📊</div>
        <div class="brand-name">RETAILPULSE</div>
        <div class="brand-subtitle">AI-Powered Retail Intelligence</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="sidebar-section">WORKSPACE</div>', unsafe_allow_html=True)
    selected_page = st.radio("NAVIGATION", page_options,
                             label_visibility="collapsed", key="premium_navigation")
    page = page_mapping[selected_page]
    st.divider()

    st.markdown('<div class="sidebar-section">GLOBAL FILTERS</div>', unsafe_allow_html=True)
    available_years = sorted(original_df["Year"].dropna().astype(int).unique().tolist())
    selected_year = st.selectbox("📅 Select Year", ["All Years"] + available_years)
    selected_month = st.selectbox("🗓️ Select Month", ["All Months"] + available_months)
    available_countries = sorted(original_df["Country"].dropna().unique().tolist())
    selected_country = st.selectbox("🌍 Select Country", ["All Countries"] + available_countries)
    available_products = sorted(original_df["Description"].dropna().unique().tolist())
    selected_product = st.selectbox("🛍️ Select Product", ["All Products"] + available_products)
    exclude_bulk = st.checkbox("Exclude bulk orders (>144 units)", value=False,
                               help="Very large orders can dominate the charts.")

    st.markdown("""
    <div class="status-card">
        <div class="status-title">PROJECT STATUS</div>
        <div class="status-text"><span class="status-dot"></span>Dashboard Active</div>
        <div class="status-text">Data Science & Analytics</div>
    </div>
    <div style="color:#64748b;font-size:10px;text-align:center;margin-top:20px;">
        RETAILPULSE PROJECT • 2026</div>
    """, unsafe_allow_html=True)

# ==================================================
# 8. APPLY FILTERS
# ==================================================
df = original_df.copy()
if selected_year != "All Years":
    df = df[pd.to_numeric(df["Year"], errors="coerce") == selected_year]
if selected_month != "All Months":
    df = df[df["Month"].astype(str).str.strip() == str(selected_month)]
if selected_country != "All Countries":
    df = df[df["Country"] == selected_country]
if selected_product != "All Products":
    df = df[df["Description"] == selected_product]
if exclude_bulk:
    df = df[df["Sum of Quantity"] <= 144]

# Model Performance and Demand Prediction do not depend on the filters,
# so let them open even when the filters return no records.
if df.empty and page not in ("Model Performance", "Demand Prediction"):
    hero("📊 RetailPulse Dashboard", "AI-Powered Retail Intelligence")
    empty_message()
    st.stop()

# ==================================================
# 9. COMMON KPIs
# ==================================================
total_sales = df["Sum of Total Sales"].sum()
total_profit = df["Sum of Estimated Profit"].sum()
total_quantity = df["Sum of Quantity"].sum()
total_products = df["Description"].nunique()
total_countries = df["Country"].nunique()
margin = (total_profit / total_sales * 100) if total_sales else 0
customer_records = (df["Count of Customer  ID"].sum()
                    if "Count of Customer  ID" in df.columns else 0)

active_filters = [x for x in [selected_year, selected_month, selected_country, selected_product]
                  if not str(x).startswith("All ")]


def trend_frame():
    t = (df.groupby("Year Month")[["Sum of Total Sales", "Sum of Estimated Profit"]]
         .sum().reset_index())
    # Chronological sorting: convert to dates first; fall back to text order
    t["_d"] = pd.to_datetime(t["Year Month"].astype(str), errors="coerce")
    if t["_d"].notna().all():
        t = t.sort_values("_d")
    else:
        t = t.sort_values("Year Month")
    return t.drop(columns="_d")


def trend_chart(height=400):
    t = trend_frame()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t["Year Month"], y=t["Sum of Total Sales"], name="Revenue",
                             mode="lines+markers", line=dict(color="#3b82f6", width=3),
                             fill="tozeroy", fillcolor="rgba(59,130,246,0.12)"))
    fig.add_trace(go.Scatter(x=t["Year Month"], y=t["Sum of Estimated Profit"], name="Profit",
                             mode="lines+markers", line=dict(color="#22c55e", width=3)))
    fig.update_layout(title="Monthly Revenue & Profit Trend",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return style(fig, height), t


# ==================================================
# 10. OVERVIEW
# ==================================================
if page == "Overview":

    hero("Retail Intelligence Dashboard",
         "Track revenue, profit and demand in one place. Use the filters to explore any slice.")

    if active_filters:
        st.caption("Active filters: " + "  •  ".join(str(x) for x in active_filters))

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("TOTAL REVENUE", short_money(total_sales), money(total_sales), "#3b82f6")
    with c2: kpi("EST. PROFIT", short_money(total_profit), f"Assumed {margin:.0f}% margin", "#22c55e")
    with c3: kpi("UNITS SOLD", f"{total_quantity:,.0f}", "Total quantity", "#f59e0b")
    with c4: kpi("PRODUCTS", f"{total_products:,}", f"{total_countries} countries", "#8b5cf6")

    st.write("")

    # Auto insights
    country_sales = (df.groupby("Country")["Sum of Total Sales"].sum()
                     .sort_values(ascending=False))
    product_sales = (df.groupby("Description")["Sum of Total Sales"].sum()
                     .sort_values(ascending=False))
    top_c = country_sales.index[0]
    top_c_share = country_sales.iloc[0] / country_sales.sum() * 100
    top_p = product_sales.index[0]
    top10_share = product_sales.head(10).sum() / product_sales.sum() * 100

    i1, i2 = st.columns(2)
    i1.markdown(f'<div class="insight">🌍 <b>{top_c}</b> is the largest market — '
                f'<b>{top_c_share:.1f}%</b> of total revenue.</div>', unsafe_allow_html=True)
    i2.markdown(f'<div class="insight">🏆 Top product <b>{top_p}</b>. Top 10 products '
                f'account for <b>{top10_share:.1f}%</b> of revenue.</div>', unsafe_allow_html=True)

    top_row_share = df["Sum of Total Sales"].max() / total_sales * 100 if total_sales else 0
    if top_row_share >= 10:
        st.markdown(f'<div class="insight">⚠️ A single record makes up <b>{top_row_share:.1f}%</b> of total revenue '
                    f'(bulk order). The trend spike comes from it. Use "Exclude bulk orders" in the sidebar to see the normal trend.</div>',
                    unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📈 Trend", "🌍 Countries & Products", "🗂️ Data"])

    with tab1:
        fig, _ = trend_chart()
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(hbar(country_sales.head(10), "Top Countries by Revenue"),
                            use_container_width=True)
        with right:
            st.plotly_chart(hbar(product_sales.head(10), "Top Products by Revenue", "#8b5cf6"),
                            use_container_width=True)
        st.plotly_chart(donut(country_sales.head(6), "Revenue Share — Top 6 Countries", 360),
                        use_container_width=True)

    with tab3:
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"Customer Records: {customer_records:,.0f} (aggregated count, not unique customers).")

# ==================================================
# 11. DEMAND PREDICTION
# ==================================================
elif page == "Demand Prediction":

    hero("🔮 Product Demand Prediction",
         "Estimated typical product demand from the trained Random Forest model.")

    # Independent of the global filters: options come from the full dataset
    prediction_countries = sorted(original_df["Country"].dropna().unique().tolist())
    prediction_products = sorted(original_df["Description"].dropna().unique().tolist())
    prediction_years = sorted(original_df["Year"].dropna().astype(int).unique().tolist())
    st.caption("Prediction inputs are independent of the sidebar filters.")

    with st.form("prediction_form"):
        a, b = st.columns(2)
        country = a.selectbox("Select Country", prediction_countries)
        product = b.selectbox("Select Product", prediction_products)
        c1, c2, c3 = st.columns(3)
        month = c1.selectbox("Select Month", month_order)
        year = c2.selectbox("Select Year", prediction_years)
        unit_price = c3.number_input(f"Unit Price ({CURRENCY})", min_value=0.01,
                                     value=8.50, step=0.50)
        predict_button = st.form_submit_button("Predict Product Demand")

    if predict_button:
        try:
            pred = float(predict_demand(country, product, month, year, [unit_price])[0])

            # Historical comparison: average for the same product + country
            hist = original_df[(original_df["Description"] == product) &
                               (original_df["Country"] == country)]["Sum of Quantity"]
            hist_avg = float(hist.mean()) if len(hist) else None

            st.divider()
            r1, r2, r3 = st.columns(3)
            with r1: kpi("PREDICTED DEMAND", f"{pred:.1f} units", "Model estimate", "#3b82f6")
            with r2:
                kpi("HISTORICAL AVERAGE",
                    f"{hist_avg:.1f} units" if hist_avg is not None else "N/A",
                    f"{len(hist)} past records" if len(hist) else "No data for this combination",
                    "#f59e0b")
            with r3:
                if hist_avg:
                    diff = (pred - hist_avg) / hist_avg * 100
                    kpi("VS HISTORY", f"{diff:+.1f}%", "Prediction − average", "#22c55e" if diff >= 0 else "#ef4444")
                else:
                    kpi("VS HISTORY", "N/A", "Cannot be compared", "#64748b")

            if not len(hist):
                st.warning("This product-country combination was not found in the data. "
                           "Treat this prediction with less confidence.")

            unseen = unseen_inputs(country, product, month)
            if unseen:
                st.warning("These values are not among the model's trained features: "
                           + ", ".join(unseen)
                           + ". They have no effect on the prediction, so the result is less reliable.")

            # Price sensitivity curve
            prices = np.linspace(max(0.5, unit_price * 0.3), unit_price * 3, 25)
            curve = predict_demand(country, product, month, year, prices)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=prices, y=curve, mode="lines+markers",
                                     line=dict(color="#8b5cf6", width=3), name="Predicted demand"))
            fig.add_trace(go.Scatter(x=[unit_price], y=[pred], mode="markers",
                                     marker=dict(size=14, color="#22c55e"), name="Your price"))
            fig.update_layout(title="Price vs Predicted Demand (Experimental)",
                              xaxis_title=f"Unit Price ({CURRENCY})", yaxis_title="Units")
            st.plotly_chart(style(fig, 380), use_container_width=True)
            st.caption("Experimental model output: the model was run with different prices. "
                       "This is not a real price elasticity analysis.")

            st.info("Experimental model: built for typical orders up to 144 units. "
                    "Predictions are less reliable for bulk orders and new product combinations.")
        except Exception as e:
            st.error(f"Prediction failed: {e}")

# ==================================================
# 12. MODEL PERFORMANCE
# ==================================================
elif page == "Model Performance":

    hero("🧠 Model Performance", "An honest evaluation of the Random Forest demand model.")

    # Previously calculated evaluation results (from the training notebook), not live
    mae, rmse, r2, baseline_mae = 6.26, 12.86, 0.3087, 9.02
    improvement = (baseline_mae - mae) / baseline_mae * 100

    st.caption("📌 The numbers below are previously calculated evaluation results "
               "(753 test records). They are not recalculated from the dashboard filters.")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("MAE", f"{mae:.2f}", "units (avg error)", "#3b82f6")
    with c2: kpi("RMSE", f"{rmse:.2f}", "units", "#8b5cf6")
    with c3: kpi("R² SCORE", f"{r2:.4f}", "Limited explanatory power", "#f59e0b")
    with c4: kpi("VS BASELINE", f"{improvement:.1f}%", "lower MAE", "#22c55e")

    st.write("")
    left, right = st.columns(2)

    with left:
        fig = go.Figure(go.Bar(
            x=["Baseline", "Random Forest"], y=[baseline_mae, mae],
            marker_color=["#64748b", "#3b82f6"],
            text=[f"{baseline_mae:.2f}", f"{mae:.2f}"], textposition="outside"))
        fig.update_layout(title="MAE Comparison (lower is better)", yaxis_title="Units")
        st.plotly_chart(style(fig, 360), use_container_width=True)

    with right:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=r2 * 100,
            number={"suffix": "%"},
            title={"text": "Variance Explained (R²)"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#f59e0b"},
                   "steps": [{"range": [0, 40], "color": "#3b1d1d"},
                             {"range": [40, 70], "color": "#3b331d"},
                             {"range": [70, 100], "color": "#1d3b27"}]}))
        st.plotly_chart(style(fig, 360), use_container_width=True)

    d1, d2, d3 = st.columns(3)
    d1.metric("Evaluation Records", "753")
    d2.metric("Typical Demand Limit", "144 units")
    d3.metric("Algorithm", "Random Forest")

    with st.expander("What do these metrics mean?"):
        st.markdown("""
- **MAE:** Average difference between predicted and actual demand.
- **RMSE:** Like MAE, but penalizes large errors more.
- **R²:** How much of the variation in demand the model explains.
- **Baseline MAE:** Error of a simple guess, used for comparison.
""")

    st.info("These are previously calculated results and are not recalculated from the current filters.")
    st.warning("Limitation: 753 typical-demand test records (up to 144 units). R² = 0.3087 means "
               "the model has limited explanatory power. It is less reliable for bulk orders and unseen combinations. "
               "Do not read these numbers as overall model accuracy.")

# ==================================================
# 13. SALES ANALYTICS
# ==================================================
elif page == "Sales Analytics":

    hero("📈 Sales Analytics", "Sales by country, product and time.")

    c1, c2, c3 = st.columns(3)
    with c1: kpi("REVENUE", short_money(total_sales), money(total_sales), "#3b82f6")
    with c2: kpi("EST. PROFIT", short_money(total_profit), f"Assumed {margin:.0f}% margin", "#22c55e")
    with c3: kpi("QUANTITY SOLD", f"{total_quantity:,.0f}", "units", "#f59e0b")

    st.write("")
    country_sales = (df.groupby("Country")["Sum of Total Sales"].sum()
                     .sort_values(ascending=False).head(15))
    product_sales = (df.groupby("Description")["Sum of Total Sales"].sum()
                     .sort_values(ascending=False).head(10))

    tab1, tab2, tab3 = st.tabs(["🌍 Geography & Products", "📈 Trend", "📥 Report"])

    with tab1:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(hbar(country_sales, "Country-wise Sales", height=480),
                            use_container_width=True)
        with right:
            st.plotly_chart(hbar(product_sales, "Product-wise Sales", "#8b5cf6", 480),
                            use_container_width=True)

        st.caption("Estimated Profit (assumed 25% margin): every row in the dataset has the same 25% margin, "
                   "so this is not actual business profit.")

    with tab2:
        fig, _ = trend_chart(440)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        cols = ["Country", "Description", "Sum of Quantity",
                "Sum of Total Sales", "Sum of Estimated Profit"]
        report = df[cols].copy()
        st.dataframe(report.head(100), use_container_width=True)
        st.caption(f"Showing first 100 of {len(report):,} filtered records.")
        st.download_button("Download Filtered Sales Report (CSV)",
                           report.to_csv(index=False).encode("utf-8"),
                           file_name="RetailPulse_Sales_Report.csv", mime="text/csv")

# ==================================================
# 14. INVENTORY INSIGHTS
# ==================================================
elif page == "Inventory Insights":

    hero("📦 Inventory Insights", "Product quantities and existing stock suggestions.")

    q = df["Sum of Quantity"]
    c1, c2, c3 = st.columns(3)
    with c1: kpi("TOTAL QUANTITY", f"{q.sum():,.0f}", "units", "#3b82f6")
    with c2: kpi("AVERAGE QUANTITY", f"{q.mean():,.2f}", "per record", "#8b5cf6")
    with c3: kpi("MEDIAN QUANTITY", f"{q.median():,.0f}", "per record", "#f59e0b")

    st.write("")
    stock_column = "Stock Suggetion"
    if stock_column in df.columns:
        counts = df[stock_column].value_counts()
        left, right = st.columns(2)
        with left:
            st.plotly_chart(donut(counts, "Existing Stock Suggestions"), use_container_width=True)
        with right:
            product_quantity = (df.groupby("Description")["Sum of Quantity"].sum()
                                .sort_values(ascending=False).head(10))
            st.plotly_chart(hbar(product_quantity, "Top Products by Quantity", "#f59e0b"),
                            use_container_width=True)

    inventory_report = (
        df.groupby("Description")
        .agg(Total_Quantity=("Sum of Quantity", "sum"),
             Total_Revenue=("Sum of Total Sales", "sum"),
             Total_Profit=("Sum of Estimated Profit", "sum"))
        .sort_values("Total_Quantity", ascending=False)
    )

    with st.expander("📋 Product Quantity Details"):
        st.dataframe(inventory_report, use_container_width=True)

    st.download_button("Download Inventory Report (CSV)",
                       inventory_report.to_csv().encode("utf-8"),
                       file_name="RetailPulse_Inventory_Report.csv", mime="text/csv")

    st.info("These are historical dataset records, not live inventory or warehouse stock.")

# ==================================================
# 15. CUSTOMER ANALYTICS
# ==================================================
elif page == "Customer Analytics":

    hero("👥 Customer Analytics", "A view of the customer information available in the aggregated dataset.")

    if "Count of Customer  ID" in df.columns:
        c1, c2 = st.columns(2)
        with c1: kpi("AGGREGATED CUSTOMER COUNT", f"{df['Count of Customer  ID'].sum():,.0f}",
                     "Not unique customers", "#3b82f6")
        with c2: kpi("COUNTRIES", f"{df['Country'].nunique():,}", "represented", "#8b5cf6")
        st.write("")

    left, right = st.columns(2)
    if "Customer Segment" in df.columns:
        with left:
            st.plotly_chart(donut(df["Customer Segment"].value_counts(),
                                  "Existing Customer Segment Records"), use_container_width=True)
    if "Churn Risk" in df.columns:
        with right:
            st.plotly_chart(donut(df["Churn Risk"].value_counts(),
                                  "Existing Churn Risk Records"), use_container_width=True)

    st.warning("Data limitation: the dataset has no individual Customer IDs or customer-level history. "
               "The segment and churn charts show only existing aggregated labels. They are not a validated "
               "segmentation or churn prediction model.")

# ==================================================
# 16. FOOTER
# ==================================================
st.divider()
st.caption("RetailPulse | AI-Powered Retail Analytics | Data Science & Analytics")