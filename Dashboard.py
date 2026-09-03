import os
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings("ignore")

# ==============================================================================
# 1. PAGE TITLE & AESTHETIC LIGHT-MODE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Plate Mill Dimension Deviation Analysis",
    page_icon="📊",
    layout="wide",
)

# Custom Aesthetic Light-Mode Styling (Slate, Indigo & Soft Neutral Palette)
st.markdown(
    """
    <style>
        /* Main Application Background */
        .stApp {
            background-color: #f8fafc;
            color: #334155;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Clean Modern Header Bar */
        .brand-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #ffffff;
            padding: 20px 28px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
            margin-bottom: 24px;
        }
        .brand-title {
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin: 0;
            color: #0f172a;
        }
        .brand-subtitle {
            font-size: 0.92rem;
            color: #64748b;
            margin-top: 4px;
            font-weight: 500;
        }

        /* Metric Cards Styling */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 16px 20px;
            border: 1px solid #e2e8f0;
            border-top: 4px solid #6366f1; /* Soft Indigo Accent */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
            transition: all 0.2s ease-in-out;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.05);
        }
        div[data-testid="stMetricLabel"] {
            color: #64748b !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 700 !important;
            font-size: 1.5rem !important;
        }

        /* Clean Interactive Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 2px solid #e2e8f0;
        }
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            background-color: #f1f5f9;
            border-radius: 6px 6px 0 0;
            border: 1px solid transparent;
            color: #475569;
            font-weight: 600;
            font-size: 0.9rem;
            padding: 0 18px;
            transition: all 0.2s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e2e8f0;
            color: #0f172a;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4f46e5 !important; /* Vivid Indigo Active Tab */
            color: #ffffff !important;
            border-color: #4f46e5 !important;
        }

        /* Section Headings */
        .section-header {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 700;
            border-bottom: 2px solid #cbd5e1;
            padding-bottom: 8px;
            margin-top: 24px;
            margin-bottom: 18px;
            letter-spacing: -0.01em;
        }

        /* Sidebar Inputs Customization */
        section[data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Bar
st.markdown(
    """
    <div class="brand-header">
        <div>
            <div class="brand-title">Plate Mill Dimension Deviation Analysis</div>
            <div class="brand-subtitle">Process Analysis & Production Quality Control Dashboard</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. FILE UPLOAD & DATA LOADING
# ==============================================================================
fl = st.file_uploader(
    "📂 **Upload Production Dataset (CSV / Excel):**",
    type=["csv", "txt", "xlsx", "xls"],
)

if fl is not None:
    if fl.name.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(fl)
    else:
        df = pd.read_csv(fl)
else:
    data_path = "Plate_deviation_View.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    elif os.path.exists("prodATA.xlsx"):
        df = pd.read_excel("prodATA.xlsx")
    else:
        st.error(
            f"File '{data_path}' or 'prodATA.xlsx' not found. Please upload a dataset to proceed."
        )
        st.stop()

# ==============================================================================
# 3. DATA PREPROCESSING & CALCULATED COLUMNS
# ==============================================================================
# Convert Datetimes
for date_col in ["TIMEROLLINGSTART", "TIMEROLLINGFINISH", "STARTTIME"]:
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# Alias STARTTIME if TIMEROLLINGSTART exists
if "TIMEROLLINGSTART" in df.columns:
    df["STARTTIME"] = df["TIMEROLLINGSTART"]

# Filter out non-operational readings
if "ACTTHICKNESS" in df.columns:
    df = df[df["ACTTHICKNESS"] > 6]

# Calculate Thickness_Deviation
if "Thickness_Deviation" not in df.columns:
    if "ACTTHICKNESS" in df.columns and "PL_TGTTHICKNESS" in df.columns:
        df["Thickness_Deviation"] = df["ACTTHICKNESS"] - df["PL_TGTTHICKNESS"]
    elif "MEASTHICKNESS" in df.columns and "TGTTHICKNESS" in df.columns:
        df["Thickness_Deviation"] = df["MEASTHICKNESS"] - df["TGTTHICKNESS"]
    elif "THICKNESSDEVIATION" in df.columns:
        df["Thickness_Deviation"] = df["THICKNESSDEVIATION"]
    else:
        df["Thickness_Deviation"] = 0.0

# Calculate Width_Deviation
if "Width_Deviation" not in df.columns:
    if "ACTWIDTH" in df.columns and "PL_TGTWIDTH" in df.columns:
        df["Width_Deviation"] = df["ACTWIDTH"] - df["PL_TGTWIDTH"]
    elif "MEASWIDTH" in df.columns and "TGTWIDTH" in df.columns:
        df["Width_Deviation"] = df["MEASWIDTH"] - df["TGTWIDTH"]
    elif "WIDTHDEVIATION" in df.columns:
        df["Width_Deviation"] = df["WIDTHDEVIATION"]
    else:
        df["Width_Deviation"] = 0.0

# Calculate Total Rolling Time (Minutes)
if (
    "TIMEROLLINGFINISH" in df.columns
    and "TIMEROLLINGSTART" in df.columns
    and "Total_Rolling_Time" not in df.columns
):
    df["Total_Rolling_Time"] = (
        df["TIMEROLLINGFINISH"] - df["TIMEROLLINGSTART"]
    ).dt.total_seconds() / 60.0

# Add Shift Column
hours = df["STARTTIME"].dt.hour
conditions = [(hours >= 6) & (hours < 14), (hours >= 14) & (hours < 22)]
choices = ["A Shift", "B Shift"]
df["Shift"] = np.select(conditions, choices, default="C Shift")

# Ensure required string columns exist
for col in [
    "PLATEID",
    "SLABID",
    "STEELGRADE",
    "PL_TGTTHICKNESS",
    "ACTTHICKNESS",
    "PL_TGTWIDTH",
    "ACTWIDTH",
    "RUNINDEX",
]:
    if col not in df.columns:
        df[col] = "N/A"

# Clean Invalid Rows
df = df.dropna(subset=["STARTTIME", "Thickness_Deviation"]).sort_values(
    "STARTTIME"
)
df["STARTTIME_STR"] = df["STARTTIME"].dt.strftime("%Y-%m-%d %H:%M:%S")


# Deviation Bucketing Function
def assign_bucket(val):
    if val > 2.0:
        return "Severe High (> +2.0)"
    elif 0.5 < val <= 2.0:
        return "In Spec High (+0.5 to +2.0)"
    elif -2.0 <= val <= 0.5:
        return "Normal Range (-2.0 to +0.5)"
    else:
        return "Severe Low (< -2.0)"


df["Thick_Deviation_Bucket"] = df["Thickness_Deviation"].apply(assign_bucket)
df["Width_Deviation_Bucket"] = df["Width_Deviation"].apply(assign_bucket)

# ==============================================================================
# 4. DATE RANGE & SIDEBAR FILTERS
# ==============================================================================
min_date = df["STARTTIME"].min()
max_date = df["STARTTIME"].max()

st.sidebar.markdown("### ⚙️ **Dashboard Controls**")
col1, col2 = st.sidebar.columns(2)

with col1:
    date1 = pd.to_datetime(
        st.date_input("Start Date", min_date if pd.notnull(min_date) else None)
    )

with col2:
    date2 = pd.to_datetime(
        st.date_input("End Date", max_date if pd.notnull(max_date) else None)
    )

# Primary Filtering Application
filtered_df = df[
    (df["STARTTIME"] >= date1)
    & (df["STARTTIME"] <= date2 + pd.Timedelta(days=1))
].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 **Dimension Filters**")

# 1. Steel Grade Filter
steel_grades = sorted(filtered_df["STEELGRADE"].astype(str).dropna().unique())
selected_grades = st.sidebar.multiselect("Select Steel Grade(s):", steel_grades)
if selected_grades:
    filtered_df = filtered_df[filtered_df["STEELGRADE"].isin(selected_grades)]

# 2. Plate ID Filter
plate_ids = sorted(filtered_df["PLATEID"].astype(str).dropna().unique())
selected_plates = st.sidebar.multiselect("Select Plate ID(s):", plate_ids)
if selected_plates:
    filtered_df = filtered_df[filtered_df["PLATEID"].isin(selected_plates)]

# 3. Slab ID Filter
slab_ids = sorted(filtered_df["SLABID"].astype(str).dropna().unique())
selected_slabs = st.sidebar.multiselect("Select Slab ID(s):", slab_ids)
if selected_slabs:
    filtered_df = filtered_df[filtered_df["SLABID"].isin(selected_slabs)]

# Empty State Check
if filtered_df.empty:
    st.warning("⚠️ No data available matching the selected filters.")
    st.stop()

# ==============================================================================
# 5. THICKNESS ANALYSIS SECTION
# ==============================================================================
st.markdown(
    '<div class="section-header">📏 Thickness Deviation Overview</div>',
    unsafe_allow_html=True,
)

y_vals_thick = filtered_df["Thickness_Deviation"]
thick_thresholds = {
    "Above +2.0 mm": (y_vals_thick > 2.0).sum(),
    "Above +1.5 mm": (y_vals_thick > 1.5).sum(),
    "Above +1.0 mm": (y_vals_thick > 1.0).sum(),
    "Above +0.5 mm": (y_vals_thick > 0.5).sum(),
    "Below -0.5 mm": (y_vals_thick < -0.5).sum(),
    "Below -1.0 mm": (y_vals_thick < -1.0).sum(),
    "Below -1.5 mm": (y_vals_thick < -1.5).sum(),
    "Below -2.0 mm": (y_vals_thick < -2.0).sum(),
}

m_cols_thick = st.columns(4)
keys_thick = list(thick_thresholds.keys())

for idx, key in enumerate(keys_thick):
    target_col = m_cols_thick[idx % 4]
    target_col.metric(label=key, value=f"{thick_thresholds[key]:,} plates")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for Thickness Analysis
tab1, tab2, tab3 = st.tabs(
    [
        "📈 Thickness Time-Series Trend",
        "📦 Shift & Bucket Box Plots",
        "📋 Active Filtered Data",
    ]
)

# TAB 1: Thickness Time-Series
with tab1:
    fig_line_thick = px.line(
        filtered_df,
        x="STARTTIME",
        y="Thickness_Deviation",
        custom_data=[
            "PLATEID",
            "Shift",
            "PL_TGTTHICKNESS",
            "ACTTHICKNESS",
            "STEELGRADE",
        ],
        title="<b>Plate Mill: Thickness Deviation Over Time</b>",
    )

    fig_line_thick.update_traces(
        mode="lines+markers",
        marker=dict(size=5, color="#4f46e5"),
        line=dict(width=1.5, color="#818cf8"),
        hovertemplate=(
            "<b>Plate ID:</b> %{customdata[0]}<br>"
            + "<b>Shift:</b> %{customdata[1]}<br>"
            + "<b>Target Thickness:</b> %{customdata[2]} mm<br>"
            + "<b>Measured Thickness:</b> %{customdata[3]} mm<br>"
            + "<b>Steel Grade:</b> %{customdata[4]}<br>"
            + "<b>Start Time:</b> %{x|%Y-%m-%d %H:%M:%S}<br>"
            + "<b>Thickness Deviation:</b> %{y:.3f} mm"
            + "<extra></extra>"
        ),
    )

    lines_to_add = [
        {"y": 2.0, "color": "#b91c1c"},
        {"y": 1.5, "color": "#dc2626"},
        {"y": 1.0, "color": "#f59e0b"},
        {"y": 0.5, "color": "#64748b"},
        {"y": -0.5, "color": "#64748b"},
        {"y": -1.0, "color": "#f59e0b"},
        {"y": -1.5, "color": "#dc2626"},
        {"y": -2.0, "color": "#b91c1c"},
    ]

    for line in lines_to_add:
        fig_line_thick.add_hline(
            y=line["y"],
            line_dash="dash",
            line_color=line["color"],
            line_width=1.2,
            annotation_text=f"y = {line['y']}",
            annotation_position="bottom right"
            if line["y"] < 0
            else "top right",
        )

    fig_line_thick.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(step="all", label="All"),
            ]
        ),
    )

    fig_line_thick.update_layout(
        xaxis_title="Start Time",
        yaxis_title="Thickness Deviation (mm)",
        template="plotly_white",
        hovermode="closest",
        yaxis=dict(fixedrange=False),
        height=550,
    )

    st.plotly_chart(fig_line_thick, use_container_width=True)

