from pandas import read_excel

# Справочники для поиска статусов в отчетах
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
	"""
	Функция аналитики загруженного файла .xlsx
	:param
	file_path - путь до файла .xlsx

	:return
	- list
	список обработанных данных для записи в модели
	"""
	# Чтение файла
	data = read_excel(file_path)
	# Инициализация списка
	application = []
	# Подсчет пакетов содержащих заявки в виде словаря Пример: {'64e482c3a472457a0b2e0547': 90}
	id_package_count = data['ID пакета'].value_counts()


	def get_names(user_str: str):
		"""
		Функция получения фамилии, имени, отчества пользователя
		:param user_str: str
		:return:
		- dict
		{
			'last_name': фамилия,
			'name': имя,
			'surname': отчество
		}
		"""
		user_data = user_str.split(' ')
		return {'last_name': user_data[0], 'name': user_data[1], 'surname': user_data[2]}


	def get_appeals(appeal_str: str):
		"""
		Функция получения статуса заявки из справочников для поиска статусов в отчетах
		APPEAL_ADDED
		APPEAL_EXTENDED
		APPEAL_DUPLICATED
		:param appeal_str: str
		текст поля заявка
		:return:
		-dict
		{
			'appeal': статус заявки из справочника,
			'appeal_view': текст поля заявка
		}
		"""
		if appeal_str in APPEAL_ADDED:
			return {'appeal': APPEAL_ADDED[1], 'appeal_view': appeal_str}
		if appeal_str in APPEAL_EXTENDED:
			return{'appeal': APPEAL_EXTENDED[1], 'appeal_view': appeal_str}
		if appeal_str.startswith(APPEAL_DUPLICATED):
			return {'appeal': APPEAL_DUPLICATED[1], 'appeal_view': appeal_str}


	def get_application(application):
		"""
		Функция обрабатывает переданный датасет и возвращает отформатированный словарь
		:param application:
		:return:
		- dict
		{
			'user_data': пользователь,
			'appeal_data': состояние заявки,
			'coordination_data': согласование заявки,
			'status_data': статус заявки,
			'created_data': дата создания заявки,
			'finished_data': дата окончания обработки заявки,
			'time_from_request_to_processing_data': время от создания заявки до конца обработки,
			'number_app_data': номер заявки,
			'ids_package_data': ID пакета заявок,
		}
		"""
		# Получение пользователя из строки
		user_data = get_names(application['Автор заявки'])
		# Получение состояния заявки из строки
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

	# Из сформированного ранее словаря достаем ключи и значения ключей
	for key, value in id_package_count.items():
		# Фильтруем датасет для поиска всех пакетов с таким значением
		application_by_ids = data[data['ID пакета'] == key]
		# Из сформированного списка по пакету берем индексы строк и проходим по ним для обработки данных
		for app in application_by_ids.index:
			# Создаем обработанный словарь для записи в модели
			application_data = get_application(data.iloc[app])
			# Добавляем очередной словарь в массив ответа функции
			application.append(application_data)

	return application
