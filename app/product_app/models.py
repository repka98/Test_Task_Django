from django.db import models
from datetime import datetime
from users.models import UserClient


# Create your models here.


class PackageHash(models.Model):
	data = models.DateTimeField(auto_now_add=True)
	hash = models.CharField(max_length=255)

	class Meta:
		verbose_name_plural = 'Hashes'
		verbose_name = 'Hash'

	def __str__(self):
		return f"{self.data} {self.hash}"


class Application(models.Model):
	"""Класс для хранения данных о заявках"""
	number_app = models.CharField(max_length=12)
	user_app = models.ForeignKey(UserClient, related_name='user_app', on_delete=models.CASCADE)
	hash_data = models.ForeignKey(PackageHash, related_name='hash_data', on_delete=models.CASCADE, default=1)
	created_at = models.DateTimeField(blank=True, null=True)
	finished_at = models.DateTimeField(blank=True, null=True)

	def __str__(self):
		return f"Заявка ��� {self.number_app} от {self.user_app.last_name} {self.user_app.name}"

	class Meta:
		verbose_name_plural = 'Applications'
		verbose_name = 'Application'


class AppealBook(models.Model):
	APPEAL = (
		('added', 'Добавление'),
		('extended', 'Расширение'),
		('duplicate', 'Дубликат')
	)
	appeal = models.CharField(max_length=200, default='', choices=APPEAL)

	def __str__(self):
		return f"{self.appeal}"



class AppealApplication(models.Model):
	"""Класс для хранения данных о состоянии заявки"""


	appeal_id = models.ForeignKey(AppealBook, related_name='appeal_book', on_delete=models.CASCADE)
	application = models.ForeignKey(Application, related_name='appeal', on_delete=models.CASCADE)
	appeal_view = models.CharField(max_length=200, default='')

	def __str__(self):
		return f"Заявка ��� {self.application.number_app} от " \
		       f"{self.application.user_app.last_name} {self.application.user_app.name} " \
		       f"состояние {self.appeal_view}"


class CoordinationBook(models.Model):
	COORDINATION = (
		('material_not_added', 'Материал не выбран'),
		('coordination_no_required', 'Согласование не требуется'),
		('extended_after_coordination', 'Расширен после согласования'),
		('extended_without_coordination', 'Расширен без согласования'),
	)
	coordination = models.CharField(max_length=200, default='', choices=COORDINATION)

	def __str__(self):
		return f"{self.coordination}"


class CoordinationApplication(models.Model):
	"""Класс для хранения данных о согласовании заявка"""

	coordination_id = models.ForeignKey(CoordinationBook, related_name='coordination_book', on_delete=models.CASCADE)
	application = models.ForeignKey(Application, related_name='coordination',on_delete=models.CASCADE)

	def __str__(self):
		return f"Заявка ��� {self.application.number_app} от " \
		       f"{self.application.user_app.last_name} {self.application.user_app.name} " \
		       f"согласование {self.coordination_id.coordination}"


class StatusBook(models.Model):
	STATUS = (
		('sent_for_processing','Отправлена в обработку'),
		('returned_for_clarification','Возвращена на уточнение'),
		('sent_for_processing_repeated','Отправлена в обработку (повторно)'),
		('processing_completed','Обработка завершена'),
		('in_process_repeated','В обработке (повторно)'),
		('in_process_confirmed','В обработке (подтверждена)'),
	)
	status = models.CharField(choices=STATUS, default='', max_length=200)

	def __str__(self):
			return f"{self.status}"


class StatusApplication(models.Model):
	"""Класс для хранения данных о статусе заявки"""


	status_id = models.ForeignKey(StatusBook, related_name='status_book', on_delete=models.CASCADE)
	application = models.ForeignKey(Application, related_name='status', on_delete=models.CASCADE)

	def __str__(self):
			return f"Заявка ��� {self.application.number_app} от " \
			       f"{self.application.user_app.last_name} {self.application.user_app.name} " \
			       f"статус {self.status_id.status}"


class TimeToProcessingReport(models.Model):
	"""Класс для хранения отчета о времени обработки заявки"""
	time_from_request_to_processing = models.CharField(max_length=200, default='Обработка не завершена')
	application = models.OneToOneField(Application, related_name='time_to_processing', on_delete=models.CASCADE)

	def __str__(self):
		return f"Заявка ��� {self.application.number_app} от " \
		       f"{self.application.user_app.last_name} {self.application.user_app.name} " \
		       f"время обработки {self.time_from_request_to_processing}"


class UploadFiles(models.Model):
	file = models.FileField(upload_to='uploads_model')
