from .utils import dj_conn, parse_time
from datetime import datetime, timedelta, MINYEAR, MAXYEAR
import datajoint as dj
from datajoint.schemas import VirtualModule
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pyNsXStitch.helpers import get_nsx_start_timestamp, get_nsx_duration
import os

SAMPLING_RATE = 30_000
DATALAKE_PATH = os.environ.get('DATALAKE_PATH', "/mnt/datalake/data/emu")
STITCHED_PATH = os.environ.get('STITCHED_PATH', "/mnt/stitched/EMU-18112")

# define class to get absolute start timestamp of stitchedchunk


class QueryBuilder:
    def __init__(self, data, session_id=None):
        self.data = data
        # connect to db and get all data
        conn = dj_conn()
        self.schemas = VirtualModule(module_name='schemas', schema_name='emu24_stitch', connection=conn)
        if self.data["mode"] == "datalake":
            self.table = self.schemas.NSPChunks()
        else:
            self.table = self.schemas.StitchedChunks()
        self.session_id = session_id
        self.channel_layer = get_channel_layer()
    
    def send_status(self, message):
        if self.session_id:
            async_to_sync(self.channel_layer.group_send)(
                f'progress_{self.session_id}',
                {
                    'type': 'send_progress',
                    'message': {'status': message}
                }
            )

    def waterfall_query(self):
        if self.data["mode"] == "datalake":
            # run all steps of query
            self.send_status("filtering dates")
            self._timerange_query_dl()
            self.send_status("filtering patients")
            self._patient_query()
            self.send_status("filtering tasks")
            self._task_query_dl()
            self.send_status("filtering stay days")
            self._stay_day_query_dl()
            self.send_status("filtering week times")
            self._weektime_query_dl()
        else:
            self.send_status("filtering dates")
            self._timerange_query_s()
            self.send_status("filtering patients")
            self._patient_query()
            self.send_status("filtering stay days")
            self._stay_day_query_s()
            self.send_status("filtering week times")
            self._weektime_query_s()
            self.send_status("filtering tasks")
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

        total = len(self.table)
        if self.data["mode"] == "datalake":
            for i, row in enumerate(self.table):
                patient_emu_id = (self.schemas.Patient() & f"patient_id = '{row['patient_id']}'").fetch1('emu_id')
                res_patient = patient_emu_id
                formatted_time = parse_time(row['absolute_time']).strftime("'%Y-%m-%d %H:%M:%S'")
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
                        end_time = parse_time(row['absolute_time']) + timedelta(seconds=duration)
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

                if i % 20 == 0:
                    self.send_status(f"Processed {i}/{total} rows")
        else:
            for i, row in enumerate(self.table):
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
                    chunk_time = parse_time(chunk_time)
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
                if i % 20 == 0:
                    self.send_status(f"Processed {i}/{total} rows")

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
        # set filters list
        filters = []
        # get current patient ids
        pt_ids = list(set(self.table.fetch('patient_id')))
        for pt_id in pt_ids:
            # get admission start
            admission_data = self.schemas.Admission() & f"patient_id = '{pt_id}'"
            admission_start = admission_data.fetch1('admission_date')
            admission_start = parse_time(admission_start).replace(hour=0, minute=0, second=0, microsecond=0)

            # loop through day list
            for day_delta in self.data["selectedDaysOfStay"]:
                day_start = admission_start + timedelta(days=day_delta-1)
                day_end = day_start + timedelta(days=1)
                # add to query
                filter = f"(patient_id = '{pt_id}' AND absolute_time >= '{day_start}' AND absolute_time < '{day_end}')"
                filters.append(filter)
            

        filter = " OR ".join(filters)
        self.table = self.table & filter
        return self.table

    def _weektime_query_dl(self):
        # just return query as is if we have the maximal set
        if self.data["selectedTimesOfWeek"] and len(self.data["selectedTimesOfWeek"]) == 7 * 24:
            return self.table
    
        # get current min and max time
        min_ts_str = (dj.U().aggr(self.table, n='min(absolute_time)').fetch1("n"))
        max_ts_str = (dj.U().aggr(self.table, n='max(absolute_time)').fetch1("n"))

        min_dt = parse_time(min_ts_str)
        max_dt = parse_time(max_ts_str)

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
            filters.append(f'(absolute_time >= "{start_str}" AND absolute_time < "{end_str}")')
            
        filter = " OR ".join(filters)
        self.table = self.table & filter
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
    
    def _timerange_query_s(self):
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
        
        # now create table to filter from
        start_chunks = self.schemas.NSPChunks.proj(
            start_chunk='chunk_id', 
            start_absolute_time='absolute_time',
            )
        
        joint_table = (self.table * start_chunks)

        # now filter by time
        joint_table = joint_table & f'start_absolute_time >= "{from_time}"'
        joint_table = joint_table & f'start_absolute_time <= "{to_time}"'
        
        # get keys and filter original table
        filtered_keys = joint_table.proj()
        self.table = self.table & filtered_keys
        return self.table
    
    def _stay_day_query_s(self):
        # set filters list
        filters = []
        # get current patient ids
        pt_ids = list(set(self.table.fetch('patient_id')))
        
        # now create table to filter from
        start_chunks = self.schemas.NSPChunks.proj(
            start_chunk='chunk_id', 
            start_absolute_time='absolute_time',
            )
        
        joint_table = (self.table * start_chunks)
        
        for pt_id in pt_ids:
            try:
                # get admission start
                admission_data = self.schemas.Admission() & f"patient_id = '{pt_id}'"
                admission_start = admission_data.fetch1('admission_date')
                admission_start = parse_time(admission_start).replace(hour=0, minute=0, second=0, microsecond=0)
            except Exception as e:
                print(f"Error fetching admission date for patient {pt_id}: {e} - including all data for this patient")
                filter = f"(patient_id = '{pt_id}')"
                filters.append(filter)
                continue

            # loop through day list
            for day_delta in self.data["selectedDaysOfStay"]:
                day_start = admission_start + timedelta(days=day_delta-1)
                day_end = day_start + timedelta(days=1)
                # add to query
                filter = f"(patient_id = '{pt_id}' AND start_absolute_time >= '{day_start}' AND start_absolute_time < '{day_end}')"
                filters.append(filter)
            

        filter = " OR ".join(filters)
        joint_table = joint_table & filter
        
        # get keys and filter original table
        filtered_keys = joint_table.proj()
        self.table = self.table & filtered_keys
        return self.table
    
    def _weektime_query_s(self):
        # just return query as is if we have the maximal set
        if self.data["selectedTimesOfWeek"] and len(self.data["selectedTimesOfWeek"]) == 7 * 24:
            return self.table
        
        # now create table to filter from
        start_chunks = self.schemas.NSPChunks.proj(
            start_chunk='chunk_id', 
            start_absolute_time='absolute_time',
            )
        
        joint_table = (self.table * start_chunks)
    
        # get current min and max time
        min_ts_str = (dj.U().aggr(joint_table, n='min(start_absolute_time)').fetch1("n"))
        max_ts_str = (dj.U().aggr(joint_table, n='max(start_absolute_time)').fetch1("n"))

        min_dt = parse_time(min_ts_str)
        max_dt = parse_time(max_ts_str)

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
            filters.append(f'(start_absolute_time >= "{start_str}" AND start_absolute_time < "{end_str}")')
            
        filter = " OR ".join(filters)
        joint_table = joint_table & filter
        
        # get keys and filter original table
        filtered_keys = joint_table.proj()
        self.table = self.table & filtered_keys
        return self.table
    

