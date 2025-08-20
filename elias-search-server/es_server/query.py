from .utils import parse_time
from .models import *
from datetime import datetime, timedelta, MINYEAR, MAXYEAR
import pandas as pd
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pyNsXStitch.helpers import get_nsx_start_timestamp, get_nsx_duration
import os
from django.db.models import Q, Min, Max

SAMPLING_RATE = 30_000
DATALAKE_PATH = os.environ.get('DATALAKE_PATH', "/mnt/datalake/data/emu")
STITCHED_PATH = os.environ.get('STITCHED_PATH', "/mnt/stitched/EMU-18112")

# define class to get absolute start timestamp of stitchedchunk
class QueryBuilder:
    def __init__(self, data, session_id=None):
        self.data = data
        # setup blank filter
        self.filter = Q()
        self.chunk_filter = Q()
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
            self.send_status("filtering dates 0/100")
            self._timerange_query_dl()
            self.send_status("filtering patients 10/100")
            self._patient_query()
            self.send_status("filtering tasks 20/100")
            self._task_query_dl()
            self.send_status("filtering stay days 40/100")
            self._stay_day_query_dl()
            self.send_status("filtering week times 50/100")
            self._weektime_query_dl()
            self.send_status("formatting results 60/100")
        else:
            self.send_status("filtering dates 0/100")
            self._timerange_query_s()
            self.send_status("filtering patients 10/100")
            self._patient_query()
            self.send_status("filtering stay days 20/100")
            self._stay_day_query_s()
            self.send_status("filtering week times 30/100")
            self._weektime_query_s()
            self.send_status("filtering tasks 40/100")
            self._task_query_s()
            self.send_status("formatting results 60/100")
    
    def format_query_results(self):
        # initialize result dictionary
        if self.data["mode"] == "datalake":
            rows = NSPChunks.objects.filter(self.filter).select_related('patient_id', 'nev_file', 'ns5_file', 'ns3_file').values(
                'patient_id__emu_id',
                'nev_file__filepath',
                'ns5_file__filepath',
                'ns3_file__filepath',
                'absolute_time',
                'nsp_id'
            )
            query_df = pd.DataFrame(list(rows))
        else:
            rows = StitchedChunks.objects.filter(self.filter).select_related('patient_id', 'nev_file', 'ns5_file', 'ns3_file', 'start_tid').values(
                # merge keys
                'patient_id',
                'admission_id',
                'toc_id',
                'start_chunk',
                # results
                'patient_id__emu_id',
                'nev_file__filepath',
                'ns5_file__filepath',
                'ns3_file__filepath',
                'start_tid__timestamp',
                'nsp_id'
            )
            query_df = pd.DataFrame(list(rows))
            # also get df for start chunks
            chunk_rows = NSPChunks.objects.filter(self.chunk_filter).values(
                'patient_id',
                'admission_id',
                'toc_id',
                'chunk_id',
                'nsp_id',
                'absolute_time',
                'ns5_file__filepath',
            )
            chunk_df = pd.DataFrame(list(chunk_rows))
            # merge start chunk data
            query_df = query_df.merge(chunk_df, 
            left_on=['patient_id', 'admission_id', 'toc_id', 'nsp_id', 'start_chunk'], 
            right_on=['patient_id', 'admission_id', 'toc_id', 'nsp_id','chunk_id'],
            how='inner'
            )
            query_df.rename(columns={
                'absolute_time': 'start_chunk__absolute_time',
                'ns5_file__filepath_x': 'ns5_file__filepath',
                'ns5_file__filepath_y': 'start_chunk__ns5_file__filepath'
                }, inplace=True)

        # format table for datalake NSPChunks
        if self.data["mode"] == "datalake":
            query_df["start_time"] = query_df["absolute_time"].apply(
                lambda x: parse_time(x).strftime("'%Y-%m-%d %H:%M:%S'")
                )
            query_df["file"] = query_df["nev_file__filepath"].apply(
                lambda x: x.replace('.nev', '', 1) if x else None
                )
            def get_duration(x):
                try:
                    return f"{get_nsx_duration(os.path.join(DATALAKE_PATH, x)) / SAMPLING_RATE:.2f}"
                except Exception as e:
                    print(f"Error fetching duration for {x}: {e}")
                    return None
            query_df["duration_s"] = query_df["ns5_file__filepath"].apply(get_duration)
            query_df["end_time"] = query_df.apply(
                lambda row: parse_time(row['absolute_time']) + timedelta(seconds=float(row['duration_s'])) if row['duration_s'] else None,
                axis=1  
            )
            
            query_df['filetypes'] = query_df.apply(
                lambda row: ";".join([ft for ft in ['nev', 'ns5', 'ns3'] if row[f"{ft}_file__filepath"]]),
                axis=1
            )
            query_df['source'] = 'datalake'
        else:
            # format table for stitched chunks
            query_df["file"] = query_df["nev_file__filepath"].apply(
                lambda x: x.replace('.nev', '', 1) if x else None
                )

            query_df['filetypes'] = query_df.apply(
                lambda row: ";".join([ft for ft in ['nev', 'ns5', 'ns3'] if row[f"{ft}_file__filepath"]]),
                axis=1
            )

            def get_duration(x):
                try:
                    return f"{get_nsx_duration(os.path.join(STITCHED_PATH, x)) / SAMPLING_RATE:.2f}"
                except Exception as e:
                    print(f"Error fetching duration for {x}: {e}")
                    return None
            query_df['duration_s'] = query_df["ns5_file__filepath"].apply(get_duration)
            
            def get_start_time(row):
                try:
                    chunk_start_time = parse_time(row['start_chunk__absolute_time']) 
                    chunk_start_stamp = get_nsx_start_timestamp(os.path.join(DATALAKE_PATH, row['start_chunk__ns5_file__filepath']))
                    offset_s = (row['start_tid__timestamp'] - chunk_start_stamp) / SAMPLING_RATE
                    return chunk_start_time + timedelta(seconds=offset_s)
                except Exception as e:
                    print(f"Error fetching start time for {row}: {e}")
                    return None
            query_df["start_time"] = query_df.apply(get_start_time, axis=1)

            def get_end_time(row):
                try:
                    return row['start_time'] + timedelta(seconds=float(row['duration_s']))
                except Exception as e:
                    print(f"Error fetching end time for {row}: {e}")
                    return None
            query_df["end_time"] = query_df.apply(get_end_time, axis=1)
            
            query_df['source'] = 'stitched'
        
        # now format results
        results = query_df[[
                'patient_id__emu_id',
                'file',
                'start_time',
                'duration_s',
                'end_time',
                'filetypes',
                'nsp_id',
                'source'
            ]]
                                                          
        results.rename(columns={'patient_id__emu_id': 'patient'}, inplace=True)
        self.send_status("finished 100/100")
        return results.to_dict(orient='list')
    
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

        # now set filter by time
        self.filter &= Q(absolute_time__gte=from_time, absolute_time__lte=to_time)
        return self.filter

    def _patient_query(self):
        # get patient id and filter nsp rows
        self.filter &= Q(patient_id__emu_id__in=self.data["selectedPatients"])
        return self.filter
    
    def _task_query_dl(self):
        # first filter task list depending on flags

        # return filter as is if allData requested
        if self.data["allData"]:
            return self.filter
        
        if self.data["allTasks"]:
            all_tasks = TaskIDComments.objects.values_list('task_name', flat=True).distinct()
            self.data["selectedTasks"] = all_tasks
        if self.data["excludeStim"]:
            self.data["selectedTasks"] = [task for task in self.data["selectedTasks"] 
                                          if "pep" not in task.lower() and "AD" not in task 
                                          and "oracle" not in task and "xai" not in task]
        
        task_filter = Q()
        # get all TaskIDComments for selected tasks
        query_id = TaskIDComments.objects.filter(task_name__in=self.data["selectedTasks"]).values('patient_id', 'admission_id', 'emu_id').distinct()
        for entry in query_id:
            try:
                start_chunk, toc_id = StartComments.objects.filter(
                    patient_id=entry['patient_id'],
                    emu_id=entry['emu_id']).values('chunk_id', 'toc_id')[0].values()
                stop_chunk = StopComments.objects.filter(
                    patient_id=entry['patient_id'],
                    emu_id=entry['emu_id']).values('chunk_id')[0]['chunk_id']
                # add filter
                task_filter |= Q(
                    patient_id=entry['patient_id'], 
                    admission_id=entry['admission_id'], 
                    chunk_id__gte=start_chunk, 
                    chunk_id__lte=stop_chunk, 
                    toc_id=toc_id,
                    )
            except Exception as e:
                print(f"Error fetching start and stop chunks for patient {entry['patient_id']} and emu_id {entry['emu_id']}: {e}- not including this task")
        self.filter &= task_filter
        return self.filter

    def _stay_day_query_dl(self):
        # set filters list
        filters = Q()
        # get current patient ids
        pt_ids = NSPChunks.objects.filter(self.filter).values_list('patient_id', flat=True).distinct()
        for pt_id in pt_ids:
            try:
                # get admission start
                admission_start = Admission.objects.filter(patient_id=pt_id).values_list('admission_date', flat=True)[0]
                admission_start = parse_time(admission_start).replace(hour=0, minute=0, second=0, microsecond=0)
                # get minimum timestamp in NSPChunks
                min_ts_str = NSPChunks.objects.filter(patient_id=pt_id).aggregate(Min('absolute_time'))['absolute_time__min']
                min_ts = parse_time(min_ts_str)
                if min_ts - admission_start < timedelta(seconds=0) or min_ts - admission_start > timedelta(hours=48):
                    raise ValueError("first chunk is not within 48 hours of admission start - somethign is wrong with this recording")
            except Exception as e:
                print(f"Error fetching admission date for patient {pt_id}: {e} - including all data for this patient")
                filters |= Q(patient_id=pt_id)
                continue

            # loop through day list
            for day_delta in self.data["selectedDaysOfStay"]:
                day_start = admission_start + timedelta(days=day_delta-1)
                day_end = day_start + timedelta(days=1)
                # add to query

                filter = Q(patient_id=pt_id, absolute_time__gte=day_start, absolute_time__lt=day_end)
                filters |= filter
            
        self.filter &= filters
        return self.filter

    def _weektime_query_dl(self):
        # just return query as is if we have the maximal set
        if self.data["selectedTimesOfWeek"] and len(self.data["selectedTimesOfWeek"]) == 7 * 24:
            return self.filter
    
        # get current min and max time
        min_ts_str = NSPChunks.objects.filter(self.filter).aggregate(Min('absolute_time'))['absolute_time__min']
        max_ts_str = NSPChunks.objects.filter(self.filter).aggregate(Max('absolute_time'))['absolute_time__max']

        try:
            min_dt = parse_time(min_ts_str)
            max_dt = parse_time(max_ts_str)
        except Exception as e:
            print("No more entries found - query will end")
            return self.filter

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
        filters = Q()
        for start, end in valid_ranges:
            start_str = start.strftime("%Y-%m-%d %H:%M:%S.%f")
            end_str = end.strftime("%Y-%m-%d %H:%M:%S.%f")
            filters |= Q(absolute_time__gte=start_str, absolute_time__lt=end_str)
            
        self.filter &= filters
        return self.filter

    def _task_query_s(self):
        # first filter task list depending on flags
        # return table as is if allData requested
        if self.data["allData"]:
            return self.filter
        
        if self.data["allTasks"]:
            all_tasks = all_tasks = TaskIDComments.objects.values_list('task_name', flat=True).distinct()
            self.data["selectedTasks"] = all_tasks
        if self.data["excludeStim"]:
            self.data["selectedTasks"] = [task for task in self.data["selectedTasks"] 
                                          if "pep" not in task.lower() and "AD" not in task]
        
        filters = Q()
        for task in self.data["selectedTasks"]:
            # get patient id and emu_id - will iterate through them to get all chunks
            data = TaskIDComments.objects.filter(task_name=task).values('patient_id', 'emu_id').distinct()
            for item in data:
                filters |= Q(patient_id=item['patient_id'], emu_id=item['emu_id'])
            
        self.filter &= filters
        return self.filter
    
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
        
        # now set filter by time
        self.chunk_filter &= Q(absolute_time__gte=from_time, absolute_time__lte=to_time)
        return self.filter
    
    def _stay_day_query_s(self):
        # set filters list
        filters = Q()
        # get current patient ids
        pt_ids = NSPChunks.objects.filter(self.filter).values_list('patient_id', flat=True).distinct()
        for pt_id in pt_ids:
            try:
                # get admission start
                admission_start = Admission.objects.filter(patient_id=pt_id).values_list('admission_date', flat=True)[0]
                admission_start = parse_time(admission_start).replace(hour=0, minute=0, second=0, microsecond=0)
                # get minimum timestamp in NSPChunks
                min_ts_str = NSPChunks.objects.filter(patient_id=pt_id).aggregate(Min('absolute_time'))['absolute_time__min']
                min_ts = parse_time(min_ts_str)
                if min_ts - admission_start < timedelta(seconds=0) or min_ts - admission_start > timedelta(hours=48):
                    raise ValueError("first chunk is not within 48 hours of admission start - somethign is wrong with this recording")
            except Exception as e:
                print(f"Error fetching admission date for patient {pt_id}: {e} - including all data for this patient")
                filters |= Q(patient_id=pt_id)
                continue

            # loop through day list
            for day_delta in self.data["selectedDaysOfStay"]:
                day_start = admission_start + timedelta(days=day_delta-1)
                day_end = day_start + timedelta(days=1)
                # add to query

                filter = Q(patient_id=pt_id, absolute_time__gte=day_start, absolute_time__lt=day_end)
                filters |= filter
            
        self.chunk_filter &= filters
        return self.filter
        
    
    def _weektime_query_s(self):
       # just return query as is if we have the maximal set
        if self.data["selectedTimesOfWeek"] and len(self.data["selectedTimesOfWeek"]) == 7 * 24:
            return self.filter
    
        # get current min and max time
        min_ts_str = NSPChunks.objects.filter(self.chunk_filter).aggregate(Min('absolute_time'))['absolute_time__min']
        max_ts_str = NSPChunks.objects.filter(self.chunk_filter).aggregate(Max('absolute_time'))['absolute_time__max']

        try:
            min_dt = parse_time(min_ts_str)
            max_dt = parse_time(max_ts_str)
        except Exception as e:
            print("No more entries found - query will end")
            return self.filter

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
        filters = Q()
        for start, end in valid_ranges:
            start_str = start.strftime("%Y-%m-%d %H:%M:%S.%f")
            end_str = end.strftime("%Y-%m-%d %H:%M:%S.%f")
            filters |= Q(absolute_time__gte=start_str, absolute_time__lt=end_str)
            
        self.chunk_filter &= filters
        return self.filter

