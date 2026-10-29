import csv
import re
from pathlib import Path

SQL_FILE = Path("vegetation_platform_new (14).sql")
OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "region_year_metrics.csv"

if not SQL_FILE.exists():
    raise FileNotFoundError(
        f"SQL file not found: {SQL_FILE.resolve()}"
    )

sql = SQL_FILE.read_text(encoding="utf-8", errors="replace")

# Extract INSERT statements for this table only.
pattern = re.compile(
    r"INSERT INTO\s+`region_year_metrics`\s*"
    r"\((.*?)\)\s*VALUES\s*(.*?);",
    re.IGNORECASE | re.DOTALL,
)

def parse_values(text):
    """Parse SQL values while respecting quoted strings."""
    rows = []
    i = 0
    n = len(text)

    while i < n:
        if text[i].isspace() or text[i] == ",":
            i += 1
            continue

        if text[i] != "(":
            i += 1
            continue

        i += 1
        values = []
        value = []
        quoted = False

        while i < n:
            char = text[i]

            if char == "'":
                if quoted and i + 1 < n and text[i + 1] == "'":
                    value.append("'")
                    i += 2
                    continue

                quoted = not quoted
                i += 1
                continue

            if char == "," and not quoted:
                values.append("".join(value).strip())
                value = []
                i += 1
                continue

            if char == ")" and not quoted:
                values.append("".join(value).strip())
                i += 1
                break

            value.append(char)
            i += 1

        rows.append(values)

    return rows


all_rows = []
headers = None

for match in pattern.finditer(sql):
    columns_text = match.group(1)
    values_text = match.group(2)

    headers = re.findall(r"`([^`]+)`", columns_text)
    all_rows.extend(parse_values(values_text))

if not headers or not all_rows:
    raise ValueError(
        "No data found for region_year_metrics. "
        "Check the SQL file and table name."
    )

# Convert SQL NULL values to empty CSV cells.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(headers)

    for row in all_rows:
        if len(row) != len(headers):
            raise ValueError(
                f"Row has {len(row)} values; expected {len(headers)}."
            )

        writer.writerow([
            "" if value.upper() == "NULL" else value
            for value in row
        ])

print("Extraction completed successfully!")
print(f"Table: region_year_metrics")
print(f"Rows extracted: {len(all_rows)}")
print(f"Columns: {len(headers)}")
print(f"CSV saved to: {OUTPUT_FILE.resolve()}")
