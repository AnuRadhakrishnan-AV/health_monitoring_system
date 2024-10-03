from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'

class IsHealthcareProvider(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'healthcare_provider'

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'patient'
