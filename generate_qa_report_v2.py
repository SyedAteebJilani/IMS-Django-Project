import pandas as pd
from datetime import date

# Test Results Data
data = [
    {
        "Test ID": "TC_001",
        "Feature": "Auth",
        "Test Scenario": "Verify user can log in",
        "Expected Result": "Redirect to Home Dashboard",
        "Actual Result": "Redirected successfully",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_002",
        "Feature": "Inventory",
        "Test Scenario": "Add new product 'Test Pen' (UI)",
        "Expected Result": "Item appears in table",
        "Actual Result": "Modal does not close (UI Bug)",
        "Status": "FAIL",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_003",
        "Feature": "Inventory",
        "Test Scenario": "Add new product 'Test Pen' (Shell)",
        "Expected Result": "Item added to DB",
        "Actual Result": "Item added successfully via Shell",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_004",
        "Feature": "Sales Logic",
        "Test Scenario": "Sell 10 units of 'Test Pen'",
        "Expected Result": "Sale completes, Stock reduces",
        "Actual Result": "Sale completed, Stock 100 -> 90",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_005",
        "Feature": "Data Integrity",
        "Test Scenario": "Verify Sale Total (PKR)",
        "Expected Result": "Total = 5000 (10 * 500)",
        "Actual Result": "Total = 5000",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_006",
        "Feature": "Reversal",
        "Test Scenario": "Refund Sale",
        "Expected Result": "Sale deleted, Stock restored",
        "Actual Result": "Sale deleted, Stock 90 -> 100",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_007",
        "Feature": "Reporting",
        "Test Scenario": "Export Daily Sales",
        "Expected Result": "CSV Download",
        "Actual Result": "Button works",
        "Status": "PASS",
        "Date Executed": date.today()
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Export to Excel
file_path = "QA_Pass_Report.xlsx"
df.to_excel(file_path, index=False)

print(f"Report generated successfully: {file_path}")
