from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import Group
from django.conf import settings


class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self.process_request(request, response)

    def process_request(self, request, response):
        if not request.user.is_authenticated and not self._is_exempt(request):
            # Redirect to the login page if not authenticated
            return redirect(reverse('login'))

        return response

    def _is_exempt(self, request):
        exempt_urls = [
            # Add the URL patterns that should be exempted here
            reverse('public'),
            reverse('login'),
            reverse('register'),
            reverse('reset_password'),
            # reverse('password_reset_done'),
            # reverse('password_reset_confirm'),
            # reverse('password_reset_complete'),

        ]

        return request.path_info in exempt_urls

    def _redirection_not_allowed(self, request):
        not_allowed = [
            reverse('login'),
            reverse('register'),
        ]
        return request.path_info in not_allowed


class AdminCustomerRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path_info in [reverse('login'), reverse('register')]:
            if request.user.groups.filter(name='admin').exists():
                # Redirect admin users to accounts_home
                return redirect(reverse('accounts_home'))

            elif request.user.groups.filter(name='customer').exists():
                # Redirect customer users to user_page
                return redirect(reverse('user_page'))

        return self.get_response(request)


class GroupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_exempt(request):
            # Check if the user is in the "admin" group
            if request.user.groups.filter(name='admin').exists():
                return self.handle_admin_request(request)

            # Check if the user is in the "customer" group
            elif request.user.groups.filter(name='customer').exists():
                return self.handle_customer_request(request)

        response = self.get_response(request)
        return response

    def handle_admin_request(self, request):
        # Prevent admin users from accessing user_page
        if request.path_info.startswith(reverse('user_page')):
            return HttpResponseRedirect(reverse('accounts_home'))

        # Redirect admin users to the admin dashboard
        # this below condition will never process since every request will start with ' ' anyways. SO , you can remove it.
        if not request.path_info.startswith(reverse('accounts_home')):
            return HttpResponseRedirect(reverse('accounts_home'))

        return self.get_response(request)

    def handle_customer_request(self, request):
        # Redirect customer users to the customer dashboard
        # only user_page/... can be accessed, any url not starting with user_page/ won't work.
        if not request.path_info.startswith(reverse('user_page')):
            if request.path_info.startswith(settings.MEDIA_URL):
                return self.get_response(request)
            else:
                print("Not starting with user_page")
                return HttpResponseRedirect(reverse('user_page'))
        return self.get_response(request)

    def _is_exempt(self, request):
        exempt_urls = [
            reverse('login'),
            reverse('register'),
            reverse('logout'),  # Exempt logout URL from redirection
        ]

        for url in exempt_urls:
            if request.path_info.startswith(url):
                return True

        return False
