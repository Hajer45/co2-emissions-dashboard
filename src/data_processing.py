"""
Data Processing Module for CO2 Emissions Analysis
Handles loading, cleaning, and preprocessing of CO2 emissions data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional


class CO2DataProcessor:
    """Process and clean CO2 emissions data"""
    
    def __init__(self, data_path: str = "data/raw/dataset.csv"):
        """Initialize processor with data path"""
        self.data_path = Path(data_path)
        self.raw_data = None
        self.processed_data = None
        
    def load_data(self) -> pd.DataFrame:
        """Load raw CSV data"""
        print(f"Loading data from {self.data_path}...")
        self.raw_data = pd.read_csv(self.data_path)
        print(f"Loaded {len(self.raw_data):,} rows and {len(self.raw_data.columns)} columns")
        return self.raw_data
    
    def explore_data(self) -> dict:
        """Get basic data exploration statistics"""
        if self.raw_data is None:
            self.load_data()
            
        exploration = {
            'shape': self.raw_data.shape,
            'columns': self.raw_data.columns.tolist(),
            'dtypes': self.raw_data.dtypes.to_dict(),
            'missing_values': self.raw_data.isnull().sum().to_dict(),
            'unique_countries': self.raw_data['country'].nunique() if 'country' in self.raw_data.columns else 0,
            'unique_sectors': self.raw_data['sector'].nunique() if 'sector' in self.raw_data.columns else 0,
            'date_range': (self.raw_data['date'].min(), self.raw_data['date'].max()) if 'date' in self.raw_data.columns else None,
            'sample_data': self.raw_data.head(10)
        }
        return exploration
    
    def clean_data(self) -> pd.DataFrame:
        """Clean and preprocess the data"""
        if self.raw_data is None:
            self.load_data()
            
        print("Cleaning data...")
        df = self.raw_data.copy()
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        
        # Ensure value column is numeric
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Remove rows with missing critical values
        initial_rows = len(df)
        df = df.dropna(subset=['country', 'date', 'value'])
        removed_rows = initial_rows - len(df)
        print(f"Removed {removed_rows:,} rows with missing critical values")
        
        # Clean country names (strip whitespace)
        df['country'] = df['country'].str.strip()
        df['sector'] = df['sector'].str.strip() if 'sector' in df.columns else None
        
        self.processed_data = df
        print(f"Cleaned data: {len(df):,} rows")
        return df
    
    def add_derived_metrics(self, population_data: Optional[pd.DataFrame] = None,
                           gdp_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Add derived metrics like per capita emissions"""
        if self.processed_data is None:
            self.clean_data()
            
        df = self.processed_data.copy()
        
        # Calculate total emissions by country and year
        yearly_totals = df.groupby(['country', 'year'])['value'].sum().reset_index()
        yearly_totals.rename(columns={'value': 'total_emissions'}, inplace=True)
        
        # Merge back to main dataframe
        df = df.merge(yearly_totals, on=['country', 'year'], how='left')
        
        # If population data is provided, calculate per capita
        if population_data is not None:
            df = df.merge(population_data, on=['country', 'year'], how='left')
            df['emissions_per_capita'] = df['total_emissions'] / df['population']
        
        # If GDP data is provided, calculate emission intensity
        if gdp_data is not None:
            df = df.merge(gdp_data, on=['country', 'year'], how='left')
            df['emission_intensity'] = df['total_emissions'] / df['gdp']
        
        self.processed_data = df
        return df
    
    def calculate_growth_rates(self) -> pd.DataFrame:
        """Calculate year-over-year emission growth rates"""
        if self.processed_data is None:
            self.clean_data()
            
        df = self.processed_data.copy()
        
        # Get yearly totals by country
        yearly = df.groupby(['country', 'year'])['value'].sum().reset_index()
        yearly = yearly.sort_values(['country', 'year'])
        
        # Calculate growth rate
        yearly['prev_year_emissions'] = yearly.groupby('country')['value'].shift(1)
        yearly['growth_rate'] = ((yearly['value'] - yearly['prev_year_emissions']) / 
                                 yearly['prev_year_emissions'] * 100)
        
        return yearly
    
    def get_top_emitters(self, n: int = 10, by_year: Optional[int] = None) -> pd.DataFrame:
        """Get top N emitting countries"""
        if self.processed_data is None:
            self.clean_data()
            
        df = self.processed_data.copy()
        
        if by_year:
            df = df[df['year'] == by_year]
        
        top_emitters = (df.groupby('country')['value']
                       .sum()
                       .sort_values(ascending=False)
                       .head(n)
                       .reset_index())
        top_emitters.columns = ['country', 'total_emissions']
        
        return top_emitters
    
    def get_sectoral_breakdown(self, country: Optional[str] = None) -> pd.DataFrame:
        """Get emissions breakdown by sector"""
        if self.processed_data is None:
            self.clean_data()
            
        df = self.processed_data.copy()
        
        if country:
            df = df[df['country'] == country]
        
        sectoral = (df.groupby('sector')['value']
                   .sum()
                   .sort_values(ascending=False)
                   .reset_index())
        sectoral.columns = ['sector', 'total_emissions']
        
        return sectoral
    
    def save_processed_data(self, output_path: str = "data/processed/co2_emissions_processed.csv"):
        """Save processed data to CSV"""
        if self.processed_data is None:
            self.clean_data()
            
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.processed_data.to_csv(output_path, index=False)
        print(f"Saved processed data to {output_path}")
        

def main():
    """Main function for testing"""
    processor = CO2DataProcessor()
    
    # Load and explore
    processor.load_data()
    exploration = processor.explore_data()
    
    print("\n=== DATA EXPLORATION ===")
    print(f"Shape: {exploration['shape']}")
    print(f"Columns: {exploration['columns']}")
    print(f"Unique Countries: {exploration['unique_countries']}")
    print(f"Unique Sectors: {exploration['unique_sectors']}")
    print(f"Date Range: {exploration['date_range']}")
    print(f"\nMissing Values:\n{exploration['missing_values']}")
    print(f"\nSample Data:\n{exploration['sample_data']}")
    
    # Clean data
    processor.clean_data()
    
    # Get top emitters
    print("\n=== TOP 10 EMITTERS (ALL TIME) ===")
    top_emitters = processor.get_top_emitters(n=10)
    print(top_emitters)
    
    # Save processed data
    processor.save_processed_data()
    

if __name__ == "__main__":
    main()
