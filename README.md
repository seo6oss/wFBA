# wholesaleFBA: Automated Amazon FBA Wholesale Optimiser

This powerful command-line tool automates and optimises the Amazon FBA (Fulfilled by Amazon) wholesale business process. It intelligently parses and cleanses supplier data, enriches it with real-time market insights from Amazon, Keepa, and Jungle Scout APIs, and performs advanced profitability calculations for informed purchasing decisions.

## Key Features

### 1. Supplier Data Ingestion & Cleansing (VBA within Google Sheets)

This crucial initial step is handled by a sophisticated **VBA macro** embedded within Google Sheets. It's designed to automate the parsing, consolidation, cleansing, and structuring of massive supplier lists (100,000+ entries). This ensures the raw data is transformed into a clean, standardised format, ready for subsequent automated processing.

*   **Input:** Raw supplier data files (e.g., CSV, Excel files).
*   **Output (for Python):** A meticulously cleansed and structured dataset, typically exported as a CSV or Excel file, serving as the primary input for the Python-based modules.

### 2. Product Data Enrichment (Python with Advanced API Integrations)

Leveraging Python, this module integrates with leading e-commerce data providers to enrich product information:

*   **Amazon API Integration:** Connects with the Amazon MWS API to pull real-time product details, current prices, sales ranks, and ASINs (Amazon Standard Identification Numbers) for accurate matching.
*   **Keepa API Integration:** Retrieves comprehensive historical data from the Keepa API, including historical price fluctuations, sales rank trends, Buy Box statistics, and estimated sales velocity. Crucially, it also exports relevant fees associated with each product, vital for accurate profitability assessments.
*   **Jungle Scout API Integration:** Obtains critical market intelligence from the Jungle Scout API, such as estimated monthly sales volumes, competitive landscape analysis, and product opportunity scores, aiding in identifying profitable niches.
*   **Validation Tools (Integration):** The system is designed to work in conjunction with external validation tools like `DS Quick View`, `RevSeller`, and `AMZScout`, implying their integration or a workflow where their data is used to cross-verify API-pulled information.

### 3. Profitability Analysis & Optimal Unit Calculation (Python Module)

This core Python module implements powerful calculations to guide purchasing decisions:

*   **Profit Calculation:** Calculates the precise profit for each product using the formula:
    `Profit = (Buy Box Price - (Amazon Fulfilment Cost + Amazon Referral Fee + VAT)) - Supplier Buy Price`
*   **Optimal Unit Calculation:** Determines the optimal number of units to purchase, based on market demand and competition, using the formula:
    `Recommended Units = Monthly Sales (from Jungle Scout) / Number of sellers within 15% of Buy Box Price`

### 4. Image-based Verification (Python with Amazon SP-API)

This module leverages the Amazon Selling Partner API (SP-API) to retrieve product images directly from Amazon listings. This provides a critical verification step to reduce false positives in product matching. By comparing supplier-provided images with Amazon's official product images, the system ensures accurate product association, especially when traditional identifiers (like barcodes) might lead to ambiguous matches.

### 5. Comprehensive Reporting

The final stage generates a detailed and actionable report (e.g., CSV or Excel). This report consolidates all the cleansed supplier data, enriched market insights, calculated profits, recommended purchase quantities, and any flagged discrepancies, serving as an indispensable tool for strategic purchasing decisions.

## Tech Stack

*   **Primary Automation Language:** Python 3.8+ (for API integrations, calculations, image processing, CLI)
*   **Data Preparation:** VBA (within Google Sheets - an external pre-processing step)
*   **Python Libraries:**
    *   `pandas`: For efficient data manipulation, reading the VBA-processed supplier data (CSV or Excel), and generating comprehensive reports.
    *   `requests`: For making HTTP requests to Amazon, Keepa, and Jungle Scout APIs.
    *   `click`: For building a user-friendly command-line interface (CLI).
*   **APIs/Tools:** Amazon MWS API, Keepa API, Jungle Scout API, DS Quick View, RevSeller, AMZScout.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/seo6oss/wholesaleFBA.git
    cd wholesaleFBA
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the root of the project and add your API keys:

    ```
    AMAZON_API_KEY=your_amazon_api_key
    KEEPA_API_KEY=your_keepa_api_key
    JUNGLE_SCOUT_API_KEY=your_junglescout_api_key
    ```

