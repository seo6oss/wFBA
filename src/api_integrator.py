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

            amazon_data = {
                'asin': data.get('asin'),
                'title': data.get('attributes', {}).get('item_name', [{}])[0].get('value'),
                'buy_box_price': data.get('summaries', [{}])[0].get('buyBoxPrice', {}).get('amount'),
                'sales_rank': data.get('salesRanks', [{}])[0].get('rank'),
                'main_image_url': data.get('images', {}).get('main', {}).get('link') # Extract main image URL
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

    def get_keepa_product_data(self, asin):
        click.echo(f"  Integrating with Keepa API for ASIN: {asin}...")
        if not self.keepa_api_key:
            click.echo("    Keepa API Key not provided. Skipping Keepa integration.")
            return {}

        # The domain 'api.keepa.com' is standard. Authentication is via the 'key' query parameter.
        keepa_api_url = f"https://api.keepa.com/product?key={self.keepa_api_key}&asin={asin}&domain=3" # Domain 3 for UK

        try:
            response = requests.get(keepa_api_url)
            response.raise_for_status()
            data = response.json()

            # Parse Keepa API response
            keepa_data = {
                'historical_price': data.get('products', [{}])[0].get('data', {}).get('AMAZON'), # Example: Amazon price history
                'sales_rank_history': data.get('products', [{}])[0].get('data', {}).get('SALES_RANK'),
                'buy_box_history': data.get('products', [{}])[0].get('data', {}).get('BUY_BOX'),
                'estimated_sales_velocity': data.get('products', [{}])[0].get('stats', {}).get('avg180', {}).get('salesRank'), # Example: 180-day average sales rank
                'competitive_sellers': self._get_competitive_sellers_from_keepa_buybox(data.get('products', [{}])[0].get('data', {}).get('BUY_BOX')) # Extract competitive sellers
            }
            return keepa_data

        except requests.exceptions.RequestException as e:
            click.echo(f"    Error during Keepa API call: {e}")
            return {}
        # --- END KEEPA API INTEGRATION ---

    def _get_competitive_sellers_from_keepa_buybox(self, buy_box_data, price_threshold=0.15, lookback_months=3):
        # This is a simplified example. Real implementation would involve more robust parsing
        # of Keepa's Buy Box history data to identify unique sellers and their prices within
        # the specified price_threshold and lookback_months.
        # Keepa's Buy Box data is often a list of [timestamp, price, seller_id, ...] tuples.
        
        if not buy_box_data:
            return 0

        competitive_seller_count = 0
        unique_sellers = set()
        for i in range(0, len(buy_box_data), 3):
            if i + 2 < len(buy_box_data):
                seller_id = buy_box_data[i+2]
                if seller_id > 0:
                    unique_sellers.add(seller_id)
        
        return len(unique_sellers)

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
