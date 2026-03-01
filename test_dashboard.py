#!/usr/bin/env python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babycare_project.settings')

import django
django.setup()

from django.test import RequestFactory
from core.views import DashboardView
from django.contrib.auth import get_user_model 
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

User = get_user_model()

factory = RequestFactory()
request = factory.get('/dashboard/')

# Add session/auth middleware
SessionMiddleware(lambda x: None).process_request(request)
AuthenticationMiddleware(lambda x: None).process_request(request)

try:
    view = DashboardView.as_view()
    response = view(request)
    print(f"Status: {response.status_code}")
    print(f"Response type: {type(response).__name__}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
