
import os
import sys
import psycopg2

# Add project root to path for imports to work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings

def verify_db():
    print("🔍 Verifying Database Setup...")
    
    try:
        # 1. Test Connection
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        print("✅ Connection Successful")
        
        cur = conn.cursor()
        
        # 2. Check Tables
        expected_tables = ['customers', 'products', 'orders', 'order_items', 'page_views']
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [r[0] for r in cur.fetchall()]
        
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if not missing_tables:
            print(f"✅ All {len(expected_tables)} tables exist")
        else:
            print(f"❌ Missing tables: {missing_tables}")
            return False

        # 3. Check Row Counts
        print("\n📊 Data Statistics:")
        total_rows = 0
        for table in expected_tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  - {table}: {count:,} rows")
            total_rows += count
            
        if total_rows > 0:
            print(f"✅ Database populated with {total_rows:,} total records")
        else:
            print("⚠️ Database appears empty (did seed script run?)")

        # 4. Sample Query
        print("\n🔬 Running Sample Query (Revenue by Status):")
        cur.execute("""
            SELECT status, COUNT(*) as count, SUM(total_amount) as revenue
            FROM orders
            GROUP BY status
            ORDER BY revenue DESC
        """)
        results = cur.fetchall()
        for row in results:
            print(f"  - {row[0]}: {row[1]:,} orders, ${row[2]:,.2f}")
            
        print("\n✅ Verification Complete!")
        return True

    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    success = verify_db()
    sys.exit(0 if success else 1)
