from django.http import HttpResponse
from django.http.response import JsonResponse

def index(request):
    return HttpResponse("Hello, yacine. You're at the polls index.")