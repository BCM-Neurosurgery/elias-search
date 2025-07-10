from utils import dj_conn, parse_time
conn = dj_conn()
import datajoint as dj
from datajoint import schema
from emu24.schema import StitchedChunks, NSPChunks, StartComments, StopComments
from pyNsXStitch.helpers import get_nsx_start_timestamp
from datetime import datetime, timedelta

db_name = list(conn.schemas.keys)[0]
schema = dj.schema(db_name)
SAMPLING_RATE = 30_000

@schema
class StitchedChunksPlus(dj.Computed):
    definition = """
    -> StitchedChunks
    ---
    start_time: varchar(256)
    stop_time: varchar(256)
    """
    
    def make(self, key):
        try:
            start_chunks = NSPChunks.proj(start_chunk='chunk_id', start_absolute_time='absolute_time', start_ns5_file='ns5_file')
            stop_chunks = NSPChunks.proj(stop_chunk='chunk_id', stop_absolute_time='absolute_time', stop_ns5_file='ns5_file')
            start_comments = StartComments.proj(start_tid='comment_id', start_timestamp='timestamp')
            stop_comments = StopComments.proj(stop_tid='comment_id', stop_timestamp='timestamp')
            
            joined = (StitchedChunks() *  start_chunks * stop_chunks * start_comments * stop_comments) & key
            # get necessary fields from joined
            start_chunk_time, stop_chunk_time, start_comment_stamp, stop_comment_stamp = joined.fetch1(
                'start_absolute_time',
                'stop_absolute_time',
                'start_timestamp',
                'stop_timestamp'
            )
            # get comment delta for each chunk
            try:
                start_ns5 = joined.fetch1('start_ns5_file')
                start_delta = timedelta(seconds=(start_comment_stamp - get_nsx_start_timestamp(start_ns5)) / SAMPLING_RATE)
            except Exception as e:
                print(e)
                start_delta = timedelta(seconds=0)
            try:
                stop_ns5 = joined.fetch1('stop_ns5_file')
                stop_delta = timedelta(seconds=(stop_comment_stamp - get_nsx_start_timestamp(stop_ns5)) / SAMPLING_RATE)
            except Exception as e:
                print(e)
                stop_delta = timedelta(seconds=0)
            
            start_time = (parse_time(start_chunk_time) + start_delta).strftime('%Y-%m-%d %H:%M:%S.%f')
            stop_time = (parse_time(stop_chunk_time) + stop_delta).strftime('%Y-%m-%d %H:%M:%S.%f')
            
            self.insert1({**key, 'start_time': start_time, 'stop_time': stop_time})
        except Exception as e:
            print(f"Error processing key {key}: {e}")
            
