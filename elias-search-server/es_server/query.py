from emu24.helper import connect
from datetime import datetime, timedelta
import datajoint as dj
import copy

class QueryBuilder:
    def __init__(self, data):
        self.data = data
        # connect to db and get all data
        connect()
        from emu24.schema import NSPChunks, Patient, Admission, TaskIDComments, StitchedChunks
        self.all_nsp = NSPChunks()
        self.query = NSPChunks()
        self.all_patients = Patient()
        self.all_admissions  = Admission()
        self.all_taskid_comments = TaskIDComments()
        self.all_stitched = StitchedChunks()
    
    def waterfall_query(self):
        # first connect to dj server
        # data["selectedTasks"]
        # data["selectedPatients"]
        # data["fromDateTime"]
        # data["toDateTime"]
        # data["selectedDaysOfStay"]
        # data["selectedTimesOfWeek"]
        pass
    
    def _timerange_query(self):
        # get our time range!!
        if self.data["fromDateTime"]:
            from_time = datetime.fromisoformat(self.data["fromDateTime"])
        else:
            from_time = datetime.MINYEAR

        if self.data["toDateTime"]:
            to_time = datetime.fromisoformat(self.data["toDateTime"])
        else:
            to_time = datetime.MAXYEAR
        
        # format for datajoint
        from_time = from_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        to_time = to_time.strftime("%Y-%m-%d %H:%M:%S.%f")

        # now filter by time
        self.query = self.query & f'absolute_time >= "{from_time}"'
        self.query = self.query & f'absolute_time <= "{to_time}"'
        return self.query

    def _patient_query(self):
        from emu24.schema import Patient
        patient_filtered_query = self.all_nsp & '0=1'
        # get patient id and filter nsp rows
        for patient in self.data["selectedPatients"]:
            # get patient id and qu
            pt_id = (self.all_patients & f"emu_id = '{patient}'").fetch1('patient_id')
            subquery = self.query & f"patient_id = '{pt_id}'"
            patient_filtered_query = patient_filtered_query + subquery

        self.query = patient_filtered_query
        return self.query
    
    def _task_query(self):
        task_filtered_query = self.all_nsp & '0=1'
        for task in self.data["selectedTasms"]:
            # get patient id and qu
            pt_id = (Patient () & f"emu_id = '{patient}'").fetch1('patient_id')
            subquery = self.query & f"patient_id = '{pt_id}'"
            patient_filtered_query = patient_filtered_query + subquery

        self.query = task_filtered_query
        return self.query

    def _stay_day_query(self):
        pass

    def _weektime_query(self):
         # just return query as is if we have the maximal set
        if self.data["selectedTimesOfWeek"] and len(self.data["selectedTimesOfWeek"]) == 7 * 24:
            return self.query
    
        # get current min and max time
        min_ts_str = (dj.U().aggr(self.query, n='min(absolute_time)').fetch1("n"))
        max_ts_str = (dj.U().aggr(self.query, n='max(absolute_time)').fetch1("n"))

        min_dt = datetime.strptime(min_ts_str, "%Y-%m-%d %H:%M:%S.%f")
        max_dt = datetime.strptime(max_ts_str, "%Y-%m-%d %H:%M:%S.%f")

        # use python week
        day_to_index = {
        "Sunday": 6, "Monday": 0, "Tuesday": 1, "Wednesday": 2,
        "Thursday": 3, "Friday": 4, "Saturday": 5
        }   
        # generate slot set for our time range
        if self.data["selectedTimesOfWeek"]:
            time_of_week = self.data["selectedTimesOfWeek"]
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
            subquery = self.query & f
            time_filtered_query = subquery if time_filtered_query is None else(time_filtered_query + subquery)

        self.query = time_filtered_query
        return self.query