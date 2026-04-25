from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'public/home.html')

def result_view(request):
    return render(request, 'public/result.html')