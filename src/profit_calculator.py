import click
import pandas as pd

class ProfitCalculator:
    def calculate_profit(self, buy_box_price, fba_fee, referral_fee_percentage, supplier_buy_price, vat_rate=0.20):
        # Profit = (Buy Box Price - (Amazon Fulfilment Cost + Amazon Referral Fee + VAT)) - Supplier Buy Price
        referral_fee_amount = buy_box_price * referral_fee_percentage
        vat_amount = (buy_box_price - supplier_buy_price - fba_fee - referral_fee_amount) * vat_rate
        total_amazon_fees = fba_fee + referral_fee_amount + vat_amount
        profit = buy_box_price - total_amazon_fees - supplier_buy_price
        return round(profit, 2)

    def calculate_recommended_units(self, estimated_monthly_sales, number_of_sellers, buy_box_price, seller_price_threshold=0.15):
        # Recommended Units = Monthly Sales (from Jungle Scout) / Number of sellers within 15% of Buy Box Price
        # For simplicity, we'll assume sellers within 15% of Buy Box Price are considered competitive
        competitive_sellers = number_of_sellers # In a real scenario, this would be filtered based on price
        if competitive_sellers == 0:
            return estimated_monthly_sales # If no competitive sellers, recommend all sales
        
        recommended_units = estimated_monthly_sales / competitive_sellers
        return round(recommended_units)
