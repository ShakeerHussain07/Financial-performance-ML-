import requests
import pandas as pd
import mysql.connector

BASE_URL = "https://bluemutualfund.in/server/api/company.php"
API_KEY = "ghfkffu6378382826hhdjgk"

company_id = input(
    "Enter company ID (example: TCS, INFY, HDFCBANK): "
).strip().upper()

params = {
    "id": company_id,
    "api_key": API_KEY
    
}

print("Fetching financial data for:", company_id)

response = requests.get(BASE_URL, params=params)

if response.status_code != 200:
    print("API request failed")
    exit()

data = response.json()

profit_loss = data["data"]["profitandloss"]
df = pd.DataFrame(profit_loss)

df["sales_growth_pct"] = df["sales"].pct_change() * 100
df["profit_growth_pct"] = df["net_profit"].pct_change() * 100

avg_sales_growth = df["sales_growth_pct"].tail(5).mean()
avg_profit_growth = df["profit_growth_pct"].tail(5).mean()

print("Average Sales Growth (last 5 years):", round(avg_sales_growth, 2))
print("Average Profit Growth (last 5 years):", round(avg_profit_growth, 2))

pros = []
cons = []

if avg_sales_growth > 10:
    pros.append("Good sales growth over the last five years")
else:
    cons.append("Poor sales growth over the last five years")

if avg_profit_growth > 10:
    pros.append("Strong profit growth over the last five years")
else:
    cons.append("Weak profit growth over the last five years")

print("Pros:")
for p in pros:
    print("-", p)

print("Cons:")
for c in cons:
    print("-", c)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="system",
    database="ml_project"
)

cursor = conn.cursor()

insert_query = """
INSERT INTO ml_results
(company_id, avg_sales_growth, avg_profit_growth, pros, cons)
VALUES (%s, %s, %s, %s, %s)
"""

cursor.execute(
    insert_query,
    (
        company_id,
        round(avg_sales_growth, 2),
        round(avg_profit_growth, 2),
        ", ".join(pros),
        ", ".join(cons)
    )
)

conn.commit()
cursor.close()
conn.close()

print("Analysis saved successfully to the database")
