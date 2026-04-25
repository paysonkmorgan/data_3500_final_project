import requests
import csv
import os

url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance"
filename = "operating_cash_balance.csv"

response = requests.get(url)
print(response.status_code)

data = response.json()
items = data["data"]

existing_rows = set()

if os.path.exists(filename):
    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_rows.add((row["record_date"], row["account_type"]))

fieldnames = [
    "record_date",
    "account_type",
    "open_today_bal",
    "close_today_bal",
    "record_fiscal_year"
]

new_rows = 0

with open(filename, "a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    if os.path.getsize(filename) == 0:
        writer.writeheader()

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

print(f"Added {new_rows} new rows.")

import json

rows = []

with open(filename, "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        rows.append(row)

print(f"Total rows loaded: {len(rows)}")

balances = []

for row in rows:
    try:
        balance = float(row["close_today_bal"])
        balances.append(balance)
    except:
        continue

max_balance = max(balances)
min_balance = min(balances)
avg_balance = sum(balances) / len(balances)

latest_row = max(rows, key=lambda x: x["record_date"])

latest_date = latest_row["record_date"]
latest_balance = float(latest_row["close_today_bal"])

results = {
    "total_records": len(rows),
    "max_balance": max_balance,
    "min_balance": min_balance,
    "average_balance": avg_balance,
    "latest_date": latest_date,
    "latest_balance": latest_balance
}

with open("results.json", "w") as file:
    json.dump(results, file, indent=4)

print("Results saved to results.json")