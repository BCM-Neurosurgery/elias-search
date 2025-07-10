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
    dj.config["filepath_checksum_size_limit"] = -1
    os.environ['DJ_SUPPORT_FILEPATH_MANAGEMENT'] = 'TRUE'

    # always reset connection on each call
    return dj.conn(reset=True)

def parse_time(s):
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m-%d-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"time data {s!r} does not match expected formats")