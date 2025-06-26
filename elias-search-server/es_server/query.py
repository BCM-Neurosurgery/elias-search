from .utils import dj_conn
from datetime import datetime, timedelta, MINYEAR, MAXYEAR
import datajoint as dj
from datajoint.schemas import VirtualModule
from pyNsXStitch.helpers import get_nsx_start_timestamp, get_nsx_duration
import os

SAMPLING_RATE = 30_000
DATALAKE_PATH = os.environ.get('DATALAKE_PATH', "/mnt/datalake/data/emu")
STITCHED_PATH = os.environ.get('STITCHED_PATH', "/mnt/stitched/EMU-18112")
class QueryBuilder:
    def __init__(self, data):
        self.data = data
        # connect to db and get all data
        conn = dj_conn()
        self.schemas = VirtualModule(module_name='schemas', schema_name='emu24_stitch', connection=conn)
        if self.data["mode"] == "datalake":
            self.table = self.schemas.NSPChunks()
        else:
            self.table = self.schemas.StitchedChunks()
    
    def waterfall_query(self):
        if self.data["mode"] == "datalake":
            # run all steps of query
            # self._timerange_query_dl()
            self._patient_query()
            self._task_query_dl()
            # self._stay_day_query()
            # self._weektime_query()
        else:
            # self._timerange_query_s()
            self._patient_query()
            # self._stay_day_query_s()
            # self._weektime_query_s()
            self._task_query_s()
        return self.table
    
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

        if self.data["mode"] == "datalake":
            for row in self.table:
                patient_emu_id = (self.schemas.Patient() & f"patient_id = '{row['patient_id']}'").fetch1('emu_id')
                res_patient = patient_emu_id
                formatted_time = datetime.strptime(row['absolute_time'], "%Y-%m-%d %H:%M:%S.%f").strftime("'%Y-%m-%d %H:%M:%S'")
                res_start_time = formatted_time
                filetypes = []
                if row['nev_file']:
                    filetypes.append('nev')
                    file = row['nev_file'].replace(DATALAKE_PATH, '{DATALAKE_PATH}', 1)
                    file = file.replace('.nev', '', 1)
                    res_file = file
                else:
                    res_file = 'NULL'
                if row['ns5_file']:
                    try:
                        filetypes.append('ns5')
                        duration = get_nsx_duration(row['ns5_file']) / SAMPLING_RATE
                        res_duration_s = f"{duration:.2f}"
                        end_time = datetime.strptime(row['absolute_time'], "%Y-%m-%d %H:%M:%S.%f") + timedelta(seconds=duration)
                        res_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        res_duration_s = 'NULL'
                        res_end_time = 'NULL'
                else:
                    res_duration_s = 'NULL'
                    res_end_time = 'NULL'
                if row['ns3_file']:
                    filetypes.append('ns3')
                
                # set remaining results
                res_filetypes = ";".join(filetypes)
                res_nsp_id = row['nsp_id']
                res_source = 'datalake' 
                
                # append results
                results['patient'].append(res_patient)
                results['start_time'].append(res_start_time)
                results['file'].append(res_file)
                results['duration_s'].append(res_duration_s)
                results['end_time'].append(res_end_time)
                results['filetypes'].append(res_filetypes)
                results["nsp_id"].append(res_nsp_id)
                results['source'].append(res_source)
        else:
            for row in self.table:
                patient_emu_id = (self.schemas.Patient() & f"patient_id = '{row['patient_id']}'").fetch1('emu_id')
                # set available res
                res_patient = patient_emu_id
                res_source = 'stitched'
                res_nsp_id = row['nsp_id']
                filetypes = []
                if row['nev_file']:
                    filetypes.append('nev')
                    file = row['nev_file'].replace(STITCHED_PATH, '{STITCHED_PATH}', 1)
                    file = file.replace('.nev', '', 1)
                    res_file = file
                else:
                    res_file = 'NULL'
                if row['ns5_file']:
                    filetypes.append('ns5')
                if row['ns3_file']:
                    filetypes.append('ns3')
                res_filetypes = ";".join(filetypes)
                try:
                    chunk_time, chunk_ns5 = (
                        self.schemas.NSPChunks() & 
                        f"patient_id = '{row['patient_id']}' AND toc_id = '{row['toc_id']}' AND nsp_id = '{row['nsp_id']}' AND chunk_id = '{row['start_chunk']}'"
                        ).fetch1('absolute_time', 'ns5_file')
                    start_stamp = (
                        self.schemas.StartComments() & 
                        f"patient_id = '{row['patient_id']}' AND comment_id = '{row['start_tid']}' AND toc_id = '{row['toc_id']}' AND nsp_id = '{row['nsp_id']}'"
                        ).fetch('timestamp')[0]
                    chunk_time = datetime.strptime(chunk_time, "%Y-%m-%d %H:%M:%S.%f")
                    comment_offset = (start_stamp - get_nsx_start_timestamp(chunk_ns5)) / SAMPLING_RATE
                    duration = get_nsx_duration(row['ns5_file']) / SAMPLING_RATE
                    start_ts = chunk_time + timedelta(seconds=comment_offset)
                    end_ts = start_ts + timedelta(seconds=duration)
                    res_start_time = start_ts.strftime("%Y-%m-%d %H:%M:%S")
                    res_duration_s = f'{duration:.2f}'
                    res_end_time = end_ts.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    res_start_time = 'NULL'
                    res_duration_s = 'NULL'
                    res_end_time = 'NULL'
                results['patient'].append(res_patient)
                results['start_time'].append(res_start_time)
                results['file'].append(res_file)
                results['duration_s'].append(res_duration_s)
                results['end_time'].append(res_end_time)
                results['filetypes'].append(res_filetypes)
                results["nsp_id"].append(res_nsp_id)
                results['source'].append(res_source)

        return results
    
    def _timerange_query_dl(self):
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
        self.table = self.table & f'absolute_time >= "{from_time}"'
        self.table = self.table & f'absolute_time <= "{to_time}"'
        return self.table

    def _patient_query(self):
        # get patient id and filter nsp rows
        pt_ids = []
        for patient in self.data["selectedPatients"]:
            # get patient id and qu
            pt_id = (self.schemas.Patient() & f"emu_id = '{patient}'").fetch1('patient_id')
            pt_ids.append(pt_id)
        filter = " OR ".join([f"patient_id = '{pt_id}'" for pt_id in pt_ids])
        self.table = self.table & filter
        return self.table
    
    def _task_query_dl(self):
        # first filter task list depending on flags

        # return table as is if allData requested
        if self.data["allData"]:
            return self.table
        
        if self.data["allTasks"]:
            all_tasks = self.schemas.TaskIDComments()
            task_list = list(set(all_tasks.fetch('task_name')))
            self.data["selectedTasks"] = task_list
        if self.data["excludeStim"]:
            self.data["selectedTasks"] = [task for task in self.data["selectedTasks"] 
                                          if "pep" not in task.lower() and "AD" not in task 
                                          and "oracle" not in task and "xai" not in task]
        
        filters = []
        for task in self.data["selectedTasks"]:
            # get patient id and emu_id - will iterate through them to get all chunks
            data = (self.schemas.TaskIDComments() & f"task_name = '{task}'").fetch(format="frame")
            data = data.reset_index()
            data = data.drop_duplicates(subset=['patient_id', 'emu_id', 'toc_id'])
            for idx, row in data.iterrows():
                # get start comment nsp id
                start_chunk_query = self.schemas.StartComments() & f"patient_id = '{row.patient_id}' AND emu_id = '{row.emu_id}'"
                try:
                    start_chunk_id = start_chunk_query.fetch('chunk_id')[0]
                except IndexError:
                    start_chunk_id = None
                # get stop comment nsp id
                stop_chunk_query = self.schemas.StopComments() & f"patient_id = '{row.patient_id}' AND emu_id = '{row.emu_id}'"
                try:
                    stop_chunk_id = stop_chunk_query.fetch('chunk_id')[0]
                except IndexError:
                    stop_chunk_id = None
                # add all chunks
                if start_chunk_id == None or stop_chunk_id == None:
                    continue
                for id_ in range(start_chunk_id, stop_chunk_id + 1):
                    subquery = f"(patient_id = '{row.patient_id}' AND chunk_id = '{id_}' AND toc_id = '{row.toc_id}')"
                    filters.append(subquery)
        filter = " OR ".join(filters)
        self.table = self.table & filter
        return self.table

    def _stay_day_query_dl(self):
        stay_filtered_query = self.schemas.NSPChunks() & '0=1'
        # get current patient ids
        pt_ids = list(set(self.table.fetch('patient_id')))
        for pt_id in pt_ids:
            # get admission start
            admission_start = self.schemas.Admission() & f"patient_id = '{pt_id}'"
            admission_start = datetime.strptime(admission_start, "%Y-%m-%d %H:%M:%S.%f").replace(hour=0, minute=0, second=0, microsecond=0)

            # loop through day list
            for day_delta in self.data["selectedDaysOfStay"]:
                day_start = admission_start + timedelta(days=day_delta-1)
                day_end = day_start + timedelta(days=1)
                # add to query
                subquery = self.table & f"patient_id = '{pt_id}' AND absolute_time >= '{day_start}' AND absolute_time < '{day_end}'"
                stay_filtered_query = stay_filtered_query + subquery

        self.table = stay_filtered_query
        return self.table

    def _weektime_query_dl(self):
         # just return query as is if we have the maximal set
        if self.data["selectedTimesOfWeek"] and len(self.data["selectedTimesOfWeek"]) == 7 * 24:
            return self.table
    
        # get current min and max time
        min_ts_str = (dj.U().aggr(self.table, n='min(absolute_time)').fetch1("n"))
        max_ts_str = (dj.U().aggr(self.table, n='max(absolute_time)').fetch1("n"))

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
            subquery = self.table & f
            time_filtered_query = subquery if time_filtered_query is None else(time_filtered_query + subquery)

        self.table = time_filtered_query
        return self.table

    def _task_query_s(self):
        # first filter task list depending on flags
        # return table as is if allData requested
        if self.data["allData"]:
            return self.table
        
        if self.data["allTasks"]:
            all_tasks = self.schemas.TaskIDComments()
            task_list = list(set(all_tasks.fetch('task_name')))
            self.data["selectedTasks"] = task_list
        if self.data["excludeStim"]:
            self.data["selectedTasks"] = [task for task in self.data["selectedTasks"] 
                                          if "pep" not in task.lower() and "AD" not in task]
        
        filters = []
        for task in self.data["selectedTasks"]:
            # get patient id and emu_id - will iterate through them to get all chunks
            data = (self.schemas.TaskIDComments() & f"task_name = '{task}'").fetch(format="frame")
            data = data.reset_index()
            data = data.drop_duplicates(subset=['patient_id', 'emu_id', 'toc_id'])
            for idx, row in data.iterrows():
                # get associated stitched_chunk
                subquery = f"(patient_id = '{row.patient_id}' AND emu_id = '{row.emu_id}')"
                filters.append(subquery)

        filter = " OR ".join(filters)
        self.table = self.table & filter
        return self.table
    

