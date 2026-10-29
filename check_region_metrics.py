import pandas as pd

file_path = "data/region_year_metrics.csv"
df = pd.read_csv(file_path)

print("Columns:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head().to_string(index=False))

print("\nYear range:")
print(df["year"].min(), "-", df["year"].max())

print("\nForecast distribution:")
print(df["is_forecast"].value_counts(dropna=False))

print("\nMissing values:")
print(df.isnull().sum())
