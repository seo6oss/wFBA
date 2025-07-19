## Data Preparation Overview (Conceptual - VBA within Google Sheets)

This project assumes an initial data preparation step, conceptually handled by a sophisticated VBA macro embedded within Google Sheets. This macro is responsible for:

*   **Parsing & Consolidation:** Automating the ingestion and consolidation of large, raw supplier spreadsheets (e.g., CSV, Excel files) containing product information.
*   **Cleansing & Structuring:** Implementing logic to cleanse and standardise the data. This includes:
    *   Removing duplicate entries.
    *   Correcting formatting inconsistencies.
    *   Handling missing values.
    *   Structuring the data into a consistent, tabular format suitable for further processing by the Python modules.

This pre-processing step ensures that the Python-based automation receives a clean, reliable dataset, allowing it to focus on advanced API integrations and profitability analysis. The output of this conceptual VBA process is typically a CSV or Excel file, which then serves as the primary input for the Python components of this `wholesaleFBA` tool.
