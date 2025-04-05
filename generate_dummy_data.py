# generate_dummy_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

# Create output directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Settings
num_records = 5000
invoice_ids = [f"INV{1000 + i}" for i in range(num_records)]
vendor_ids = [f"VEND{np.random.randint(1, 50)}" for _ in range(num_records)]

base_date = datetime.today()
invoice_dates = [base_date - timedelta(days=np.random.randint(0, 180)) for _ in range(num_records)]
payment_due_dates = [d + timedelta(days=np.random.randint(10, 30)) for d in invoice_dates]

payment_methods = np.random.choice(["Bank Transfer", "Cheque", "UPI", "Cash"], size=num_records)
departments = np.random.choice(["HR", "Finance", "Operations", "IT", "Marketing"], size=num_records)
amounts = np.random.randint(500, 100000, size=num_records)

# Realistic delay generation
def realistic_delay(method, amount):
    if method == "Cash":
        return np.random.randint(-3, 2)  # Fast or on-time
    elif method == "UPI":
        return np.random.randint(-1, 3)
    elif method == "Bank Transfer":
        return np.random.randint(0, 6)
    elif method == "Cheque":
        base_delay = np.random.randint(3, 12)
        if amount > 50000:
            base_delay += np.random.randint(3, 7)  # Big cheques take longer
        return base_delay
    return 0

delay_days = [realistic_delay(method, amt) for method, amt in zip(payment_methods, amounts)]
payment_dates = [due + timedelta(days=delay) for due, delay in zip(payment_due_dates, delay_days)]

df = pd.DataFrame({
    "Invoice_ID": invoice_ids,
    "Vendor_ID": vendor_ids,
    "Invoice_Date": invoice_dates,
    "Payment_Due_Date": payment_due_dates,
    "Payment_Date": payment_dates,
    "Amount": amounts,
    "Payment_Method": payment_methods,
    "Department": departments
})

df.to_csv("data/vendor_payments.csv", index=False)
print("✅ Realistic data generated in 'data/vendor_payments.csv'")
