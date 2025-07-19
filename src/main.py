import click
import pandas as pd
import os
from src.api_integrator import APIIntegrator
from src.profit_calculator import ProfitCalculator
from src.image_matcher import ImageMatcher
from src.report_generator import ReportGenerator

@click.group()
def cli():
    """A command-line tool for wholesale FBA automation and optimisation."""
    pass

@cli.command()
@click.option('--supplier_file', required=True, help='Path to the cleansed supplier data file (e.g., CSV or Excel).')
@click.option('--amazon_api_key', envvar='AMAZON_API_KEY', help='Amazon MWS API Key.')
@click.option('--keepa_api_key', envvar='KEEPA_API_KEY', help='Keepa API Key.')
@click.option('--jungle_scout_api_key', envvar='JUNGLE_SCOUT_API_KEY', help='Jungle Scout API Key.')
def process_supplier_data(supplier_file, amazon_api_key, keepa_api_key, jungle_scout_api_key):
    """Processes supplier data, enriches it with API data, calculates profitability, and generates reports.

    Assumes supplier_file is already cleansed and structured (e.g., from VBA pre-processing).
    """
    click.echo(f"Starting processing for supplier file: {supplier_file}")

    if not os.path.exists(supplier_file):
        click.echo(f"Error: Supplier file not found at {supplier_file}")
        return

    # Load supplier data (assuming CSV for simplicity, can extend to Excel)
    try:
        supplier_df = pd.read_csv(supplier_file)
        click.echo(f"Loaded {len(supplier_df)} rows from {supplier_file}")
    except Exception as e:
        click.echo(f"Error loading supplier file: {e}")
        return

    api_integrator = APIIntegrator(amazon_api_key, keepa_api_key, jungle_scout_api_key)
    profit_calculator = ProfitCalculator()
    image_matcher = ImageMatcher()
    report_generator = ReportGenerator()

    processed_data = []

    for index, row in supplier_df.iterrows():
        barcode = row['barcode'] # Assuming a 'barcode' column in supplier data
        supplier_buy_price = row['buy_price'] # Assuming a 'buy_price' column
        
        click.echo(f"Processing product with barcode: {barcode}")

        # 1. Amazon API Integration
        amazon_data = api_integrator.get_amazon_product_data(barcode)
        if not amazon_data:
            click.echo(f"  Skipping {barcode}: Could not get Amazon data.")
            continue
        
        asin = amazon_data.get('asin')
        buy_box_price = amazon_data.get('buy_box_price')
        fba_fee = amazon_data.get('fba_fee')
        referral_fee_percentage = amazon_data.get('referral_fee')

        # 2. Keepa API Integration
        keepa_data = api_integrator.get_keepa_product_data(asin)

        # 3. Jungle Scout API Integration
        jungle_scout_data = api_integrator.get_jungle_scout_product_data(asin)

        # 4. Profitability Analysis
        profit = profit_calculator.calculate_profit(
            buy_box_price,
            fba_fee,
            referral_fee_percentage,
            supplier_buy_price
        )
        
        estimated_monthly_sales = jungle_scout_data.get('estimated_monthly_sales', 0)
        number_of_sellers = jungle_scout_data.get('number_of_sellers', 1) # Avoid division by zero

        recommended_units = profit_calculator.calculate_recommended_units(
            estimated_monthly_sales,
            number_of_sellers,
            buy_box_price
        )

        # 5. Image Matching (Conceptual - requires image paths in supplier_df)
        # For a real implementation, supplier_df would need columns for image paths
        # is_image_matched = image_matcher.match_product_image(row['supplier_image_path'], amazon_data.get('amazon_image_path'))
        is_image_matched = True # Simulate for now

        processed_data.append({
            'barcode': barcode,
            'supplier_buy_price': supplier_buy_price,
            'asin': asin,
            'title': amazon_data.get('title'),
            'buy_box_price': buy_box_price,
            'fba_fee': fba_fee,
            'referral_fee_percentage': referral_fee_percentage,
            'profit': profit,
            'estimated_monthly_sales': estimated_monthly_sales,
            'number_of_sellers': number_of_sellers,
            'recommended_units': recommended_units,
            'is_image_matched': is_image_matched,
            'keepa_data': keepa_data, # Include raw API data for detailed report
            'jungle_scout_data': jungle_scout_data # Include raw API data
        })
    
    processed_df = pd.DataFrame(processed_data)

    # Apply image matching to reduce false positives (conceptual)
    # This would typically be applied to a subset of data or as a verification step
    # processed_df = image_matcher.reduce_false_positives(processed_df)

    # 6. Generate Reports
    report_generator.generate_report(processed_df, os.path.join('reports', 'wholesale_analysis_report.csv'))

    click.echo("Processing complete. Check the 'reports/' directory for the analysis report.")

if __name__ == '__main__':
    cli()