## Usage

1.  **Prepare Supplier Data:** Ensure your raw supplier data has been processed by the VBA macro in Google Sheets and exported as a clean CSV or Excel file (e.g., `data/cleansed_supplier_data.csv`).

2.  **Run the processing tool:**

    ```bash
    python src/main.py process_supplier_data --spreadsheet_name "Your Spreadsheet Name" --worksheet_name "Your Worksheet Name"
    ```

    *(Note: Replace "Your Spreadsheet Name" and "Your Worksheet Name" with your actual Google Sheet details.)*

## Project Structure

```
wholesaleFBA/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api_integrator.py
│   ├── profit_calculator.py
│   ├── google_sheets_integrator.py
│   ├── data_prep_overview.md
├── vba/
│   └── conceptual_macro.vba
├── .env
├── requirements.txt
├── README.md
```

## Workflow Overview

Here's a step-by-step breakdown of how the `wholesaleFBA` tool integrates into your overall workflow:

1.  **Supplier Data Preparation (VBA in Google Sheets):**
    *   Raw supplier lists are processed by a VBA macro (conceptual code provided in `vba/conceptual_macro.vba`) to consolidate, cleanse, and structure the data within a Google Sheet.
    *   **Conceptual Email Integration:** (Due to signed NDA, actual code cannot be provided. This is a conceptual outline.) An automated process would ideally grab supplier files from a dedicated email inbox and pass them to the Google Sheets API for initial processing by the VBA macro.
    *   Output: A clean, structured Google Sheet ready for Python processing.

2.  **Python Processing - Data Enrichment & Analysis:**
    *   **Product Data Ingestion:** The Python script reads the cleansed supplier data directly from the Google Sheet using the Google Sheets API.
    *   **Amazon API Integration:** Matches barcodes to Amazon listings, pulling real-time prices, sales ranks, ASINs, and main product image URLs.
    *   **Keepa API Integration:** Retrieves historical price data, sales rank history, Buy Box statistics, and estimated sales velocity. It also performs barcode-to-ASIN conversion.
    *   **Jungle Scout API Integration:** Obtains estimated monthly sales, competitive landscape analysis, and product opportunity scores.
    *   **Data Enrichment to Google Sheet:** All enriched data from the APIs (including Amazon image URLs, sales ranks, buy box prices, FBA fees, referral fees, Keepa buy box history, Jungle Scout sales volume) is written back to the *same Google Sheet*.

3.  **VBA Macro - Final Calculations & Reporting (within Google Sheets):**
    *   The VBA macro (conceptual code provided in `vba/conceptual_macro.vba`) within the Google Sheet then takes this enriched data to:
        *   Perform **Image Verification**: Compares supplier-provided image URLs with Amazon image URLs to confirm product matches.
        *   Execute **Profit Calculation**: `Profit = (Buy Box Price - (Amazon Fulfilment Cost + Amazon Referral Fee + VAT)) - Supplier Buy Price`.
        *   Execute **Optimal Unit Calculation**: `Recommended Units = Monthly Sales (from Jungle Scout) / Number of sellers within 15% of Buy Box Price`.
        *   Calculate **Profit Percentage** and **Return on Investment (ROI)**.
        *   Apply **Conditional Formatting**: Colors rows based on profitability (e.g., red for unprofitable, green for highly profitable).

## Project Summary & Conclusion

This `wholesaleFBA` project stands as a testament to the power of automation and data-driven decision-making in the e-commerce wholesale domain. It encapsulates a sophisticated workflow, from initial data preparation and cleansing (leveraging VBA for efficiency) to advanced market analysis and profitability forecasting through seamless API integrations.

The modular design and clear separation of concerns (data preparation, API integration, calculation, reporting) demonstrate a robust and scalable approach to complex business challenges. While the API keys and specific operational details are omitted due to their sensitive and proprietary nature, the underlying architecture and implementations are designed to be fully functional and adaptable to real-world scenarios.

This tool empowers FBA wholesalers to:

*   **Automate tedious manual processes**, saving significant time and resources.
*   **Gain deep, actionable insights** into product profitability and market demand.
*   **Reduce purchasing risks** through intelligent data validation and image-based matching.
*   **Optimise inventory decisions** for maximum return on investment.

It represents a comprehensive solution for achieving operational excellence and competitive advantage in the dynamic Amazon FBA landscape.
