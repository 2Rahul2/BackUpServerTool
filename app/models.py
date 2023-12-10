from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
# Create your models here.
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
import pytz

User = get_user_model()
class FolderFiles(models.Model):
    name = models.CharField(max_length=500)
    file = models.BinaryField()
    subBranchId = models.IntegerField()
    size_mb = models.DecimalField(max_digits=100 ,default=1 , decimal_places=6 , null=True)

    def __str__(self):
        return str(self.name)

class SubFolder(models.Model):
    name = models.CharField(max_length=500)
    mainBranchId = models.IntegerField()
    SecondaryBranchId = models.IntegerField(null=True)
    subFolder = models.ManyToManyField('self',null=True , symmetrical=False)
    files = models.ManyToManyField(FolderFiles)
    size_mb = models.DecimalField(max_digits=100 ,default=1 , decimal_places=6 , null=True)
    def __str__(self):
        return self.name
class MainBranch(models.Model):
    user = models.ForeignKey(User  , blank=True ,null=True ,on_delete=models.SET_NULL)
    name = models.CharField(max_length=500)
    subFolder = models.ManyToManyField(SubFolder ,null=True ,blank=True)
    dateInfo = models.DateTimeField()
    size_mb = models.DecimalField(max_digits=100 ,default=1 , decimal_places=6 , null=True)
    files = models.ManyToManyField(FolderFiles ,null=True ,blank=True)
    # def save(self, *args, **kwargs):
    #     # Set the time zone to 'Asia/Kolkata' (IST)
    #     ist_timezone = pytz.timezone('Asia/Kolkata')

    #     # Get the current UTC time
    #     utc_now = timezone.now()

    #     # Convert UTC time to IST
    #     ist_time = utc_now.astimezone(ist_timezone)

    #     # Set the IST time as the created_at value
    #     self.dateInfo = ist_time

    #     super().save(*args, **kwargs)
    def __str__(self):
        return str(self.dateInfo)

@receiver(pre_delete, sender=MainBranch)
def delete_files_related_to_main_branch(sender, instance, **kwargs):
    instance.files.all().delete()


@receiver(pre_delete, sender=SubFolder)
def delete_files_realted_to_sub_folder(sender ,instance ,**kwargs):
    instance.files.all().delete()
    
@receiver(pre_delete ,sender=SubFolder)
def delete_subFolder_related_to_sub_folder(sender ,instance ,**kwargs):
    instance.subFolder.all().delete()

@receiver(pre_delete, sender=MainBranch)
def delete_sub_folder_related_to_main_branch(sender,instance ,**kwargs):
    instance.subFolder.all().delete()

