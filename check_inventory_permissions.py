#!/usr/bin/env python
"""Check inventory permissions in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babycare_project.settings')
django.setup()

from core.models import Permission

print("Checking Inventory Permissions:")
print("-" * 60)

inventory_perms = Permission.objects.filter(module='Inventory').order_by('action')
if inventory_perms.exists():
    print(f"Found {inventory_perms.count()} inventory permissions:\n")
    for perm in inventory_perms:
        print(f"  ✓ {perm.code:<35} | {perm.action}")
else:
    print("  ✗ No inventory permissions found!")
    print("\nAll modules in database:")
    modules = Permission.objects.values_list('module', flat=True).distinct().order_by('module')
    for mod in modules:
        count = Permission.objects.filter(module=mod).count()
        print(f"  - {mod}: {count} permissions")

print("-" * 60)
