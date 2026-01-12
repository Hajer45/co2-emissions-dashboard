"""
Visualization Module for CO2 Emissions Dashboard
Reusable chart functions using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List


class CO2Visualizer:
    """Create interactive visualizations for CO2 emissions data"""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize with processed data"""
        self.data = data
        self.color_scale = 'Reds'
        self.theme_colors = {
            'primary': '#d62728',
            'secondary': '#2ca02c',
            'accent': '#ff7f0e',
            'background': '#1a1a1a',
            'text': '#ffffff'
        }
    
    def create_top_emitters_bar(self, n: int = 15, year: Optional[int] = None) -> go.Figure:
        """Create horizontal bar chart of top emitters"""
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]
            title = f'Top {n} CO2 Emitting Countries - {year}'
        else:
            title = f'Top {n} CO2 Emitting Countries (All Time)'
        
        top_emitters = (df.groupby('country')['value']
                       .sum()
                       .sort_values(ascending=False)
                       .head(n)
                       .reset_index())
        top_emitters.columns = ['country', 'emissions']
        
        fig = px.bar(top_emitters,
                     x='emissions',
                     y='country',
                     orientation='h',
                     title=title,
                     labels={'emissions': 'Total CO2 Emissions', 'country': 'Country'},
                     color='emissions',
                     color_continuous_scale=self.color_scale)
        
        fig.update_layout(
            height=600,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        return fig
    
    def create_global_trend(self) -> go.Figure:
        """Create line chart of global emissions over time"""
        trend = self.data.groupby('year')['value'].sum().reset_index()
        trend.columns = ['year', 'emissions']
        
        fig = px.line(trend,
                      x='year',
                      y='emissions',
                      title='Global CO2 Emissions Trend',
                      labels={'emissions': 'Total CO2 Emissions', 'year': 'Year'},
                      markers=True)
        
        fig.update_traces(line_color=self.theme_colors['primary'], line_width=3)
        fig.update_layout(hovermode='x unified', height=500)
        
        return fig
    
    def create_country_trends(self, countries: List[str]) -> go.Figure:
        """Create multi-line chart for specific countries"""
        df_filtered = self.data[self.data['country'].isin(countries)]
        trend = df_filtered.groupby(['year', 'country'])['value'].sum().reset_index()
        
        fig = px.line(trend,
                      x='year',
                      y='value',
                      color='country',
                      title='CO2 Emissions Trend by Country',
                      labels={'value': 'CO2 Emissions', 'year': 'Year'},
                      markers=True)
        
        fig.update_layout(hovermode='x unified', height=600)
        
        return fig
    
    def create_sectoral_breakdown(self, country: Optional[str] = None) -> go.Figure:
        """Create bar chart of emissions by sector"""
        df = self.data.copy()
        
        if country:
            df = df[df['country'] == country]
            title = f'CO2 Emissions by Sector - {country}'
        else:
            title = 'Global CO2 Emissions by Sector'
        
        sectoral = (df.groupby('sector')['value']
                   .sum()
                   .sort_values(ascending=False)
                   .reset_index())
        sectoral.columns = ['sector', 'emissions']
        
        fig = px.bar(sectoral,
                     x='sector',
                     y='emissions',
                     title=title,
                     labels={'emissions': 'Total CO2 Emissions', 'sector': 'Sector'},
                     color='emissions',
                     color_continuous_scale='Viridis')
        
        fig.update_layout(xaxis_tickangle=-45, height=500)
        
        return fig
    
    def create_sectoral_trend(self) -> go.Figure:
        """Create stacked area chart of sectoral emissions over time"""
        trend = self.data.groupby(['year', 'sector'])['value'].sum().reset_index()
        
        fig = px.area(trend,
                      x='year',
                      y='value',
                      color='sector',
                      title='CO2 Emissions by Sector Over Time',
                      labels={'value': 'CO2 Emissions', 'year': 'Year'})
        
        fig.update_layout(hovermode='x unified', height=600)
        
        return fig
    
    def create_animated_map(self) -> go.Figure:
        """Create animated choropleth map"""
        yearly = self.data.groupby(['country', 'year'])['value'].sum().reset_index()
        yearly.columns = ['country', 'year', 'emissions']
        
        fig = px.choropleth(yearly,
                           locations='country',
                           locationmode='country names',
                           color='emissions',
                           hover_name='country',
                           animation_frame='year',
                           color_continuous_scale=self.color_scale,
                           title='Global CO2 Emissions Over Time',
                           labels={'emissions': 'CO2 Emissions'})
        
        fig.update_layout(height=600)
        
        return fig
    
    def create_growth_rate_chart(self, n: int = 20) -> go.Figure:
        """Create chart showing countries with highest growth rates"""
        # Calculate growth rates
        yearly = self.data.groupby(['country', 'year'])['value'].sum().reset_index()
        yearly = yearly.sort_values(['country', 'year'])
        yearly['prev_emissions'] = yearly.groupby('country')['value'].shift(1)
        yearly['growth_rate'] = ((yearly['value'] - yearly['prev_emissions']) / 
                                 yearly['prev_emissions'] * 100)
        
        # Get recent average growth
        recent_years = yearly['year'].max() - 5
        recent = yearly[yearly['year'] >= recent_years]
        avg_growth = recent.groupby('country')['growth_rate'].mean().reset_index()
        avg_growth = avg_growth.sort_values('growth_rate', ascending=False).head(n)
        
        fig = px.bar(avg_growth,
                     x='growth_rate',
                     y='country',
                     orientation='h',
                     title=f'Top {n} Countries by Average CO2 Growth Rate (Last 5 Years)',
                     labels={'growth_rate': 'Average Growth Rate (%)', 'country': 'Country'},
                     color='growth_rate',
                     color_continuous_scale=self.color_scale)
        
        fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        
        return fig
    
    def create_pie_chart(self, countries: List[str], year: Optional[int] = None) -> go.Figure:
        """Create pie chart for selected countries"""
        df = self.data.copy()
        
        if year:
            df = df[df['year'] == year]
            title = f'CO2 Emissions Share - {year}'
        else:
            title = 'CO2 Emissions Share (All Time)'
        
        df_filtered = df[df['country'].isin(countries)]
        emissions = df_filtered.groupby('country')['value'].sum().reset_index()
        
        fig = px.pie(emissions,
                     values='value',
                     names='country',
                     title=title,
                     hole=0.4)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def create_comparison_chart(self, countries: List[str], metric: str = 'total') -> go.Figure:
        """Create comparison chart for multiple countries"""
        df = self.data[self.data['country'].isin(countries)]
        
        if metric == 'total':
            data = df.groupby('country')['value'].sum().reset_index()
            title = 'Total CO2 Emissions Comparison'
            y_label = 'Total Emissions'
        elif metric == 'average':
            data = df.groupby('country')['value'].mean().reset_index()
            title = 'Average CO2 Emissions Comparison'
            y_label = 'Average Emissions'
        
        fig = px.bar(data,
                     x='country',
                     y='value',
                     title=title,
                     labels={'value': y_label, 'country': 'Country'},
                     color='value',
                     color_continuous_scale=self.color_scale)
        
        fig.update_layout(height=500)
        
        return fig
    
    def create_heatmap(self, countries: List[str], n_years: int = 10) -> go.Figure:
        """Create heatmap of emissions by country and year"""
        df = self.data[self.data['country'].isin(countries)]
        
        # Get recent years
        max_year = df['year'].max()
        min_year = max_year - n_years + 1
        df = df[df['year'] >= min_year]
        
        # Pivot for heatmap
        heatmap_data = df.groupby(['country', 'year'])['value'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='country', columns='year', values='value')
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale=self.color_scale,
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=f'CO2 Emissions Heatmap (Last {n_years} Years)',
            xaxis_title='Year',
            yaxis_title='Country',
            height=600
        )
        
        return fig
