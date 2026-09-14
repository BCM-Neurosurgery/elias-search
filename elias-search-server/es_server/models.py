from django.db import models

# define external models
class ExtChunk(models.Model):
    hash = models.BinaryField(max_length=16, primary_key=True)
    size = models.BigIntegerField()
    attachment_name = models.CharField(max_length=255, null=True)
    filepath = models.CharField(max_length=1000, null=True)
    contents_hash = models.BinaryField(max_length=16, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '~external_Ext_Chunk'
        managed = False

class ExtStitched(models.Model):
    hash = models.BinaryField(max_length=16, primary_key=True)
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
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    admission_date = models.CharField(max_length=256)

    class Meta:
        db_table = 'admission'
        managed = False
        unique_together = (
            'patient_id', 'admission_id'
        )
        
    def delete(self, *args, **kwargs):
        # manually delete dependent TOCInstances
        TOCInstance.objects.filter(
            patient_id=self.patient_id,
            admission_id=self.admission_id
        ).delete()

        super().delete(*args, **kwargs)

class ProbeConfig(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    config_id = models.IntegerField()

    start_time = models.CharField(max_length=256)
    end_time = models.CharField(max_length=256)
    mri_file = models.CharField(max_length=256)
    ct_file = models.CharField(max_length=256)
    pip_file = models.CharField(max_length=256)
    t1_file = models.CharField(max_length=256)

    class Meta:
        db_table = 'probe_config'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'config_id'
        )


class Probes(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    config_id = models.IntegerField()
    probe_id = models.IntegerField()

    label = models.CharField(max_length=64)
    region_target = models.CharField(max_length=64)
    micros_available = models.BooleanField()
    n_contacts = models.IntegerField()
    hemisphere = models.CharField(max_length=64)
    manufacturer = models.CharField(max_length=64)
    type = models.CharField(max_length=64)
    direction_x = models.FloatField()
    direction_y = models.FloatField()
    direction_z = models.FloatField()

    class Meta:
        db_table = 'probes'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'config_id', 'probe_id'
        )


class MacroContacts(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    config_id = models.IntegerField()
    probe_id = models.IntegerField()
    electrode_id = models.IntegerField()

    electrode_label = models.CharField(max_length=64)
    micro_adjacent = models.BooleanField()
    native_x = models.FloatField()
    native_y = models.FloatField()
    native_z = models.FloatField()
    mni305_x = models.FloatField()
    mni305_y = models.FloatField()
    mni305_z = models.FloatField()
    mni152_x = models.FloatField()
    mni152_y = models.FloatField()
    mni152_z = models.FloatField()

    class Meta:
        db_table = 'macro_contacts'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'config_id', 'probe_id', 'electrode_id'
        )


class AreaFsVox(models.Model):
    """FreeSurfer label of the voxel each macro contact sits in.

    The DataJoint table is keyed by the full MacroContacts key, so patient and
    admission are columns here and no join is needed to find which admissions
    have a contact in a given region.
    """
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    config_id = models.IntegerField()
    probe_id = models.IntegerField()
    electrode_id = models.IntegerField()

    area_fs_vox = models.CharField(max_length=64)

    class Meta:
        db_table = 'area_fs_vox'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'config_id', 'probe_id', 'electrode_id'
        )

class TOCInstance(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    base_file = models.CharField(max_length=256)
    
    class Meta:
        db_table = 't_o_c_instance'
        managed=False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id'
        )
    
    def delete(self, *args, **kwargs):
            # manually delete dependent NEVChunks, NS3Chunks, NS5Chunks
            NEVChunks.objects.filter(
                patient_id=self.patient_id,
                admission_id=self.admission_id,
                toc_id=self.toc_id
            ).delete()
            NS3Chunks.objects.filter(
                patient_id=self.patient_id,
                admission_id=self.admission_id,
                toc_id=self.toc_id
            ).delete()
            NS5Chunks.objects.filter(
                patient_id=self.patient_id,
                admission_id=self.admission_id,
                toc_id=self.toc_id
            ).delete()

            super().delete(*args, **kwargs)