# TAB 2: Thickness Box Plots
with tab2:
    buckets = [
        "Severe High (> +2.0)",
        "In Spec High (+0.5 to +2.0)",
        "Normal Range (-2.0 to +0.5)",
        "Severe Low (< -2.0)",
    ]

    colors = ["#b91c1c", "#f59e0b", "#10b981", "#dc2626"]

    fig_box_thick = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=buckets,
        shared_xaxes=True,
        vertical_spacing=0.08,
    )

    for idx, (bucket_name, color) in enumerate(zip(buckets, colors), start=1):
        sub_df = filtered_df[
            filtered_df["Thick_Deviation_Bucket"] == bucket_name
        ]

        if not sub_df.empty:
            box_trace = go.Box(
                x=sub_df["Shift"],
                y=sub_df["Thickness_Deviation"],
                name=bucket_name,
                marker_color=color,
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8,
                customdata=np.stack(
                    (
                        sub_df["PLATEID"],
                        sub_df["STARTTIME_STR"],
                        sub_df["STEELGRADE"],
                    ),
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>Plate ID:</b> %{customdata[0]}<br>"
                    "<b>Shift:</b> %{x}<br>"
                    "<b>Start Time:</b> %{customdata[1]}<br>"
                    "<b>Steel Grade:</b> %{customdata[2]}<br>"
                    "<b>Deviation:</b> %{y:.3f} mm<extra></extra>"
                ),
            )
            fig_box_thick.add_trace(box_trace, row=idx, col=1)

        fig_box_thick.update_yaxes(
            title_text="Dev (mm)", fixedrange=False, row=idx, col=1
        )

    lines_to_add_box = [
        {"y": 2.0, "color": "#b91c1c", "row": 1},
        {"y": 0.5, "color": "#f59e0b", "row": 2},
        {"y": -2.0, "color": "#dc2626", "row": 4},
    ]

    for line in lines_to_add_box:
        fig_box_thick.add_hline(
            y=line["y"],
            line_dash="dash",
            line_color=line["color"],
            line_width=1.5,
            annotation_text=f"y = {line['y']}",
            annotation_position="top right",
            row=line["row"],
            col=1,
        )

    fig_box_thick.update_layout(
        title="<b>Plate Mill: Thickness Deviation Box Plots by Bucket & Shift</b>",
        height=900,
        template="plotly_white",
        showlegend=False,
        hovermode="closest",
    )

    fig_box_thick.update_xaxes(title_text="Shift", row=4, col=1)

    st.plotly_chart(fig_box_thick, use_container_width=True)

