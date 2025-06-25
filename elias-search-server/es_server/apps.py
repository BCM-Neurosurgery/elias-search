from django.apps import AppConfig
import datajoint as dj
import os

class DatajointConn(AppConfig):
    name = 'es_server'

    def ready(self):
        from emu24 import settings
        dj.config['database.user'] = os.environ["DJ_USER"]
        dj.config['database.password'] = os.environ["DJ_PASSWORD"]
        dj.config['database.host'] = os.environ["DJ_HOST"]
        dj.config['database.port'] = int(os.environ["DJ_PORT"])
        dj.config['safemode'] = settings.DJ_CONFIG_SAFEMODE
        dj.config['stores'] = settings.DJ_CONFIG_STORES
        os.environ['DJ_SUPPORT_FILEPATH_MANAGEMENT'] = 'TRUE'
        conn = dj.conn()