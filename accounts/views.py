from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# Create your views here.
def login_view(request):
    print("view hit")
    if request.method == 'POST':
        print("POST RECEIVED")
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            role = user.role.lower() if user.role else ''
            print("ROLE:", role)
            if role == 'admin':
                 return redirect('admin_dashboard')
            elif role == 'teacher':
                 return redirect('teacher_dashboard')
            elif role == 'data_entry':
                 return redirect('data_entry_dashboard')
            

        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})

    return render(request, 'accounts/login.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')