# TAB 3: Data Inspection
with tab3:
    st.dataframe(filtered_df, use_container_width=True)

# ==============================================================================
# 6. WIDTH ANALYSIS SECTION
# ==============================================================================
st.markdown(
    '<div class="section-header">📐 Width Deviation Overview</div>',
    unsafe_allow_html=True,
)

y_vals_width = filtered_df["Width_Deviation"]
width_thresholds = {
    "Above +2.0 mm": (y_vals_width > 2.0).sum(),
    "Above +1.5 mm": (y_vals_width > 1.5).sum(),
    "Above +1.0 mm": (y_vals_width > 1.0).sum(),
    "Above +0.5 mm": (y_vals_width > 0.5).sum(),
    "Below -0.5 mm": (y_vals_width < -0.5).sum(),
    "Below -1.0 mm": (y_vals_width < -1.0).sum(),
    "Below -1.5 mm": (y_vals_width < -1.5).sum(),
    "Below -2.0 mm": (y_vals_width < -2.0).sum(),
}

m_cols_width = st.columns(4)
keys_width = list(width_thresholds.keys())

for idx, key in enumerate(keys_width):
    target_col = m_cols_width[idx % 4]
    target_col.metric(label=key, value=f"{width_thresholds[key]:,} plates")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs for Width Analysis
