import os
import pandas as pd
from datetime import datetime, timedelta

BILLS_FOLDER_PATH = os.path.join("bill docs")

expected_files = ['file1', 'file2', 'file3', 'file4', 'file5', 'file6', 'file7', 'file8']

def get_contract_docs_data():
 
    contract_files = {}

    for contract_no in os.listdir(BILLS_FOLDER_PATH):
        contract_path = os.path.join(BILLS_FOLDER_PATH, contract_no, 'contract_docs')
        if os.path.isdir(contract_path):
            found_files = {os.path.splitext(file)[0]: file for file in os.listdir(contract_path)}
            contract_files[contract_no] = [
                os.path.join(contract_path, found_files.get(expected_file))
                if expected_file in found_files else None
                for expected_file in expected_files
            ]
    return contract_files


def generate_download_links(contract_no):
    contract_path = os.path.join(BILLS_FOLDER_PATH, contract_no, 'contract_docs')
    if os.path.isdir(contract_path):
        found_files = {os.path.splitext(file)[0]: file for file in os.listdir(contract_path)}
        return [
            os.path.join(contract_path, found_files.get(expected_file))
            if expected_file in found_files else None
            for expected_file in expected_files
        ]
    else:
        return [None] * len(expected_files)
    

def generate_sample_df():
    # Define the starting date
    start_date = datetime(2023, 1, 15)

    # Get the current date
    current_date = datetime.now()

    # Compute the number of months between start date and current date
    num_months = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month) + 1

    # Generate the list of months up to current month
    # Generate the list of months up to current month
    months = [(start_date + timedelta(days=30*i)).strftime('%b-%y') for i in range(num_months)]

    # Create lists for the data
    statuses = ['Green', 'Red', 'Yellow']
    remarks = ['Paid on time', 'Delayed payment', 'Partial payment']
    amounts_paid = ['$1000', '$800', '$1200']

    # Repeat the lists to cover the months
    full_months = months
    full_statuses = [statuses[i % 3] for i in range(num_months)]
    full_remarks = [remarks[i % 3] for i in range(num_months)]
    full_amounts_paid = [amounts_paid[i % 3] for i in range(num_months)]

    # Create DataFrame
    payment_df = pd.DataFrame({
        'Month': full_months,
        'Status': full_statuses,
        'Amount Paid': full_amounts_paid,
        'Remarks': full_remarks
    })
    payment_df = payment_df.sort_index(ascending=False)
    return payment_df