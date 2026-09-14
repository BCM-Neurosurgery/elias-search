"""
Database router to separate Django's internal models from neural data models.
Django internal models (sessions, admin, etc.) use the default SQLite database.
Neural data models use the neural_data MySQL database.
"""

class NeuralDataRouter:
    """
    A router to control database operations for neural data models.
    """
    
    # Models that should use the neural_data database
    # Using app_label.model_name format to avoid circular imports
    neural_data_models = {
        'es_server.ExtChunk',
        'es_server.ExtStitched', 
        'es_server.Patient',
        'es_server.Admission',
        'es_server.ProbeConfig',
        'es_server.Probes',
        'es_server.MacroContacts',
        'es_server.AreaFsVox',
        'es_server.TOCInstance',
        'es_server.NEVChunks',
        'es_server.NS3Chunks',
        'es_server.NS5Chunks',
        'es_server.NSPChunks',
        'es_server.StitchedChunks',
        'es_server.TaskComments',
        'es_server.StartComments',
        'es_server.StopComments',
        'es_server.TaskIDComments',
    }
    
    def db_for_read(self, model, **hints):
        """
        Point neural data models to the neural_data database.
        """
        if model._meta.app_label == 'es_server': # model_label in self.neural_data_models:
            return 'neural_data'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """
        Point neural data models to the neural_data database.
        """
        if model._meta.app_label == 'es_server': # model_label in self.neural_data_models:
            return 'neural_data'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database.
        """
        db1 = self.db_for_read(obj1)
        db2 = self.db_for_read(obj2)
        return db1 == db2
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Only allow migrations on the default database.
        Neural data models are managed=False, so they don't need migrations.
        """
        if db == 'neural_data':
            return False
        return True
