import click
import requests
import os

class APIIntegrator:
    def __init__(self, amazon_api_key=None, keepa_api_key=None, jungle_scout_api_key=None):
        self.amazon_api_key = amazon_api_key or os.getenv('AMAZON_API_KEY')
        self.keepa_api_key = keepa_api_key or os.getenv('KEEPA_API_KEY')
        self.jungle_scout_api_key = jungle_scout_api_key or os.getenv('JUNGLE_SCOUT_API_KEY')

    def get_amazon_product_data(self, asin):
        click.echo(f"  Integrating with Amazon SP-API for ASIN: {asin}...")
        if not self.amazon_api_key:
            click.echo("    Amazon API Key not provided. Skipping Amazon integration.")
            return {}

        # Endpoint for Catalog Items API (v2022-04-01) to get item details by ASIN.
        amazon_api_url = f"https://sellingpartnerapi-eu.amazon.com/catalog/2022-04-01/items/{asin}" # Example for EU region
        headers = {
            "x-amz-access-token": self.amazon_api_key,
            "Content-Type": "application/json"
        }
        params = {
            "marketplaceIds": "A1F83G8C2ARO7P" # UK Marketplace ID
        }

        try:
            response = requests.get(amazon_api_url, headers=headers, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()

            # Parse Amazon SP-API Catalog Items response
            amazon_data = {
                'asin': data.get('asin'),
                'title': data.get('attributes', {}).get('item_name', [{}])[0].get('value'),
                'buy_box_price': data.get('summaries', [{}])[0].get('buyBoxPrice', {}).get('amount'),
                'sales_rank': data.get('salesRanks', [{}])[0].get('rank'),
            }
            
            # Get FBA and Referral Fees using Product Fees API
            buy_box_price = amazon_data.get('buy_box_price')
            if buy_box_price:
                fees = self.get_amazon_fees(asin, buy_box_price, params["marketplaceIds"])
                amazon_data['fba_fee'] = fees.get('fba_fee')
                amazon_data['referral_fee'] = fees.get('referral_fee')

            return amazon_data

        except requests.exceptions.RequestException as e:
            click.echo(f"    Error during Amazon SP-API call: {e}")
            return {}
        # --- END AMAZON SP-API CATALOG ITEMS INTEGRATION ---

    def get_asin_from_barcode(self, barcode, domain=3):
        click.echo(f"  Attempting to get ASIN from barcode {barcode} using Keepa API...")
        if not self.keepa_api_key:
            click.echo("    Keepa API Key not provided. Cannot convert barcode to ASIN.")
            return None

        # Keepa API endpoint for product lookup by barcode
        keepa_api_url = f"https://api.keepa.com/product?key={self.keepa_api_key}&code={barcode}&domain={domain}"

        try:
            response = requests.get(keepa_api_url)
            response.raise_for_status()
            data = response.json()

            # Check if products are returned and extract ASIN
            products = data.get('products')
            if products and len(products) > 0:
                asin = products[0].get('asin')
                if asin:
                    click.echo(f"    Found ASIN: {asin} for barcode: {barcode}")
                    return asin
            click.echo(f"    No ASIN found for barcode: {barcode}")
            return None

        except requests.exceptions.RequestException as e:
            click.echo(f"    Error during Keepa API barcode-to-ASIN conversion: {e}")
            return None

    def get_amazon_fees(self, asin, price, marketplace_id="A1F83G8C2ARO7P"):
        click.echo(f"  Integrating with Amazon SP-API Product Fees for ASIN: {asin}...")
        if not self.amazon_api_key:
            click.echo("    Amazon API Key not provided. Skipping Amazon fees integration.")
            return {"fba_fee": None, "referral_fee": None}

        # Endpoint for Product Fees API (v0) to get fee estimates.
        fees_api_url = f"https://sellingpartnerapi-eu.amazon.com/fees/v0/products/feesEstimate"
        headers = {
            "x-amz-access-token": self.amazon_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "FeesEstimateRequest": {
                "MarketplaceId": marketplace_id,
                "PriceToEstimateFees": {
                    "ListingPrice": {
                        "Amount": price,
                        "CurrencyCode": "GBP" # Assuming UK marketplace
                    }
                },
                "Identifier": asin,
                "IsASIN": True
            }
        }

        try:
            response = requests.post(fees_api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            fba_fee = None
            referral_fee = None

            # Parse fees from the response
            fees_estimate = data.get("FeesEstimateResult", {}).get("FeesEstimate", {})
            for fee in fees_estimate.get("Fees", []):
                if fee.get("FeeType") == "FBAFees":
                    fba_fee = fee.get("FeeAmount")
                elif fee.get("FeeType") == "ReferralFee":
                    referral_fee = fee.get("FeeAmount")
            
            return {"fba_fee": fba_fee, "referral_fee": referral_fee}

        except requests.exceptions.RequestException as e:
            click.echo(f"    Error during Amazon Product Fees API call: {e}")
            return {"fba_fee": None, "referral_fee": None}
        # --- END AMAZON SP-API PRODUCT FEES INTEGRATION ---

    def get_jungle_scout_product_data(self, asin):
        click.echo(f"  Integrating with Jungle Scout API for ASIN: {asin}...")
        if not self.jungle_scout_api_key:
            click.echo("    Jungle Scout API Key not provided. Skipping Jungle Scout integration.")
            return {}

        # This uses the Product Database API as an example.
        jungle_scout_api_url = f"https://api.junglescout.com/api/v1/products" # Common endpoint
        headers = {
            "Authorization": f"Bearer {self.jungle_scout_api_key}", # Common authentication method
            "Content-Type": "application/json"
        }
        params = {"asin": asin} # Common parameter

        try:
            response = requests.get(jungle_scout_api_url, headers=headers, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()

            # Parse Jungle Scout API response
            jungle_scout_data = {
                'estimated_monthly_sales': data.get('data', [{}])[0].get('estimated_sales'),
                'number_of_sellers': data.get('data', [{}])[0].get('seller_count'),
                'opportunity_score': data.get('data', [{}])[0].get('opportunity_score')
            }
            return jungle_scout_data

        except requests.exceptions.RequestException as e:
            click.echo(f"    Error during Jungle Scout API call: {e}")
            return {}
        # --- END JUNGLE SCOUT API INTEGRATION ---
