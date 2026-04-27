from database import run_query

columns, rows = run_query("""
    SELECT DISTINCT status, COUNT(*) as count 
    FROM application 
    GROUP BY status 
    ORDER BY count DESC
""")

if isinstance(rows, str):
    print("Error:", rows)
else:
    print("All Status Values:")
    for row in rows:
        print(f"  {row['status']} → {row['count']} records")