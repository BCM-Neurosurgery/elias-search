from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import login, logout
from paramiko import SSHClient, AutoAddPolicy
from datajoint.schemas import VirtualModule
import json
import datajoint as dj
from .utils import dj_conn, parse_time
#from .query import QueryBuilder
from .dj_query import QueryBuilder

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
        request.session.modified = True
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=401)

@csrf_exempt
def auth_logout(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    logout(request)
    request.session['ssh_authenticated'] = False
    request.session['username'] = ''
    return JsonResponse({'success': True})

def auth_status(request):
    # for dev purposes always be authenticated
    # return JsonResponse({"authenticated": True})
    return JsonResponse({"authenticated": request.session.get("ssh_authenticated", False)})

@csrf_exempt
def query_db(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    data = json.loads(request.body)
    session_id = data.get('session_id')

    if not session_id:
        return JsonResponse({'error': 'Missing session_id'}, status=400)
    
    qb = QueryBuilder(data, session_id=session_id)
    qb.waterfall_query()
    results = qb.format_query_results()
    return(JsonResponse(results))

def get_formdata(request):
    conn = dj_conn()
    schemas = VirtualModule(module_name='schemas', schema_name='emu24_stitch', connection=conn)
    pt_ids = schemas.Patient()
    patient_list = list(pt_ids.fetch('emu_id'))
    query = schemas.TaskIDComments()
    task_list = list(set(query.fetch('task_name')))
    max_days = 0
    # get total days per patient to get max days of stay
    pt_ids = pt_ids.fetch('patient_id')
    for pt_id in pt_ids:
        admission_data = schemas.Admission() & f"patient_id = '{pt_id}'"
        try:
            admission_date = admission_data.fetch1('admission_date')
            admission_date = parse_time(admission_date)
        except Exception as e:
            print(f"Error fetching admission date for patient {pt_id}: {e}")
            continue
        last_recording = (dj.U().aggr(schemas.NSPChunks() & f"patient_id = '{pt_id}'", n='max(absolute_time)').fetch1("n"))
        last_recording = parse_time(last_recording)
        days_of_stay = (last_recording - admission_date).days
        # assume any value above 30 is a mistake and do not consider this patient
        if days_of_stay > 30:
            days_of_stay = 0
        max_days = max(max_days, days_of_stay)
    return JsonResponse({'patients': patient_list, 'tasks': task_list, 'max_days': max_days})


