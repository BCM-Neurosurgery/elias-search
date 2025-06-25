from datetime import datetime, timedelta
import datajoint as dj
import os

def assemble_query(data):
    data["selectedTasks"]
    data["selectedPatients"]
    data["fromDateTime"]
    data["toDateTime"]
    data["selectedDaysOfStay"]
    data["selectedTimesOfWeek"]
    pass

def format_response(data):
    pass
    

def dj_conn():
    from emu24 import settings
    dj.config['database.user'] = os.environ["DJ_USER"]
    dj.config['database.password'] = os.environ["DJ_PASSWORD"]
    dj.config['database.host'] = os.environ["DJ_HOST"]
    dj.config['database.port'] = int(os.environ["DJ_PORT"])
    dj.config['safemode'] = settings.DJ_CONFIG_SAFEMODE
    dj.config['stores'] = settings.DJ_CONFIG_STORES
    os.environ['DJ_SUPPORT_FILEPATH_MANAGEMENT'] = 'TRUE'

    # always reset connection on each call
    return dj.conn(reset=True)