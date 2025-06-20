from emu24.helper import connect
from datetime import datetime, timedelta
import datajoint as dj

def waterfall_query(data):
    # first connect to dj server
    connect()

    # we essentially want NSP chunks that we will format appropriately
    from emu24.schema import NSPChunks
    query = NSPChunks()
    query = timerange_query(data, query)

     
    

    data["selectedTasks"]
    data["selectedPatients"]
    data["fromDateTime"]
    data["toDateTime"]
    data["selectedDaysOfStay"]
    data["selectedTimesOfWeek"]

    pass

def timerange_query(data, query):
    # get our time range!!
    if data["fromDateTime"]:
        from_time = datetime.fromisoformat(data["fromDateTime"])
    else:
        from_time = datetime.MINYEAR

    if data["toDateTime"]:
        to_time = datetime.fromisoformat(data["toDateTime"])
    else:
        to_time = datetime.MAXYEAR
    
    # format for datajoint
    from_time = from_time.strftime("%Y-%m-%d %H:%M:%S.%f")
    to_time = to_time.strftime("%Y-%m-%d %H:%M:%S.%f")

    # now filter by time
    query = query & f'absolute_time >= "{from_time}"'
    query = query & f'absolute_time <= "{to_time}"'

    return query

def weektime_query(data, query):
    # just return query as is if we have the maximal set
    if data["selectedTimesOfWeek"] and len(data["selectedTimesOfWeek"]) == 7 * 24:
        return query
    
    # get current min and max time
    min_ts_str = (dj.U().aggr(query, n='min(absolute_time)').fetch1("n"))
    max_ts_str = (dj.U().aggr(query, n='max(absolute_time)').fetch1("n"))

    min_dt = datetime.strptime(min_ts_str, "%Y-%m-%d %H:%M:%S.%f")
    max_dt = datetime.strptime(max_ts_str, "%Y-%m-%d %H:%M:%S.%f")

    # use python week
    day_to_index = {
    "Sunday": 6, "Monday": 0, "Tuesday": 1, "Wednesday": 2,
    "Thursday": 3, "Friday": 4, "Saturday": 5
    }   
    # generate slot set for our time range
    if data["selectedTimesOfWeek"]:
        time_of_week = data["selectedTimesOfWeek"]
        slot_set = set((day_to_index[s["day"]], s["hour"]) for s in time_of_week)
    else:
        slot_set = set()
    
    # get valid datetime ranges
    current = min_dt.replace(minute=0, second=0, microsecond=0)
    valid_ranges = []

    while current <= max_dt:
        weekday = current.weekday()
        hour = current.hour

        if (weekday, hour) in slot_set:
            start = current
            end = current + timedelta(hours=1)
            valid_ranges.append((start, end))
        current += timedelta(hours=1)
    
    # convert valid ranges to readable filters for dj
    filters = []
    for start, end in valid_ranges:
        start_str = start.strftime("%Y-%m-%d %H:%M:%S.%f")
        end_str = end.strftime("%Y-%m-%d %H:%M:%S.%f")
        filters.append(f'absolute_time >= "{start_str}" AND absolute_time < "{end_str}"')
        
    # now build up query for all viable time ranges
    time_filtered_query = None
    for f in filters:
        subquery = query & f
        time_filtered_query = subquery if time_filtered_query is None else(time_filtered_query + subquery)

    return time_filtered_query

def patient_query(data, query):
    from emu24.schema import NSPChunks, Patient
    patient_filtered_query = NSPChunks() & '0=1'

    # get patient id and filter nsp rows
    for patient in data["selectedPatients"]:
        # get patient id and qu
        pt_id = (Patient () & f"emu_id = '{patient}'").fetch1('patient_id')
        subquery = query & f"patient_id = '{pt_id}'"
        patient_filtered_query = patient_filtered_query + subquery

    return patient_filtered_query