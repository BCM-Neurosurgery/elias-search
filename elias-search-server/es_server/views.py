from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.sessions.models import SessionMiddleware
from paramiko import SSHClient, AutoAddPolicy
import json
import JsonResponse

@csrf_exempt
def ssh_auth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())

    try:
        ssh.connect('localhost', username=username, password=password)
        ssh.close()
        request.session['ssh_authenticated'] = True
        request.session['username'] = username
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=401)

def auth_status(request):
    return JsonResponse({"authenticated": request.session.get("ssh_authenticated", False)})