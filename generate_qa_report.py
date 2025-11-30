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
        "Feature": "Dashboard",
        "Test Scenario": "Verify Sales Overview Graph",
        "Expected Result": "Graph canvas visible",
        "Actual Result": "Canvas element found",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_003",
        "Feature": "Inventory",
        "Test Scenario": "Add new product 'Test Item'",
        "Expected Result": "Item appears in table",
        "Actual Result": "Item added and visible",
        "Status": "PASS",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_004",
        "Feature": "Sales Logic",
        "Test Scenario": "Sell 2 units of 'Test Item'",
        "Expected Result": "Sale completes successfully",
        "Actual Result": "Could not select item in dropdown (UI Automation Issue)",
        "Status": "FAIL",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_005",
        "Feature": "Data Integrity",
        "Test Scenario": "Verify Inventory Deduction",
        "Expected Result": "Quantity decreases by 2",
        "Actual Result": "Quantity remained unchanged (Sale failed)",
        "Status": "FAIL",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_006",
        "Feature": "Reporting",
        "Test Scenario": "Verify Sales Stats Update",
        "Expected Result": "Sales Today increases",
        "Actual Result": "Stats unchanged (Sale failed)",
        "Status": "FAIL",
        "Date Executed": date.today()
    },
    {
        "Test ID": "TC_007",
        "Feature": "Download",
        "Test Scenario": "Verify Export CSV Button",
        "Expected Result": "Button exists",
        "Actual Result": "Button found",
        "Status": "PASS",
        "Date Executed": date.today()
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Export to Excel
file_path = "Final_QA_Report.xlsx"
df.to_excel(file_path, index=False)

print(f"Report generated successfully: {file_path}")
