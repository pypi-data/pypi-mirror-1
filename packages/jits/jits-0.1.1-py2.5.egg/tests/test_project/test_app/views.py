# Create your views here.

from django.http import HttpResponse

test_list = []

def index(request):
    return HttpResponse(str(test_list))
