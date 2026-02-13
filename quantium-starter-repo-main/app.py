import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# Helpers (make it robust)
# -----------------------------
def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def _find_col(df: pd.DataFrame, candidates):
    cols = set(df.columns)
    for c in candidates:
        if c in cols:
            return c
    # fallback: partial match
    for c in df.columns:
        for cand in candidates:
            if cand in c:
                return c
    return None

def _empty_figure(message="No data to display"):
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=message,
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16),
            )
        ],
        margin=dict(l=20, r=20, t=40, b=20),
        height=520,
    )
    return fig

# -----------------------------
# 1) Load formatted data (Task 2 output)
# -----------------------------
CSV_FILE = "formatted_sales_data.csv"
raw = pd.read_csv(CSV_FILE)
df = _normalize_cols(raw)

sales_col = _find_col(df, ["sales"])
date_col = _find_col(df, ["date"])
region_col = _find_col(df, ["region"])

# If any required column missing -> still do not crash
if not all([sales_col, date_col, region_col]):
    missing = []
    if not sales_col: missing.append("Sales")
    if not date_col: missing.append("Date")
    if not region_col: missing.append("Region")
    df_clean = None
else:
    # Rename to standard names
    df = df.rename(columns={sales_col: "sales", date_col: "date", region_col: "region"})

    # Clean values
    df["region"] = df["region"].astype(str).str.strip().str.lower()

    # Date parsing
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sales numeric parsing (handles commas, €, $, etc.)
    df["sales"] = (
        df["sales"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip()
    )
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce")

    # Drop unusable rows
    df_clean = df.dropna(subset=["date", "sales", "region"]).copy()

# -----------------------------
# 2) Create app
# -----------------------------
app = Dash(__name__)
app.title = "Pink Morsels Sales Dashboard"

# Regions for radio buttons (Task 4 requirement wants fixed 5 options)
REGION_OPTIONS = [
    {"label": "All", "value": "all"},
    {"label": "North", "value": "north"},
    {"label": "East", "value": "east"},
    {"label": "South", "value": "south"},
    {"label": "West", "value": "west"},
]

# -----------------------------
# 3) Layout (Professional UI)
# -----------------------------
app.layout = html.Div(
    style={
        "fontFamily": "Inter, Arial, sans-serif",
        "background": "linear-gradient(180deg, #f6f8fb 0%, #ffffff 60%)",
        "minHeight": "100vh",
        "padding": "28px",
    },
    children=[
        html.Div(
            style={"maxWidth": "1180px", "margin": "0 auto"},
            children=[
                # Header card
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "16px",
                        "padding": "22px 22px",
                        "boxShadow": "0 10px 30px rgba(16, 24, 40, 0.08)",
                        "border": "1px solid #eef2f7",
                    },
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "gap": "16px", "flexWrap": "wrap"},
                            children=[
                                html.Div(
                                    children=[
                                        html.H1(
                                            "Pink Morsels Sales Dashboard",
                                            style={"margin": "0", "fontSize": "28px", "letterSpacing": "-0.2px"},
                                        ),
                                        html.P(
                                            "Answer: Were sales higher before or after the price increase on 15 Jan 2021?",
                                            style={"margin": "6px 0 0 0", "color": "#667085"},
                                        ),
                                    ],
                                ),
                                html.Div(
                                    style={"textAlign": "right"},
                                    children=[
                                        html.Div(
                                            "Price Increase Marker",
                                            style={"color": "#667085", "fontSize": "12px"},
                                        ),
                                        html.Div(
                                            "15 Jan 2021",
                                            style={"fontWeight": "700", "fontSize": "14px"},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                html.Div(style={"height": "14px"}),

                # Controls + KPIs
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1.2fr 2fr",
                        "gap": "14px",
                        "alignItems": "stretch",
                    },
                    children=[
                        # Controls card
                        html.Div(
                            style={
                                "backgroundColor": "white",
                                "borderRadius": "16px",
                                "padding": "18px",
                                "boxShadow": "0 10px 30px rgba(16, 24, 40, 0.06)",
                                "border": "1px solid #eef2f7",
                            },
                            children=[
                                html.Div("Region filter", style={"fontWeight": "700", "marginBottom": "10px"}),
                                dcc.RadioItems(
                                    id="region-filter",
                                    options=REGION_OPTIONS,
                                    value="all",
                                    inline=False,
                                    style={"display": "grid", "gap": "8px"},
                                    inputStyle={"marginRight": "10px"},
                                    labelStyle={
                                        "padding": "10px 12px",
                                        "border": "1px solid #eef2f7",
                                        "borderRadius": "12px",
                                        "cursor": "pointer",
                                        "backgroundColor": "#fbfcfe",
                                    },
                                ),
                                html.Div(
                                    style={"marginTop": "12px", "color": "#667085", "fontSize": "12px"},
                                    children="Tip: Choose a region to compare patterns before vs after the price change."
                                ),
                            ],
                        ),

                        # KPI cards
                        html.Div(
                            style={
                                "backgroundColor": "white",
                                "borderRadius": "16px",
                                "padding": "18px",
                                "boxShadow": "0 10px 30px rgba(16, 24, 40, 0.06)",
                                "border": "1px solid #eef2f7",
                            },
                            children=[
                                html.Div(
                                    style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "12px"},
                                    children=[
                                        html.Div(
                                            style={
                                                "border": "1px solid #eef2f7",
                                                "borderRadius": "14px",
                                                "padding": "14px",
                                                "backgroundColor": "#fbfcfe",
                                            },
                                            children=[
                                                html.Div("Total Sales", style={"color": "#667085", "fontSize": "12px"}),
                                                html.Div(id="kpi-total", style={"fontSize": "22px", "fontWeight": "800"}),
                                            ],
                                        ),
                                        html.Div(
                                            style={
                                                "border": "1px solid #eef2f7",
                                                "borderRadius": "14px",
                                                "padding": "14px",
                                                "backgroundColor": "#fbfcfe",
                                            },
                                            children=[
                                                html.Div("Avg Daily Sales", style={"color": "#667085", "fontSize": "12px"}),
                                                html.Div(id="kpi-avg", style={"fontSize": "22px", "fontWeight": "800"}),
                                            ],
                                        ),
                                        html.Div(
                                            style={
                                                "border": "1px solid #eef2f7",
                                                "borderRadius": "14px",
                                                "padding": "14px",
                                                "backgroundColor": "#fbfcfe",
                                            },
                                            children=[
                                                html.Div("Days in View", style={"color": "#667085", "fontSize": "12px"}),
                                                html.Div(id="kpi-days", style={"fontSize": "22px", "fontWeight": "800"}),
                                            ],
                                        ),
                                    ],
                                ),

                                html.Div(style={"height": "10px"}),

                                dcc.Graph(
                                    id="sales-chart",
                                    config={"displayModeBar": False},
                                    style={"height": "520px"},
                                ),
                            ],
                        ),
                    ],
                ),

                html.Div(
                    style={"marginTop": "10px", "color": "#667085", "fontSize": "12px", "textAlign": "center"},
                    children="Built with Dash + Plotly • Data: formatted_sales_data.csv",
                ),
            ],
        )
    ],
)

