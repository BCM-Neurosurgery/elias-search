from .utils import dj_conn
from datetime import datetime, timedelta, MINYEAR, MAXYEAR
import datajoint as dj
from datajoint.schemas import VirtualModule
from pyNsXStitch.helpers import get_nsx_duration

SAMPLING_RATE = 30_000
class QueryBuilder:
    def __init__(self, data):
        self.data = data
        # connect to db and get all data
        conn = dj_conn()
        self.schemas = VirtualModule(module_name='schemas', schema_name='emu24_stitch', connection=conn)
        self.query = self.schemas.NSPChunks()
        self.stitched_query = self.schemas.StitchedChunks() & '0=1'
    
    def waterfall_query(self):
        # run all steps of query
        self._timerange_query()
        self._patient_query()
        self._task_query()
        # self._stay_day_query()
        # self._weektime_query()
        return self.query
    
    def get_stitched_tasks_in_range(self):
        # get patients and start chunks
        res = self.query.fetch('patient_id', 'chunk_id')

        # loop through chunks and get stitched chunks!!!
        for (pt_id, chunk_id) in res:
            subquery = self.schemas.StitchedChunks() & f"patient_id = '{pt_id}' AND start_chunk = '{chunk_id}'"
            self.stitched_query = self.stitched_query + subquery
        return self.stitched_query
    
    def format_query_results(self):
        # initialize result dictionary
        results = {
            'patient': [],
            'start_time': [],
            'duration_s': [],
            'end_time': [],
            'file': [],
            'filetypes': [],
            'nsp_id': [],
            'source': []
        }

        query_res = self.query.fetch('patient_id', 'nsp_id', 'absolute_time', 
                                     'file', 'nev_file', 'ns3_file', 'ns5_file')
        for (pt_id, nsp_id, absolute_time, file, nev_file, ns3_file, ns5_file) in query_res:
            patient_emu_id = (self.schemas.Patient() & f"patient_id = '{pt_id}'").fetch1('emu_id')
            results['patient'].append(patient_emu_id)
            results['start_time'].append(absolute_time)
            results['file'].append(file)
            filetypes = []
            if nev_file:
                filetypes.append('nev')
            if ns5_file:
                filetypes.append('ns5')
                duration = get_nsx_duration(ns5_file) / SAMPLING_RATE
                results['duration'].append(duration)
                end_time = datetime.strptime(absolute_time, "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=duration)
                results['end_time'].append(end_time.strftime("%Y-%m-%d %H:%M:%S.%f"))
            else:
                results['duration'].append('NULL')
                results['end_time'].append('NULL')
            if ns3_file:
                filetypes.append('ns3')
            results['filetypes'].append(",".join(filetypes))
            results["nsp_id"].append(nsp_id)
            results['source'].append('datalake')
        query_res = self.stitched_query.fetch('patient_id', 'nsp_id', 'start_chunk', 
                                              'start_tid', 'stop_chunk', 'stop_tid', 
                                              'nev_file', 'ns3_file', 'ns5_file')
        for (pt_id, nsp_id, start_chunk, start_tid, 
             stop_chunk, stop_tid, nev_file, ns3_file, ns5_file) in query_res:
            patient_emu_id = (self.schemas.Patient() & f"patient_id = '{pt_id}'").fetch1('emu_id')
            results['patient'].append(patient_emu_id)
            results['source'].append('stitched')
            results['nsp_id'].append(nsp_id)
            filetypes = []
            if nev_file:
                filetypes.append('nev')
                file = nev_file[:-5]
                results['file'].append(file)
            if ns5_file:
                filetypes.append('ns5')
            if ns3_file:
                filetypes.append('ns3')
            results['filetypes'].append(",".join(filetypes))
            chunk_start = (self.schemas.NSPChunks() & f"patient_id = '{pt_id}' AND chunk_id = '{start_chunk}'").fetch1('absolute_time')
            start_stamp = (self.schemas.StartComments() & f"patient_id = '{pt_id}' AND comment_id = '{start_tid}'").fetch1('timestamp')
            chunk_stop = (self.schemas.NSPChunks() & f"patient_id = '{pt_id}' AND chunk_id = '{stop_chunk}'").fetch1('absolute_time')
            stop_stamp = (self.schemas.StopComments() & f"patient_id = '{pt_id}' AND comment_id = '{stop_tid}'").fetch1('timestamp')
            start_ts = datetime.strptime(chunk_start, "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=start_stamp / SAMPLING_RATE)
            end_ts = datetime.strptime(chunk_stop, "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=stop_stamp / SAMPLING_RATE)
            duration = end_ts - start_ts
            results['start_time'].append(start_ts.strftime("%Y-%m-%d %H:%M:%S.%f"))
            results['duration_s'].append(duration.total_seconds())
            results['end_time'].append(end_ts.strftime("%Y-%m-%d %H:%M:%S.%f"))

        return results    
    
    def _timerange_query(self):
        # get our time range!!
        if self.data["fromDateTime"]:
            from_time = datetime.fromisoformat(self.data["fromDateTime"])
        else:
            from_time = datetime(MINYEAR, 1, 1)

        if self.data["toDateTime"]:
            to_time = datetime.fromisoformat(self.data["toDateTime"])
        else:
            to_time = datetime(MAXYEAR, 1, 1)
        
        # format for datajoint
        from_time = from_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        to_time = to_time.strftime("%Y-%m-%d %H:%M:%S.%f")

        # now filter by time
        self.query = self.query & f'absolute_time >= "{from_time}"'
        self.query = self.query & f'absolute_time <= "{to_time}"'
        return self.query

    def _patient_query(self):
        # get patient id and filter nsp rows
        pt_ids = []
        for patient in self.data["selectedPatients"]:
            # get patient id and qu
            pt_id = (self.schemas.Patient() & f"emu_id = '{patient}'").fetch1('patient_id')
            pt_ids.append(pt_id)
        filter = " OR ".join([f"patient_id = '{pt_id}'" for pt_id in pt_ids])
        self.query = self.query & filter
        return self.query
    
    def _task_query(self):
        # first filter task list depending on flags
        if self.data["allTasks"]:
            all_tasks = self.schemas.TaskIDComments()
            task_list = list(set(all_tasks.fetch('task_name')))
            self.data["selectedTasks"] = task_list
        if self.data["excludeStim"]:
            self.data["selectedTasks"] = [task for task in self.data["selectedTasks"] 
                                          if "pep" not in task.lower() and "AD" not in task]
            
        # return query as is if allTasks adn not excludeStim
        if self.data["allTasks"] and not self.data["excludeStim"]:
            return self.query
        
        filters = []
        for task in self.data["selectedTasks"]:
            # get patient id and emu_id - will iterate through them to get all chunks
            data = (self.schemas.TaskIDComments() & f"task_name = '{task}'").fetch('patient_id', 'emu_id')
            for (pt_id, emu_id) in data:
                # get start comment nsp id
                start_chunk_query = self.schemas.StartComments() & f"patient_id = '{pt_id}' AND emu_id = '{emu_id}'"
                start_chunk_id = start_chunk_query.fetch('chunk_id')[0]
                # get stop comment nsp id
                stop_chunk_query = self.schemas.StopComments() & f"patient_id = '{pt_id}' AND emu_id = '{emu_id}'"
                stop_chunk_id = stop_chunk_query.fetch('chunk_id')[0]
                # add all chunks
                for id_ in range(start_chunk_id, stop_chunk_id + 1):
                    subquery = f"(patient_id = '{pt_id}' AND chunk_id = '{id_}')"
                    filters.append(subquery)
        filter = " OR ".join(filters)
        self.query = self.query & filter
        return self.query

    def _stay_day_query(self):
        stay_filtered_query = self.schemas.NSPChunks() & '0=1'
        # get current patient ids
        pt_ids = list(set(self.query.fetch('patient_id')))
        for pt_id in pt_ids:
            # get admission start
            admission_start = self.schemas.Admission() & f"patient_id = '{pt_id}'"
            admission_start = datetime.strptime(admission_start, "%Y-%m-%d %H:%M:%S.%f").replace(hour=0, minute=0, second=0, microsecond=0)

            # loop through day list
            for day_delta in self.data["selectedDaysOfStay"]:
                day_start = admission_start + timedelta(days=day_delta-1)
                day_end = day_start + timedelta(days=1)
                # add to query
                subquery = self.query & f"patient_id = '{pt_id}' AND absolute_time >= '{day_start}' AND absolute_time < '{day_end}'"
                stay_filtered_query = stay_filtered_query + subquery

        self.query = stay_filtered_query
        return self.query

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
    

