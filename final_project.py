# Import libraries needed for API requests, CSV files, JSON files, and file checking
import requests
import csv
import os
import json


# API URL from the U.S. Treasury Fiscal Data API
url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance"

# File names used in this project
csv_filename = "operating_cash_balance.csv"
json_filename = "results.json"


# Get data from the JSON API
response = requests.get(url)
data = response.json()

# The actual records are stored inside the "data" key
items = data["data"]


#These are the columns that will be saved in the CSV file
fieldnames = [
    "record_date",
    "account_type",
    "open_today_bal",
    "close_today_bal",
    "record_fiscal_year"
]


# A set to keep track of rows that are already in the CSV file
# prevents duplicate rows
existing_rows = set()

if os.path.exists(csv_filename):
    with open(csv_filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row_id = (row["record_date"], row["account_type"])
            existing_rows.add(row_id)


# Opening the CSV file in append mode
# Append mode
new_rows = 0

with open(csv_filename, "a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    # If the file is empty, write the header row first
    if os.path.getsize(csv_filename) == 0:
        writer.writeheader()

    # Looping through the API data and adding only new rows to the CSV file
    for item in items:
        row_id = (item["record_date"], item["account_type"])

        if row_id not in existing_rows:
            writer.writerow({
                "record_date": item["record_date"],
                "account_type": item["account_type"],
                "open_today_bal": item["open_today_bal"],
                "close_today_bal": item["close_today_bal"],
                "record_fiscal_year": item["record_fiscal_year"]
            })

            new_rows += 1


print(f"Added {new_rows} new rows to the CSV file.")


# Reading all rows from the updated CSV file
rows = []

with open(csv_filename, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        rows.append(row)


# Converting closing balance values from strings into numbers
balances = []

for row in rows:
    try:
        balance = float(row["close_today_bal"])
        balances.append(balance)
    except:
        # If a row has missing or invalid data, skip it
        continue


# Performing basic analysis on the closing balances
max_balance = max(balances)
min_balance = min(balances)
average_balance = sum(balances) / len(balances)


# Finding the most recent record
latest_row = max(rows, key=lambda x: x["record_date"])
latest_date = latest_row["record_date"]
latest_balance = float(latest_row["close_today_bal"])


# Storing the results in a dictionary
results = {
    "total_records": len(rows),
    "max_balance": max_balance,
    "min_balance": min_balance,
    "average_balance": average_balance,
    "latest_date": latest_date,
    "latest_balance": latest_balance
}


# Saving the results dictionary to a JSON file
with open(json_filename, "w") as file:
    json.dump(results, file, indent=4)


print("Analysis complete.")
print("Results saved to results.json.")