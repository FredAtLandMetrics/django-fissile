import requests

from django.urls import path
from django.http import JsonResponse
from django.conf import settings
from django.test import Client


class func(object):

    def __init__(self, route_url_def, name, method='POST'):
        self.route_url_def = route_url_def
        self.name = name
        self.method = method

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            if settings.FISSILE_EXEC_MODE == 'frontend':
                return self._request_from_backend(*args, **kwargs)
            return f(*args, **kwargs)
        return wrapped_f

    def to_path(self):
        return path(self.route_url_def, self.as_view(), self.name)

    def as_view(self):
        def view_func(request):
            args = self._request_args(request)
            kwargs = self._request_kwargs(request)
            return JsonResponse(self(*args, **kwargs))
        return view_func

    def _request_args(self, request):
        return self._request_var('args')

    def _request_kwargs(self, request):
        return self._request_var('kwargs')

    def _request_var(self, request, varname):
        if self.method == 'POST':
            return request.POST.get(varname, None)
        if self.method == 'GET':
            return request.GET.get(varname, None)
        return None

    def _request_from_backend(self, *args, **kwargs):
        if settings.FISSILE_USE_TEST_CLIENT:
            c = Client()
            response = c.post()
