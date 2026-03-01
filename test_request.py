import os
import sys
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babycare_project.settings')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from core.views import PasienListView
from core.models import User

# Create a request
factory = RequestFactory()
request = factory.get('/pasien/')

# Mock authenticated user
try:
    user = User.objects.first()
    if not user:
        print("WARNING: No users in database, using AnonymousUser")
        request.user = AnonymousUser()
    else:
        request.user = user
        print(f"Using user: {user.username}")
except Exception as e:
    print(f"Error getting user: {e}")
    request.user = AnonymousUser()

# Try to get response
try:
    view = PasienListView.as_view()
    response = view(request)
    print(f"SUCCESS! Status: {response.status_code}")
    print(f"Content length: {len(response.content) if hasattr(response, 'content') else 'N/A'}")
except Exception as e:
    print("=" * 80)
    print("ERROR OCCURRED:")
    print("=" * 80)
    print(traceback.format_exc())
    print("=" * 80)
    sys.exit(1)
