from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:MwVSPVkJnAXnZgGiNCHusbPvNPjfXudh@thomas.proxy.rlwy.net:31845/railway"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("✅ Connected successfully!")

        result = conn.execute(text("SELECT * FROM resume_url"))

        for row in result:
            print(row)

except Exception as e:
    print(f"❌ Error: {e}")