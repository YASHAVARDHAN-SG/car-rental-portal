from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    # return HttpResponse("This is Car Module")
    return render(request, 'index.html')