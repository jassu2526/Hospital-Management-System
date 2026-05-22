from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RoleRequiredMiddleware:
    """
    Enforces role-based access for URLs that declare `required_role` in view attributes.
    Views can set: view.required_role = 'ADMIN' | 'DOCTOR' | 'PATIENT' | 'ATTENDANT'
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        required_role = getattr(view_func.view_class if hasattr(view_func, 'view_class') else view_func, 'required_role', None)
        if required_role and request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if not profile or profile.role != required_role:
                messages.error(request, 'Access denied for your role.')
                return redirect(reverse('accounts:dashboard'))
        return None


class CurrentHospitalMiddleware:
    """
    Binds `request.current_hospital` for users associated with a specific hospital.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        request.current_hospital = None
        if user.is_authenticated:
            for rel in ('doctor', 'patient', 'attendant'):
                obj = getattr(user, rel, None)
                if obj and getattr(obj, 'hospital', None):
                    request.current_hospital = obj.hospital
                    break
        return self.get_response(request)

