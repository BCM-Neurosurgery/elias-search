from django.apps import AppConfig
import datajoint as dj
import os

class EsServerConfig(AppConfig):
    name = 'es_server'