tab4, tab5, tab6 = st.tabs(
    [
        "📈 Width Time-Series Trend",
        "📦 Shift & Bucket Box Plots",
        "📋 Filtered Data Table",
    ]
)

# TAB 4: Width Time Series
with tab4:
    fig_line_width = px.line(
        filtered_df,
        x="STARTTIME",
        y="Width_Deviation",
        custom_data=[
            "PLATEID",
            "Shift",
            "PL_TGTWIDTH",
            "ACTWIDTH",
            "STEELGRADE",
        ],
        title="<b>Plate Mill: Width Deviation Over Time</b>",
    )

    fig_line_width.update_traces(
        mode="lines+markers",
        marker=dict(size=5, color="#0284c7"),
        line=dict(width=1.5, color="#38bdf8"),
        hovertemplate=(
            "<b>Plate ID:</b> %{customdata[0]}<br>"
            + "<b>Shift:</b> %{customdata[1]}<br>"
            + "<b>Target Width:</b> %{customdata[2]} mm<br>"
            + "<b>Measured Width:</b> %{customdata[3]} mm<br>"
            + "<b>Steel Grade:</b> %{customdata[4]}<br>"
            + "<b>Start Time:</b> %{x|%Y-%m-%d %H:%M:%S}<br>"
            + "<b>Width Deviation:</b> %{y:.3f} mm"
            + "<extra></extra>"
        ),
    )

    for line in lines_to_add:
        fig_line_width.add_hline(
            y=line["y"],
            line_dash="dash",
            line_color=line["color"],
            line_width=1.2,
            annotation_text=f"y = {line['y']}",
            annotation_position="bottom right"
            if line["y"] < 0
            else "top right",
        )

    fig_line_width.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1h", step="hour", stepmode="backward"),
                dict(count=6, label="6h", step="hour", stepmode="backward"),
                dict(count=1, label="1d", step="day", stepmode="backward"),
                dict(step="all", label="All"),
            ]
        ),
    )

    fig_line_width.update_layout(
        xaxis_title="Start Time",
        yaxis_title="Width Deviation (mm)",
        template="plotly_white",
        hovermode="closest",
        yaxis=dict(fixedrange=False),
        height=550,
    )

    st.plotly_chart(fig_line_width, use_container_width=True)

