from django.contrib import admin
from .models import Application, StatusApplication, AppealApplication,CoordinationApplication, \
	TimeToProcessingReport, StatusBook, AppealBook, CoordinationBook, PackageHash, UploadFiles, UserClient
# Register your models here.
admin.site.register(Application)
admin.site.register(StatusApplication)
admin.site.register(AppealApplication)
admin.site.register(CoordinationApplication)
admin.site.register(TimeToProcessingReport)
admin.site.register(StatusBook)
admin.site.register(AppealBook)
admin.site.register(CoordinationBook)
admin.site.register(PackageHash)
admin.site.register(UploadFiles)

