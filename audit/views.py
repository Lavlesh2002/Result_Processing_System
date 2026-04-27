
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AuditLog
# Create your views here.
@login_required
def audit_logs(request):
    if request.user.role != 'admin':
        return redirect('login')

    logs = AuditLog.objects.all().order_by('-timestamp')

    return render(request, 'audit/logs.html', {
        'logs': logs
    })