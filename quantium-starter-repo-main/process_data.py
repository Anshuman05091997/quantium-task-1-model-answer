import pandas as pd

# Load files
df1 = pd.read_csv("data/daily_sales_data_0.csv")
df2 = pd.read_csv("data/daily_sales_data_1.csv")
df3 = pd.read_csv("data/daily_sales_data_2.csv")

# Combine all
df = pd.concat([df1, df2, df3])

# Keep only Pink Morsels
df = df[df["product"].str.lower() == "pink morsel"]

# Clean price (remove $ sign)
df["price"] = df["price"].replace('[\$,]', '', regex=True).astype(float)

# Create Sales column
df["Sales"] = df["price"] * df["quantity"]

# Keep only needed columns
df = df[["Sales", "date", "region"]]

# Rename columns
df.columns = ["Sales", "Date", "Region"]

# Save final file
df.to_csv("formatted_sales_data.csv", index=False)

print("DONE — formatted_sales_data.csv created!")
