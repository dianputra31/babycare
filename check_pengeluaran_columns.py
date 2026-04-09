#!/usr/bin/env python
"""Check pengeluaran table columns"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babycare_project.settings')
django.setup()

from django.db import connection

print("Checking database connection...")
cursor = connection.cursor()

# Try to get table columns
try:
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='pengeluaran' 
        ORDER BY column_name
    """)
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} columns in 'pengeluaran' table:")
    print("-" * 60)
    for row in results:
        print(f"{row[0]:<30} {row[1]}")
    print("-" * 60)
    
    # Check for inventory fields specifically
    inventory_fields = ['barang_id', 'jumlah_barang', 'harga_satuan_beli', 'supplier', 'no_faktur']
    print("\nChecking inventory fields:")
    cols = [r[0] for r in results]
    for field in inventory_fields:
        status = "✓ EXISTS" if field in cols else "✗ MISSING"
        print(f"  {field:<30} {status}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
