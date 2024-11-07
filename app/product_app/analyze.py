from pandas import read_excel
import pandas as pd
import numpy as np
from icecream import ic

APPEAL_ADDED = (
	'добавление', 'Добавление', 'ДОБАВЛЕНИЕ'
)

APPEAL_EXTENDED = (
	'расширение', 'Расширение', 'РАСШИРЕНИЕ'
)

APPEAL_DUPLICATED = (
	'дубликат', 'Дубликат', 'ДУБЛИКАТ'
)

def get_analyzed_data(file_path):
	data = read_excel (file_path)
	application = []
	ic(data.shape)
	id_package_count = data['ID пакета'].value_counts()


	def get_names(user_str):
		user_data = user_str.split(' ')
		return {'last_name': user_data[0], 'name': user_data[1], 'surname': user_data[2]}


	def get_appeals(appeal_str):
		if appeal_str in APPEAL_ADDED:
			return {'appeal': APPEAL_ADDED[1], 'appeal_view': appeal_str}
		if appeal_str in APPEAL_EXTENDED:
			return{'appeal': APPEAL_EXTENDED[1], 'appeal_view': appeal_str}
		if appeal_str.startswith(APPEAL_DUPLICATED):
			return {'appeal': APPEAL_DUPLICATED[1], 'appeal_view': appeal_str}


	def get_application(application):
		user_data = get_names(application['Автор заявки'])
		appeal_data = get_appeals(application['Состояние заявки'])
		coordination_data: str = application['Согласование'].capitalize()
		status_data = application['Статус заявки'].capitalize()
		created_data = application['Дата создания заявки']
		finished_data = application['Дата окончания обработки']
		time_from_request_to_processing_data = application['Время от создания заявки до конца обработки (в часах)']
		number_app_data = application['Номер заявки']
		ids_package_data = application['ID пакета']

		return {
			'user_data': user_data,
			'appeal_data': appeal_data,
			'coordination_data': coordination_data,
			'status_data': status_data,
			'created_data': created_data,
			'finished_data': finished_data,
			'time_from_request_to_processing_data': time_from_request_to_processing_data,
			'number_app_data': number_app_data,
			'ids_package_data': ids_package_data,
		}

	for key, value in id_package_count.items():

		application_by_ids = data[data['ID пакета'] == key]

		for app in application_by_ids.index:
			application_data = get_application(data.iloc[app])
			application.append(application_data)

	return application
#
# app = get_analyzed_data('E:/Nikita/testing_data.xlsx')
# ic([appl['finished_data'] for appl in app])