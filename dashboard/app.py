"""
Main Dashboard Application
Interactive CO2 Emissions Dashboard using Dash
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from visualizations import CO2Visualizer

# Initialize app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Tracking Global Carbon Footprints"
)

# Load data
DATA_PATH = Path(__file__).parent.parent / 'data' / 'processed' / 'co2_emissions_processed.csv'
df = pd.read_csv(DATA_PATH)
df['date'] = pd.to_datetime(df['date'])

# Initialize visualizer
viz = CO2Visualizer(df)

# Get unique values for filters
countries = sorted(df['country'].unique())
sectors = sorted(df['sector'].unique())
years = sorted(df['year'].unique())
min_year, max_year = min(years), max(years)

# Top 10 countries for default view
top_10_countries = (df.groupby('country')['value']
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .index.tolist())

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🌍 Tracking Global Carbon Footprints",
                   className="text-center mb-4 mt-4",
                   style={'color': '#00d9ff', 'fontWeight': 'bold'}),
            html.P("Interactive Dashboard for CO2 Emissions Analysis by Country and Sector",
                  className="text-center lead mb-4",
                  style={'color': '#adb5bd'})
        ])
    ]),
    
    html.Hr(style={'borderColor': '#495057'}),
    
    # Key Metrics Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📊 Total Countries", className="card-title"),
                    html.H2(f"{len(countries)}", className="text-primary")
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🏭 Sectors Tracked", className="card-title"),
                    html.H2(f"{len(sectors)}", className="text-success")
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📅 Year Range", className="card-title"),
                    html.H2(f"{min_year}-{max_year}", className="text-warning")
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=3),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📈 Data Points", className="card-title"),
                    html.H2(f"{len(df):,}", className="text-danger")
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=3),
    ]),
    
    # Filters Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🎛️ Filters & Controls", style={'color': '#00d9ff'})),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Countries:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id='country-filter',
                                options=[{'label': c, 'value': c} for c in countries],
                                value=top_10_countries,
                                multi=True,
                                placeholder="Select countries..."
                            )
                        ], md=6),
                        
                        dbc.Col([
                            html.Label("Select Sectors:", style={'fontWeight': 'bold'}),
                            dcc.Dropdown(
                                id='sector-filter',
                                options=[{'label': s, 'value': s} for s in sectors],
                                value=sectors,
                                multi=True,
                                placeholder="Select sectors..."
                            )
                        ], md=6),
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Year Range:", style={'fontWeight': 'bold', 'marginTop': '15px'}),
                            dcc.RangeSlider(
                                id='year-slider',
                                min=min_year,
                                max=max_year,
                                step=1,
                                value=[min_year, max_year],
                                marks={year: str(year) for year in range(min_year, max_year+1, 5)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], md=12),
                    ], className="mt-3"),
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ])
    ]),
    
    # Main Visualizations
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🌐 Global Emissions Trend")),
                dbc.CardBody([
                    dcc.Graph(id='global-trend-chart')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🏆 Top Emitting Countries")),
                dbc.CardBody([
                    dcc.Graph(id='top-emitters-chart')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📊 Emissions by Sector")),
                dbc.CardBody([
                    dcc.Graph(id='sectoral-chart')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("📈 Country-wise Trends")),
                dbc.CardBody([
                    dcc.Graph(id='country-trends-chart')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🔥 Sectoral Emissions Over Time")),
                dbc.CardBody([
                    dcc.Graph(id='sectoral-trend-chart')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🚀 High-Growth Countries")),
                dbc.CardBody([
                    dcc.Graph(id='growth-rate-chart')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=12),
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("🗺️ Animated Global Map")),
                dbc.CardBody([
                    dcc.Graph(id='animated-map')
                ])
            ], className="mb-4", style={'backgroundColor': '#212529'})
        ], md=12),
    ]),
    
    # Footer
    html.Hr(style={'borderColor': '#495057'}),
    dbc.Row([
        dbc.Col([
            html.P("Data Source: Kaggle CO2 Emissions Dataset | Dashboard built with Plotly Dash",
                  className="text-center text-muted mb-4")
        ])
    ])
    
], fluid=True, style={'backgroundColor': '#0a0a0a'})


# Callbacks
@app.callback(
    [Output('global-trend-chart', 'figure'),
     Output('top-emitters-chart', 'figure'),
     Output('sectoral-chart', 'figure'),
     Output('country-trends-chart', 'figure'),
     Output('sectoral-trend-chart', 'figure'),
     Output('growth-rate-chart', 'figure'),
     Output('animated-map', 'figure')],
    [Input('country-filter', 'value'),
     Input('sector-filter', 'value'),
     Input('year-slider', 'value')]
)
def update_charts(selected_countries, selected_sectors, year_range):
    # Filter data
    filtered_df = df.copy()
    
    if selected_countries:
        filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
    
    if selected_sectors:
        filtered_df = filtered_df[filtered_df['sector'].isin(selected_sectors)]
    
    filtered_df = filtered_df[(filtered_df['year'] >= year_range[0]) & 
                              (filtered_df['year'] <= year_range[1])]
    
    # Create visualizer with filtered data
    viz_filtered = CO2Visualizer(filtered_df)
    
    # Generate charts
    global_trend = viz_filtered.create_global_trend()
    top_emitters = viz_filtered.create_top_emitters_bar(n=15, year=year_range[1])
    sectoral = viz_filtered.create_sectoral_breakdown()
    country_trends = viz_filtered.create_country_trends(selected_countries if selected_countries else top_10_countries)
    sectoral_trend = viz_filtered.create_sectoral_trend()
    growth_rate = viz_filtered.create_growth_rate_chart(n=15)
    animated_map = viz_filtered.create_animated_map()
    
    return global_trend, top_emitters, sectoral, country_trends, sectoral_trend, growth_rate, animated_map


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
