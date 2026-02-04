import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# -----------------------------
# 1) Load cleaned data
# -----------------------------
df = pd.read_csv("cleaned_sales_data.csv")

# Clean columns
df["product"] = df["product"].astype(str).str.strip().str.lower()
df["region"] = df["region"].astype(str).str.strip().str.lower()

# Convert date text -> real date
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Convert price like "$3.00" -> 3.00
df["price"] = (
    df["price"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.strip()
)
df["price"] = pd.to_numeric(df["price"], errors="coerce")

# Convert quantity to number
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")

# Keep only Pink Morsels (safe)
df = df[df["product"] == "pink morsel"].copy()

# Drop bad rows (missing critical values)
df = df.dropna(subset=["date", "price", "quantity", "region"])

# Add revenue column
df["revenue"] = df["price"] * df["quantity"]

# Get min/max dates for picker
min_date = df["date"].min()
max_date = df["date"].max()

# -----------------------------
# 2) Create app
# -----------------------------
app = Dash(__name__)
app.title = "Pink Morsels Dashboard"


# -----------------------------
# 3) Layout (your company UI)
# -----------------------------
app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f5f7fb",
        "minHeight": "100vh",
        "padding": "24px",
    },
    children=[
        # Header
        html.Div(
            style={
                "maxWidth": "1200px",
                "margin": "0 auto 16px auto",
            },
            children=[
                html.H1("Pink Morsels Dashboard", style={"margin": "0"}),
                html.P(
                    "Explore how the price change affected sales volume and revenue.",
                    style={"margin": "6px 0 0 0", "color": "#555"},
                ),
            ],
        ),

        # Main container
        html.Div(
            style={
                "maxWidth": "1200px",
                "margin": "0 auto",
                "backgroundColor": "white",
                "borderRadius": "14px",
                "padding": "18px",
                "boxShadow": "0 8px 24px rgba(0,0,0,0.08)",
            },
            children=[
                # Filters row
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "16px",
                        "marginBottom": "16px",
                        "alignItems": "end",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.Label("Region", style={"fontWeight": "bold"}),
                                dcc.Dropdown(
                                    id="region",
                                    options=[{"label": "All", "value": "all"}]
                                    + [{"label": r.title(), "value": r}
                                       for r in sorted(df["region"].dropna().unique())],
                                    value="all",
                                    clearable=False,
                                ),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Label("Date range", style={"fontWeight": "bold"}),
                                dcc.DatePickerRange(
                                    id="date_range",
                                    start_date=min_date,
                                    end_date=max_date,
                                    min_date_allowed=min_date,
                                    max_date_allowed=max_date,
                                    display_format="MM/DD/YYYY",
                                    minimum_nights=0,
                                ),
                            ]
                        ),
                    ],
                ),

                # KPI cards row
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(3, 1fr)",
                        "gap": "12px",
                        "marginBottom": "16px",
                    },
                    children=[
                        html.Div(
                            style={
                                "backgroundColor": "#f5f7fb",
                                "borderRadius": "12px",
                                "padding": "14px",
                                "border": "1px solid #e6e9f2",
                            },
                            children=[
                                html.Div("Total Revenue", style={"color": "#666", "fontSize": "13px"}),
                                html.Div(id="kpi_revenue", style={"fontSize": "26px", "fontWeight": "bold"}),
                            ],
                        ),
                        html.Div(
                            style={
                                "backgroundColor": "#f5f7fb",
                                "borderRadius": "12px",
                                "padding": "14px",
                                "border": "1px solid #e6e9f2",
                            },
                            children=[
                                html.Div("Total Quantity", style={"color": "#666", "fontSize": "13px"}),
                                html.Div(id="kpi_qty", style={"fontSize": "26px", "fontWeight": "bold"}),
                            ],
                        ),
                        html.Div(
                            style={
                                "backgroundColor": "#f5f7fb",
                                "borderRadius": "12px",
                                "padding": "14px",
                                "border": "1px solid #e6e9f2",
                            },
                            children=[
                                html.Div("Average Price", style={"color": "#666", "fontSize": "13px"}),
                                html.Div(id="kpi_avg_price", style={"fontSize": "26px", "fontWeight": "bold"}),
                            ],
                        ),
                    ],
                ),

                # Charts row
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1fr 1fr",
                        "gap": "12px",
                    },
                    children=[
                        html.Div(
                            style={
                                "border": "1px solid #e6e9f2",
                                "borderRadius": "12px",
                                "padding": "10px",
                            },
                            children=[
                                html.Div("Quantity Trend", style={"fontWeight": "bold", "marginBottom": "6px"}),
                                dcc.Graph(id="qty_trend", config={"displayModeBar": False}),
                            ],
                        ),
                        html.Div(
                            style={
                                "border": "1px solid #e6e9f2",
                                "borderRadius": "12px",
                                "padding": "10px",
                            },
                            children=[
                                html.Div("Revenue Trend", style={"fontWeight": "bold", "marginBottom": "6px"}),
                                dcc.Graph(id="revenue_trend", config={"displayModeBar": False}),
                            ],
                        ),
                    ],
                ),

                # Footer note
                html.Div(
                    style={"marginTop": "12px", "color": "#777", "fontSize": "12px"},
                    children="Tip: Use Region + Date filters to isolate the impact of the price change."
                )
            ],
        ),
    ],
)


# -----------------------------
# 4) Callback (THE IMPORTANT PART)
# -----------------------------
@app.callback(
    Output("kpi_revenue", "children"),
    Output("kpi_qty", "children"),
    Output("kpi_avg_price", "children"),
    Output("qty_trend", "figure"),
    Output("revenue_trend", "figure"),
    Input("region", "value"),
    Input("date_range", "start_date"),
    Input("date_range", "end_date"),
)
def update_dashboard(region, start_date, end_date):
    dff = df.copy()

    # Filter by region
    if region and region != "all":
        dff = dff[dff["region"] == region]

    # Filter by date range
    if start_date:
        dff = dff[dff["date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["date"] <= pd.to_datetime(end_date)]

    # ✅ If no data, return safe outputs (no crash)
    if dff.empty:
        empty_fig = px.line(title="No data for this filter")
        empty_fig.update_layout(template="plotly_white")
        return "€0", "0", "€0.00", empty_fig, empty_fig

    # KPIs
    total_revenue = dff["revenue"].sum()
    total_qty = int(dff["quantity"].sum())
    avg_price = dff["price"].mean()

    # Group daily for trend charts
    daily = dff.groupby("date", as_index=False).agg(
        quantity=("quantity", "sum"),
        revenue=("revenue", "sum")
    )

    fig_qty = px.line(daily, x="date", y="quantity")
    fig_qty.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))

    fig_rev = px.line(daily, x="date", y="revenue")
    fig_rev.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=10, b=10))

    # Format KPI text nicely
    kpi_revenue_text = f"€{total_revenue:,.0f}"
    kpi_qty_text = f"{total_qty:,}"
    kpi_avg_price_text = f"€{avg_price:,.2f}"

    return kpi_revenue_text, kpi_qty_text, kpi_avg_price_text, fig_qty, fig_rev


# -----------------------------
# 5) Run app
# -----------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
