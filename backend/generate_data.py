"""Generate synthetic transaction data for testing."""
import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
import os

def generate_transactions(num_records=1000):
    data = []
    statuses = ["SUCCESS", "FAILED", "PENDING"]
    currencies = ["USD", "EUR", "GBP"]
    
    for _ in range(num_records):
        data.append({
            "transaction_id": str(uuid.uuid4()),
            "customer_id": f"CUST-{random.randint(1000, 9999)}",
            "amount": round(random.uniform(10.0, 5000.0), 2),
            "currency": random.choice(currencies),
            "transaction_date": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
            "status": random.choice(statuses)
        })
    
    df = pd.DataFrame(data)
    
    # Ensure directory exists
    os.makedirs("data", exist_ok=True)
    file_path = "data/transactions.csv"
    df.to_csv(file_path, index=False)
    print(f"Generated {num_records} records to {file_path}")

if __name__ == "__main__":
    generate_transactions()