# -----------------------------
# 4) Callback
# -----------------------------
@app.callback(
    Output("sales-chart", "figure"),
    Output("kpi-total", "children"),
    Output("kpi-avg", "children"),
    Output("kpi-days", "children"),
    Input("region-filter", "value"),
)
def update(region_value):
    # If columns missing, show message
    if df_clean is None:
        msg = f"CSV columns missing. Expected: Sales, Date, Region. Missing: {', '.join(missing)}"
        return _empty_figure(msg), "—", "—", "—"

    dff = df_clean.copy()

    if region_value != "all":
        dff = dff[dff["region"] == region_value]

    if dff.empty:
        return _empty_figure("No data for this region."), "0", "0", "0"

    # Group by day (Task requirement: sorted by date)
    daily = dff.groupby("date", as_index=False)["sales"].sum().sort_values("date")

    total_sales = float(daily["sales"].sum())
    avg_daily = float(daily["sales"].mean())
    days = int(daily.shape[0])

    fig = px.line(
        daily,
        x="date",
        y="sales",
        title="Pink Morsels Daily Sales (Quantity × Price)",
        labels={"date": "Date", "sales": "Sales"},
        template="plotly_white",
    )
    fig.update_traces(line=dict(width=2))
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=20),
        height=520,
        title_font=dict(size=16),
    )

    # Price increase marker (15 Jan 2021)
    fig.add_vline(x=pd.to_datetime("2021-01-15"), line_dash="dash", line_width=2)
    fig.add_annotation(
        x=pd.to_datetime("2021-01-15"),
        y=max(daily["sales"]),
        text="Price increase (15 Jan 2021)",
        showarrow=True,
        arrowhead=2,
        yshift=20,
    )

    return (
        fig,
        f"{total_sales:,.0f}",
        f"{avg_daily:,.0f}",
        f"{days:,}",
    )

# -----------------------------
# 5) Run
# -----------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
