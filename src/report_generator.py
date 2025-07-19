import click
import pandas as pd
import os

class ReportGenerator:
    def generate_report(self, data_frame, output_file='wholesale_report.csv'):
        click.echo(f"Generating comprehensive report to {output_file}...")
        data_frame.to_csv(output_file, index=False)
        click.echo("Report generation complete.")

    def generate_discrepancy_report(self, data_frame, output_file='discrepancy_report.csv'):
        click.echo(f"Generating discrepancy report to {output_file}...")
        # In a real scenario, this would filter for rows with discrepancies
        discrepancies = data_frame[data_frame['is_discrepancy'] == True] # Assuming a 'is_discrepancy' column
        discrepancies.to_csv(output_file, index=False)
        click.echo("Discrepancy report generation complete.")
