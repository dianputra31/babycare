import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babycare_project.settings')
django.setup()

from core.models import User, Role, UserRole

# Create test user
username = 'admin'
password = 'admin'

try:
    # Check if user exists
    user = User.objects.filter(username=username).first()
    if user:
        print(f"User '{username}' already exists")
    else:
        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.full_name = 'Administrator'
        user.is_active = True
        user.save()
        print(f"✓ Created user: {username}")
        print(f"  Password: {password}")
        
    # Create owner role if not exists
    owner_role, created = Role.objects.get_or_create(
        nama_role='owner',
        defaults={'deskripsi': 'System Owner'}
    )
    if created:
        print(f"✓ Created role: owner")
        
    # Assign owner role to user
    user_role, created = UserRole.objects.get_or_create(
        user=user,
        role=owner_role
    )
    if created:
        print(f"✓ Assigned role 'owner' to user '{username}'")
    else:
        print(f"  User '{username}' already has role 'owner'")
        
    print("\n✓ Setup complete!")
    print(f"  Login with: {username} / {password}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