# TAB 5: Width Box Plots
with tab5:
    fig_box_width = make_subplots(
        rows=4,
        cols=1,
        subplot_titles=buckets,
        shared_xaxes=True,
        vertical_spacing=0.08,
    )

    for idx, (bucket_name, color) in enumerate(zip(buckets, colors), start=1):
        sub_df = filtered_df[
            filtered_df["Width_Deviation_Bucket"] == bucket_name
        ]

        if not sub_df.empty:
            box_trace = go.Box(
                x=sub_df["Shift"],
                y=sub_df["Width_Deviation"],
                name=bucket_name,
                marker_color=color,
                boxpoints="all",
                jitter=0.3,
                pointpos=-1.8,
                customdata=np.stack(
                    (
                        sub_df["PLATEID"],
                        sub_df["STARTTIME_STR"],
                        sub_df["STEELGRADE"],
                    ),
                    axis=-1,
                ),
                hovertemplate=(
                    "<b>Plate ID:</b> %{customdata[0]}<br>"
                    "<b>Shift:</b> %{x}<br>"
                    "<b>Start Time:</b> %{customdata[1]}<br>"
                    "<b>Steel Grade:</b> %{customdata[2]}<br>"
                    "<b>Deviation:</b> %{y:.3f} mm<extra></extra>"
                ),
            )
            fig_box_width.add_trace(box_trace, row=idx, col=1)

        fig_box_width.update_yaxes(
            title_text="Dev (mm)", fixedrange=False, row=idx, col=1
        )

    for line in lines_to_add_box:
        fig_box_width.add_hline(
            y=line["y"],
            line_dash="dash",
            line_color=line["color"],
            line_width=1.5,
            annotation_text=f"y = {line['y']}",
            annotation_position="top right",
            row=line["row"],
            col=1,
        )

    fig_box_width.update_layout(
        title="<b>Plate Mill: Width Deviation Box Plots by Bucket & Shift</b>",
        height=900,
        template="plotly_white",
        showlegend=False,
        hovermode="closest",
    )

    fig_box_width.update_xaxes(title_text="Shift", row=4, col=1)

    st.plotly_chart(fig_box_width, use_container_width=True)

