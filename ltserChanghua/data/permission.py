import secrets

from django.conf import settings
from rest_framework.permissions import BasePermission


class HasInternalApiKey(BasePermission):
    message = "Invalid or missing internal API key."

    def has_permission(self, request, view):
        expected_key = getattr(settings, "INTERNAL_API_KEY", None)
        provided_key = request.headers.get("X-Internal-API-Key")

        if not expected_key or not provided_key:
            return False

        return secrets.compare_digest(provided_key, expected_key)
