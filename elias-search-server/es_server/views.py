from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from paramiko import SSHClient, AutoAddPolicy
from datajoint.schemas import VirtualModule
import json
from .utils import dj_conn
from .query import QueryBuilder

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
    qb = QueryBuilder(data)
    qb.waterfall_query()
    qb.get_stitched_tasks_in_range()
    results = qb.format_query_results()
    return(JsonResponse(results))

def get_formdata(request):
    conn = dj_conn()
    schemas = VirtualModule(module_name='schemas', schema_name='emu24_stitch', connection=conn)
    query = schemas.Patient()
    patient_list = list(query.fetch('emu_id'))
    query = schemas.TaskIDComments()
    task_list = list(set(query.fetch('task_name')))
    return JsonResponse({'patients': patient_list, 'tasks': task_list})