# TAB 6: Data Inspection
with tab6:
    st.dataframe(filtered_df, use_container_width=True)

# ==============================================================================
# 7. OPERATIONAL KPI METRICS (PASSES & ROLLING TIME)
# ==============================================================================
st.markdown(
    '<div class="section-header">🔄 Rolling Operations & Pass Metrics</div>',
    unsafe_allow_html=True,
)

# Pass Count Statistics
if (
    "RUNINDEX" in filtered_df.columns
    and pd.api.types.is_numeric_dtype(filtered_df["RUNINDEX"])
):
    pass_vals = filtered_df["RUNINDEX"].dropna()
    pass_max = pass_vals.max() if not pass_vals.empty else 0
    pass_min = pass_vals.min() if not pass_vals.empty else 0
    pass_median = pass_vals.median() if not pass_vals.empty else 0
    pass_mean = pass_vals.mean() if not pass_vals.empty else 0
    pass_std = pass_vals.std() if not pass_vals.empty else 0
else:
    pass_max = pass_min = pass_median = pass_mean = pass_std = 0.0

st.markdown("##### **Number of Rolling Passes (`RUNINDEX`)**")
m_cols_pass = st.columns(5)
m_cols_pass[0].metric(label="Maximum Passes", value=f"{pass_max:.0f}")
m_cols_pass[1].metric(label="Minimum Passes", value=f"{pass_min:.0f}")
m_cols_pass[2].metric(label="Median Passes", value=f"{pass_median:.1f}")
m_cols_pass[3].metric(label="Mean Passes", value=f"{pass_mean:.1f}")
m_cols_pass[4].metric(label="Standard Deviation", value=f"{pass_std:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Rolling Time Statistics
st.markdown("##### **Total Rolling Time Statistics (Minutes)**")
if (
    "Total_Rolling_Time" in filtered_df.columns
    and pd.api.types.is_numeric_dtype(filtered_df["Total_Rolling_Time"])
):
    time_vals = filtered_df["Total_Rolling_Time"].dropna()
    time_max = time_vals.max() if not time_vals.empty else 0
    time_min = time_vals.min() if not time_vals.empty else 0
    time_median = time_vals.median() if not time_vals.empty else 0
    time_mean = time_vals.mean() if not time_vals.empty else 0
    time_std = time_vals.std() if not time_vals.empty else 0
else:
    time_max = time_min = time_median = time_mean = time_std = 0.0

m_cols_time = st.columns(5)
m_cols_time[0].metric(label="Maximum Time (min)", value=f"{time_max:.2f}")
m_cols_time[1].metric(label="Minimum Time (min)", value=f"{time_min:.2f}")
m_cols_time[2].metric(label="Median Time (min)", value=f"{time_median:.2f}")
m_cols_time[3].metric(label="Mean Time (min)", value=f"{time_mean:.2f}")
m_cols_time[4].metric(label="Std Dev Time (min)", value=f"{time_std:.2f}")

st.markdown("---")
