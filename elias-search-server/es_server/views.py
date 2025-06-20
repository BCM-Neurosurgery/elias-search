from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from paramiko import SSHClient, AutoAddPolicy
import json

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
        ssh.connect('elias.bcms.bcm.edu', username=username, password=password)
        ssh.close()
        request.session['ssh_authenticated'] = True
        request.session['username'] = username
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=401)

def auth_status(request):
    return JsonResponse({"authenticated": request.session.get("ssh_authenticated", False)})

@csrf_exempt
def query_db(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    data = json.loads(request.body)
    return(JsonResponse(data))

def get_patients(request):
    patient_list = [
        "YEX",
        "YEY",
        "YFA",
        "YFF",
        "YFK",
        "YFM",
        "YFP"
    ]
    return JsonResponse({'patients': patient_list})