class NEVChunks(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    nev_file = models.ForeignKey(
        ExtChunk,
        to_field='hash',
        db_column='nev_file',
        on_delete=models.CASCADE,
        related_name='nev_chunks'
    )

    class Meta:
        db_table = 'n_e_v_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )
        
    def delete(self, *args, **kwargs):
        # manually delete dependent NSPChunks
        NSPChunks.objects.filter(
            patient_id=self.patient_id,
            admission_id=self.admission_id,
            toc_id=self.toc_id,
            chunk_id=self.chunk_id,
            nsp_id=self.nsp_id
        ).delete()

        super().delete(*args, **kwargs)


class NS3Chunks(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()
    

    ns3_file = models.ForeignKey(
        ExtChunk,
        to_field='hash',
        db_column='ns3_file',
        on_delete=models.CASCADE,
        related_name='ns3_chunks'
    )

    class Meta:
        db_table = 'n_s3_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )

class NS5Chunks(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()
    
    ns5_file = models.ForeignKey(
        ExtChunk,
        to_field='hash',
        db_column='ns5_file',
        on_delete=models.CASCADE,
        related_name='ns5_chunks'
    )

    class Meta:
        db_table = 'n_s5_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )

class NSPChunks(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    file = models.CharField(max_length=256)
    absolute_time = models.CharField(max_length=256)

    nev_file = models.ForeignKey(
        ExtChunk,
        to_field='hash',
        db_column='nev_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='nev_chunks_nsp'
    )

    ns5_file = models.ForeignKey(
        ExtChunk,
        to_field='hash',
        db_column='ns5_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns5_chunks_nsp'
    )

    ns3_file = models.ForeignKey(
        ExtChunk,
        to_field='hash',
        db_column='ns3_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns3_chunks_nsp'
    )

    class Meta:
        db_table = '__n_s_p_chunks'
        managed = False
        unique_together = (
            'patient_id', 'admission_id', 'toc_id', 'chunk_id', 'nsp_id'
        )
        
    def delete(self, *args, **kwargs):
        # manually delete dependent TaskComments
        TaskComments.objects.filter(
            patient_id=self.patient_id,
            admission_id=self.admission_id,
            toc_id=self.toc_id,
            chunk_id=self.chunk_id,
            nsp_id=self.nsp_id
        ).delete()

        super().delete(*args, **kwargs)


class TaskComments(models.Model):
    comment_id = models.IntegerField(primary_key=True) 

    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    chunk_id = models.IntegerField()
    nsp_id = models.IntegerField()

    comment = models.CharField(max_length=256)
    timestamp = models.BigIntegerField()
    type = models.CharField(max_length=256)

    class Meta:
        db_table = '__task_comments'
        managed = False
        

class StartComments(models.Model):
    comment_id = models.ForeignKey(TaskComments, on_delete=models.CASCADE, db_column='comment_id') 

    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
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
    
    def delete(self, *args, **kwargs):
        # manually delete dependent StitchedChunks
        StitchedChunks.objects.filter(
            patient_id=self.patient_id,
            admission_id=self.admission_id,
            toc_id=self.toc_id,
            start_chunk=self.chunk_id,
            start_tid=self.comment_id,
            nsp_id=self.nsp_id
        ).delete()

        super().delete(*args, **kwargs)

class TaskIDComments(models.Model):
    comment_id = models.ForeignKey(TaskComments, on_delete=models.CASCADE, db_column='comment_id') 

    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
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
    comment_id = models.ForeignKey(TaskComments, on_delete=models.CASCADE, db_column='comment_id')

    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
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
        
    def delete(self, *args, **kwargs):
        # manually delete dependent StitchedChunks
        StitchedChunks.objects.filter(
            patient_id=self.patient_id,
            admission_id=self.admission_id,
            toc_id=self.toc_id,
            stop_chunk=self.chunk_id,
            stop_tid=self.comment_id,
            nsp_id=self.nsp_id
        ).delete()

        super().delete(*args, **kwargs) 

class StitchedChunks(models.Model):
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='patient_id')
    admission_id = models.IntegerField()
    toc_id = models.IntegerField()
    start_chunk = models.IntegerField()
    nsp_id = models.IntegerField()
    start_tid = models.ForeignKey(TaskComments, on_delete=models.CASCADE, db_column='start_tid', related_name='start_tid', to_field='comment_id')
    emu_id = models.IntegerField()
    stop_chunk = models.IntegerField()
    stop_tid = models.ForeignKey(TaskComments, on_delete=models.CASCADE, db_column='stop_tid', related_name='stop_tid', to_field='comment_id')

    start_filename = models.CharField(max_length=256)
    stop_filename = models.CharField(max_length=256)

    nev_file = models.ForeignKey(
        ExtStitched,
        to_field='hash',
        db_column='nev_file',
        on_delete=models.CASCADE,
        related_name='nev_stitched'
    )

    ns5_file = models.ForeignKey(
        ExtStitched,
        to_field='hash',
        db_column='ns5_file',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ns5_stitched'
    )

    ns3_file = models.ForeignKey(
        ExtStitched,
        to_field='hash',
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
