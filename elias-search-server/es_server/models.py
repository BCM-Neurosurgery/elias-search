from django.db import models

# define external models
class ExtChunk(models.Model):
    hash_ = models.BinaryField(max_length=16, primary_key=True)
    size = models.BigIntegerField()
    attachment_name = models.CharField(max_length=255, null=True)
    filepath = models.CharField(max_length=1000, null=True)
    contents_hash = models.BinaryField(max_length=16, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '~external_Ext_Chunk'
        managed = False

class ExtStitched(models.Model):
    hash_ = models.BinaryField(max_length=16, primary_key=True)
    size = models.BigIntegerField()
    attachment_name = models.CharField(max_length=255, null=True)
    filepath = models.CharField(max_length=1000, null=True)
    contents_hash = models.BinaryField(max_length=16, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '~external_Ext_Stitch'
        managed = False

# define datajoint schema models
class Patient(models.Model):
    patient_id = models.IntegerField(primary_key=True)
    dob = models.CharField(max_length=256)
    emu_id = models.CharField(max_length=256)

    class Meta:
        db_table = 'patient'
        managed = False


class Admission(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    admission_date = models.CharField(max_length=256)

    class Meta:
        db_table = 'admission'
        managed = False
        unique_together = (
            'patient_id', 'admission_id'
        )

class Probes(models.Model):
    pass

class ElectrodeContacts(models.Model):
    pass

class TOCInstance(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    base_file = models.CharField(max_length=256)
    
    class Meta:
        db_table = 't_o_c_instance'
        managed=False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id'
        )


class NEVChunks(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    nev_file = models.ForeignKey(
        ExtChunk,
        to_field='hash_',
        db_column='nev_file',
        on_delete=models.SET_NULL,
        related_name='nev_chunks'
    )

    class Meta:
        db_table = 'n_e_v_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )


class NS3Chunks(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()
    

    ns3_file = models.ForeignKey(
        ExtChunk,
        to_field='hash_',
        db_column='ns3_file',
        on_delete=models.SET_NULL,
        related_name='ns3_chunks'
    )

    class Meta:
        db_table = 'n_s3_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )

class NS5Chunks(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()
    
    ns5_file = models.ForeignKey(
        ExtChunk,
        to_field='hash_',
        db_column='ns5_file',
        on_delete=models.SET_NULL,
        related_name='ns5_chunks'
    )

    class Meta:
        db_table = 'n_s5_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )

class NSPChunks(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    file = models.CharField(max_length=256)
    absolute_time = models.CharField(max_length=256)

    nev_file = models.ForeignKey(
        ExtChunk,
        to_field='hash_',
        db_column='nev_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='nev_chunks'
    )

    ns5_file = models.ForeignKey(
        ExtChunk,
        to_field='hash_',
        db_column='ns5_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns5_chunks'
    )

    ns3_file = models.ForeignKey(
        ExtChunk,
        to_field='hash_',
        db_column='ns3_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns3_chunks'
    )

    class Meta:
        db_table = '__n_s_p_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )

class TaskComments(models.Model):
    comment_id = models.IntegerField(primary_key=True) 

    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    comment = models.CharField(max_length=256)
    timestamp = models.BigIntegerField()
    type_ = models.CharField(max_length=256)

    class Meta:
        db_table = '__task_comments'
        managed = False
        

class StartComments(models.Model):
    comment_id = models.IntegerField(primary_key=True) 

    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    emu_id = models.IntegerField()
    comment = models.CharField(max_length=256)
    timestamp = models.BigIntegerField()

    class Meta:
        db_table = '__start_comments'
        managed = False

class TaskIDComments(models.Model):
    comment_id = models.IntegerField(primary_key=True) 

    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    emu_id = models.IntegerField()
    comment = models.CharField(max_length=256)
    timestamp = models.BigIntegerField()
    task_name = models.CharField(max_length=256)

    class Meta:
        db_table = '__task_i_d_comments'
        managed = False

class StopComments(models.Model):
    comment_id = models.IntegerField(primary_key=True) 

    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    emu_id = models.IntegerField()
    comment = models.CharField(max_length=256)
    timestamp = models.BigIntegerField()

    class Meta:
        db_table = '__stop_comments'
        managed = False

class StitchedChunks(models.Model):
    patient_id = models.IntegerField()
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    start_chunk = models.IntegerField()
    nsp_id = models.IntegerField()
    start_tid = models.IntegerField()
    emu_id = models.IntegerField()
    stop_chunk = models.IntegerField()
    stop_tid = models.IntegerField()

    start_filename = models.CharField(max_length=256)
    stop_filename = models.CharField(max_length=256)

    nev_file = models.ForeignKey(
        ExtStitched,
        to_field='hash_',
        db_column='nev_file',
        on_delete=models.SET_NULL,
        related_name='nev_stitched'
    )

    ns5_file = models.ForeignKey(
        ExtStitched,
        to_field='hash_',
        db_column='ns5_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns5_stitched'
    )

    ns3_file = models.ForeignKey(
        ExtStitched,
        to_field='hash_',
        db_column='ns3_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns3_stitched'
    )

    class Meta:
        db_table = '__stitched_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'start_chunk', 'nsp_id',
            'start_tid', 'emu_id', 'stop_chunk', 'stop_tid', 'start_filename',
            'stop_filename', 'nev_file', 'ns3_file', 'ns5_file'
        )
