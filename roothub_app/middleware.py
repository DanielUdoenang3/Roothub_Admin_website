# from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

class Custom404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 404:
            return render(request, '404_error.html', status=404)
        return response
    
# Class LoadingMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         # Add your condition to show the loading page
#         if 'loading' in request.GET:
#             return render(request, 'loading.html')
#         return None