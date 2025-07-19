import click
import pandas as pd
import os
from src.api_integrator import APIIntegrator
from src.profit_calculator import ProfitCalculator
from src.google_sheets_integrator import GoogleSheetsIntegrator

@click.group()
def cli():
    """A command-line tool for wholesale FBA automation and optimisation."""
    pass

@cli.command()
@click.option('--spreadsheet_name', required=True, help='Name of the Google Spreadsheet.')
@click.option('--worksheet_name', default=0, help='Name or index of the worksheet within the spreadsheet.')
@click.option('--amazon_api_key', envvar='AMAZON_API_KEY', help='Amazon MWS API Key.')
@click.option('--keepa_api_key', envvar='KEEPA_API_KEY', help='Keepa API Key.')
@click.option('--jungle_scout_api_key', envvar='JUNGLE_SCOUT_API_KEY', help='Jungle Scout API Key.')
def process_supplier_data(spreadsheet_name, worksheet_name, amazon_api_key, keepa_api_key, jungle_scout_api_key):
    """Processes supplier data from Google Sheet, enriches it with API data, and writes back to the sheet.
    """
    click.echo(f"Starting processing for Google Spreadsheet: {spreadsheet_name}, Worksheet: {worksheet_name}")

    google_sheets_integrator = GoogleSheetsIntegrator()
    api_integrator = APIIntegrator(amazon_api_key, keepa_api_key, jungle_scout_api_key)
    profit_calculator = ProfitCalculator()

    supplier_df = google_sheets_integrator.read_sheet_to_dataframe(spreadsheet_name, worksheet_name)
    if supplier_df.empty:
        click.echo("No data found in the specified Google Sheet. Exiting.")
        return

    click.echo(f"Loaded {len(supplier_df)} rows from Google Sheet.")

    processed_data = []

    for index, row in supplier_df.iterrows():
        barcode = row['barcode'] # Assuming a 'barcode' column in supplier data
        supplier_buy_price = row['buy_price'] # Assuming a 'buy_price' column
        
        click.echo(f"Processing product with barcode: {barcode}")

        # 1. Amazon API Integration
        # If ASIN is not directly available, attempt to get it from barcode using Keepa API
        asin = row.get('asin')
        if not asin and barcode:
            asin = api_integrator.get_asin_from_barcode(barcode)

        if not asin:
            click.echo(f"  Skipping {barcode}: ASIN not found or derivable.")
            continue

        amazon_data = api_integrator.get_amazon_product_data(asin)
        if not amazon_data:
            click.echo(f"  Skipping {barcode}: Could not get Amazon data.")
            continue
        
        buy_box_price = amazon_data.get('buy_box_price')
        fba_fee = amazon_data.get('fba_fee')
        referral_fee_percentage = amazon_data.get('referral_fee')

        # 2. Keepa API Integration
        keepa_data = api_integrator.get_keepa_product_data(asin)
        competitive_sellers = keepa_data.get('competitive_sellers', 1) # Default to 1 to avoid division by zero

        # 3. Jungle Scout API Integration
        jungle_scout_data = api_integrator.get_jungle_scout_product_data(asin)

        # 4. Profitability Analysis
        profit = profit_calculator.calculate_profit(
            buy_box_price,
            fba_fee,
            referral_fee_percentage,
            supplier_buy_price
        )
        
        profit_percentage = profit_calculator.calculate_profit_percentage(profit, buy_box_price)
        roi = profit_calculator.calculate_roi(profit, supplier_buy_price)
        
        estimated_monthly_sales = jungle_scout_data.get('estimated_monthly_sales', 0)

        recommended_units = profit_calculator.calculate_recommended_units(
            estimated_monthly_sales,
            competitive_sellers,
            buy_box_price
        )

        # Image-based Verification (Image comparison handled by VBA in Google Sheet)
        supplier_image_url = row.get('supplier_image_url') # Assuming this column exists in your sheet
        amazon_image_url = amazon_data.get('main_image_url')
        # The Python script will pull the Amazon image URL and write it back to the sheet.
        # The VBA macro will then perform the actual image comparison.

        processed_data.append({
            'barcode': barcode,
            'supplier_buy_price': supplier_buy_price,
            'asin': asin,
            'title': amazon_data.get('title'),
            'buy_box_price': buy_box_price,
            'fba_fee': fba_fee,
            'referral_fee_percentage': referral_fee_percentage,
            'profit': profit,
            'profit_percentage': profit_percentage,
            'roi': roi,
            'estimated_monthly_sales': estimated_monthly_sales,
            'number_of_sellers': number_of_sellers,
            'recommended_units': recommended_units,
            'amazon_image_url': amazon_image_url, # Write Amazon image URL back to sheet
            'keepa_data': keepa_data, # Include raw API data for detailed report
            'jungle_scout_data': jungle_scout_data # Include raw API data
        })
    
    processed_df = pd.DataFrame(processed_data)

    # Write processed data back to Google Sheet
    google_sheets_integrator.write_dataframe_to_sheet(processed_df, spreadsheet_name, worksheet_name)

    click.echo("Processing complete. Check your Google Sheet for the updated data.")

if __name__ == '__main__':
    cli()