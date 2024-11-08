from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.template import loader
from datetime import datetime

from users.models import UserClient
from .models import Application, PackageHash, UploadFiles, AppealApplication, StatusApplication,CoordinationApplication,\
            TimeToProcessingReport, StatusBook, AppealBook, CoordinationBook

from .forms import UploadFileForm, DateOrder
from numpy import nan
from .analyze import get_analyzed_data

# Create your views here.

def home(request):
    """Главная страница"""
    template = loader.get_template('product_app/home.html')
    return HttpResponse(template.render(request=request))


def application(request):
    """Страница начала работы с приложением"""
    data = {'title': 'Заявки для работы'}
    # добавление в словари данных при первом запуске приложения
    # словари заявок, статусов, согласований
    for status in StatusBook.STATUS:
        st, create = StatusBook.objects.get_or_create(status=status[1])

    for appeal in AppealBook.APPEAL:
        app, create = AppealBook.objects.get_or_create(appeal=appeal[1])

    for coordination in CoordinationBook.COORDINATION:
        coord, create = CoordinationBook.objects.get_or_create(coordination=coordination[1])


    template = loader.get_template('product_app/application.html')
    return HttpResponse(template.render(request=request, context=data))

class ApplicationRequests:
    """Класс для обработки запросов по заявкам"""
    @staticmethod
    def get_count_application_all():
        """Возвращает количество заявок"""
        return Application.objects.count()


    @staticmethod
    def get_count_application_by_date_lt(date_lt: datetime):
        """
        Возвращает количество заявок до указанной даты
        :param

        :param
        date_lt - дата до которой нужно получить количество заявок
        :return
        - int
        """
        return Application.objects.filter(created_at__lt=date_lt).count()

    @staticmethod
    def get_count_value_application_by_date_range(date_gt: datetime, date_lt: datetime):
        """
        Возвращает количество заявок в указанном диапазоне дат
        :param
        date_gt - дата с которой нужно получить количество заявок
        date_lt - дата до которой нужно получить количество заявок
        :return
        - dict
        {'count_ids_by_period': количество заявок в указанном диапазоне дат,
         'ids_by_period': список id заявок в указанном диапазоне дат}
        """
        ids_by_period = Application.objects.filter (
            created_at__range=(date_gt, date_lt)).values_list('pk', flat=True)
        count_ids_by_period = ids_by_period.count()
        return {'count_ids_by_period': count_ids_by_period, 'ids_by_period': ids_by_period}


    @staticmethod
    def def_count_appeal(ids, appeal_name: str):
        """
        Возвращает количество состояний заявок относительно диапазона дат и за весь период

        :param
        ids - список id заявок
        :param
        appeal_name - название статуса
        :return
        - dict
        {'ids_appeals': количество состояний заявки относительно диапазона дат,
         'all_appeals': количество состояний заявок за весь период}
        """

        appeal_id = AppealBook.objects.get(appeal=appeal_name)
        all_appeals = AppealApplication.objects.filter(
            appeal_id = appeal_id).count()

        ids_appeals = AppealApplication.objects.filter(
            application__in=ids
        ).filter(appeal_id = appeal_id).count()

        return {'ids_appeals': ids_appeals, 'all_appeals': all_appeals}

    @staticmethod
    def get_count_status(ids, status_name: str):
        """
        Возвращает количество статусов заявок относительно диапазона дат и за весь период
        :param
        ids - список id заявок
        :param
        status_name - название статуса
        :return
        - dict
        {'ids_status': количество статусов заявки относительно диапазона дат,
         'all_status': количество статусов заявок за весь период}
        """
        status_id = StatusBook.objects.get(status=status_name)
        all_status = StatusApplication.objects.filter(
            status_id = status_id).count()
        ids_status = StatusApplication.objects.filter(
            application__in = ids
        ).filter(status_id = status_id).count()
        return {'ids_status': ids_status, 'all_status': all_status, }

    @staticmethod
    def get_count_packages(ids):
        """
        Возвращает количество пакетов заявок относительно диапазона дат и за весь период
        :param
        ids - список id заявок
        :param
        status_name - название статуса
        :return
        - dict
        {'ids_packages': количество пакетов заявок относительно диапазона дат,
         'all_packages': количество пакетов заявок за весь период}
        """
        all_packages = PackageHash.objects.all().count()
        ids_packages = Application.objects.filter(pk__in=ids).values_list('hash_data', flat=True).distinct().count()
        return {'ids_packages': ids_packages, 'all_packages': all_packages, }


    @staticmethod
    def get_count_user(ids):
        """
        Возвращает количество пользователей относительно диапазона дат и за весь период
        :param
        ids - список id заявок
        :return
        - dict
        {'ids_users': количество пакетов заявок относительно диапазона дат,
         'all_users': количество пакетов заявок за весь период}
        """
        all_users = UserClient.objects.all().count()
        ids_users = Application.objects.filter(pk__in=ids).values_list('user_app', flat=True).distinct().count()
        return {'ids_users': ids_users, 'all_users': all_users, }


def get_data(request):
    """
    Функция для получения данных для отображения на странице в виде отчета
    :param
    request - запрос

    :return
    - HttpResponse
    """
    # Инициализация класса для работы с запросами к заявкам
    app_cl = ApplicationRequests()
    # Шаблон страницы
    template = loader.get_template('product_app/product_list.html')
    # Инициализация класса формы на страницы
    form = DateOrder(request.POST)
    # Проверка формы на валидность
    if form.is_valid():
        # Заполнение датами из формы
        app_date_start = form.cleaned_data['date_start']
        app_date_end = form.cleaned_data['date_end']
        message = f"Даты заполнены"
        message_error = f""
    else:
        # Если какой-то из дат нет, то на сегодняшнее число и ошибку заполнения
        form = DateOrder()
        app_date_start = datetime.today().date()
        app_date_end = datetime.today().date()
        message_error = f"Вы не заполнили все даты"
        message = f""
    # Получение всех заявок
    products_count_all = app_cl.get_count_application_all()

    # Получение заявок до выбранной даты (не используется)
    products_count_by_date_lt = app_cl.get_count_application_by_date_lt(app_date_end)

    # Получение заявок за выбранный период дат
    product_by_period = app_cl.get_count_value_application_by_date_range(app_date_start, app_date_end)

    # Получение состояния заявки "Дубликат"
    appeal_duplicates = app_cl.def_count_appeal(ids=product_by_period['ids_by_period'], appeal_name='Дубликат')

    # Получение состояния заявки "Добавление"
    appeal_added = app_cl.def_count_appeal(ids=product_by_period['ids_by_period'], appeal_name='Добавление')

    # Получение состояния заявки "Расширение"
    appeal_extended = app_cl.def_count_appeal(ids=product_by_period['ids_by_period'], appeal_name='Расширение')

    # Получение статуса заявки "Обработка завершена"
    status_processing_completed = app_cl.get_count_status(ids=product_by_period['ids_by_period'], status_name='Обработка завершена')

    # Получение статуса заявки "Отправлена в обработку"
    status_sent_for_processing = app_cl.get_count_status(ids=product_by_period['ids_by_period'], status_name='Отправлена в обработку')

    # Получение статуса заявки "Возвращена на уточнение"
    status_returned_for_clarification = app_cl.get_count_status(ids=product_by_period['ids_by_period'], status_name='Возвращена на уточнение')

    # Получение пакетов заявок за все время и за выбранный период
    packages = app_cl.get_count_packages(ids=product_by_period['ids_by_period'])

    # Получение пользователей за все время и за выбранный период
    users = app_cl.get_count_user(ids=product_by_period['ids_by_period'])

    # Создание словаря для заявок для отчета
    products = {
        'product_by_period': product_by_period['count_ids_by_period'],
        'products_count_all': products_count_all,
    }

    # Создание массива словарей для таблицы на страницы
    context = [
        {
            'name': 'Загруженных заявок',
            'products': products,
        },
        {
            'name': 'Дубли',
            'products': appeal_duplicates,
        },
        {
            'name': 'На создании',
            'products': appeal_added,
        },
        {
            'name': 'На расширении',
            'products': appeal_extended,
        },
        {
            'name': 'Обработка завершена',
            'products': status_processing_completed,
        },
        {
            'name': 'Возвращена на уточнение',
            'products': status_returned_for_clarification,
        },
        {
            'name': 'Отправлена в обработку',
            'products': status_sent_for_processing,
        },
        {
            'name': 'Пакетов',
            'products': packages,
        },
        {
            'name': 'Пользователей',
            'products': users,
        },

    ]

    return HttpResponse(
        template.render(
            request=request,
            context= {
                'form': form,
                'product_list': context,
                'message': message,
                'message_error': message_error
            }
        )
    )



def application_upload_view(request):
    """
    Функция страницы выбора файла для загрузки
    :param request:
    :return:
    """
    # Шаблон страницы
    template = loader.get_template('product_app/product_upload.html')
    # Проверка выполненого запроса
    if request.method == "POST":
        # Загрузка в форму данных из запроса
        form = UploadFileForm(request.POST, request.FILES)
        # Проверка валидации формы
        if form.is_valid():
            # Подгрузка нового шаблона при валиной форме
            template = loader.get_template('product_app/success_upload.html')
            # Сохранение данных о файле в модель
            fp = UploadFiles(file=form.cleaned_data['file'])
            fp.save()
            return HttpResponse(template.render(request=request, context={'pk': fp.pk}))

    else:
        # Создание пустой формы
        form = UploadFileForm()
    return HttpResponse(template.render(request=request, context={'form': form}))


def get_or_create_user(user: dict):
    """
    Функция возвращает пользователя по имени, фамилии, отчеству, если такого нет, создает
    :param user: dict
    {
        'name': имя,
        'last_name': фамилия,
        'surname': отчество
    }
    :return:
    - Series
    Пользователь из модели
    """
    user_data, created = UserClient.objects.get_or_create(**user)
    return user_data

def get_or_create_hash(hash: str):
    """
    Функция возвращает хеш по значению, если такого нет, создает
    :param hash:
    :return:
    - Series
    Хеш из модели
    """
    hash_data, created = PackageHash.objects.get_or_create(hash=hash)
    return hash_data


def create_application_appeal(app, appeal, query):
    """
    Функция создает связь заявки с типом заявки
    :param app: Series
    заявка из модели
    :param appeal: dict
    состояние заявки из словаря от обработчика файла данных
    :param query: list
    все состояния заявки из модели справочника состояний заявки
    :return:
    - Series
    Связь заявки с типом заявки из модели
    """
    appeal_query = [appeal_data for appeal_data in query if
                    appeal_data.appeal == appeal['appeal']]
    appeal_data = AppealApplication.objects.create (
        application=app,
        appeal_id=appeal_query[0],
        appeal_view=appeal['appeal_view'],
    )
    appeal_data.save ()
    return appeal_data

def create_application_status(app, status, query):
    """
    Функция создает связь заявки со статусом заявки
    :param app: Series
    заявка из модели
    :param status: str
    статус заявки
    :param query: list
    все статусы заявки из модели справочника статусов заявки
    :return:
    - Series
    Связь заявки со статусом заявки из модели
    """
    status_query = [status_data for status_data in query if
                    status_data.status == status]
    status_data = StatusApplication.objects.create (
        application=app,
        status_id=status_query[0],
    )
    status_data.save ()
    return status_data


def create_application_coordination(app, coordination, query):
    """
    Функция создает связь заявки с согласованием заявки
    :param app: Series
    заявка из модели
    :param coordination:
    согласование заявки из словаря от обработчика файла данных
    :param query:
    все согласования заявки из модели справочника согласования заявки
    :return:
    - Series
    Связь заявки с согласованием заявки из модели
    """
    coordination_query = [coordination_data for coordination_data in query if
                    coordination_data.coordination == coordination]
    coordination_data = CoordinationApplication.objects.create (
        application=app,
        coordination_id=coordination_query[0],
    )
    coordination_data.save ()
    return coordination_data



def application_success_view(request, pk: int):
    """
    Функция страницы обработки ответа от загруженного файла данных
    :param request:
    :param pk: int
    pk от модели содержащий путь от загруженного файла
    :return:
    - HttpResponseRedirect
    Переход на адрес формирования отчета
    """
    # Проверка метода запроса
    if request.method == "GET":
        # Получение из параметра функции pk и получение от модели пути файла
        fp = UploadFiles.objects.filter(pk=pk).values()

        # Запуск функции обработки загруженного файла
        application_from_file = get_analyzed_data(fp[0]['file'])

        # Получение от моделей справочников данных
        status_queryset  = StatusBook.objects.all()
        appeal_queryset = AppealBook.objects.all()
        coordination_queryset = CoordinationBook.objects.all()

        # Обработка и запись данных в модели заявок и связанных с ней моделей
        for app in application_from_file:
            # Создание иил получение пользователя
            user_pk = get_or_create_user(app['user_data'])

            # Создание или получение хэш пакета заявок
            hash_pk = get_or_create_hash(app['ids_package_data'])

            # Сохранение самой заявки в модели
            app_pk = Application.objects.create(
                user_app=user_pk,
                hash_data=hash_pk,
                number_app = app['number_app_data'],
                created_at = datetime.strptime(app['created_data'], "%d.%m.%Y %H:%M:%S"),
                finished_at = datetime.strptime(app['finished_data'], "%d.%m.%Y %H:%M:%S") if app['finished_data'] is not nan else None,
            )
            app_pk.save()

            # Сохранение заявки и состояния заявки в модели
            create_application_appeal(app=app_pk, appeal=app['appeal_data'], query=appeal_queryset)

            # Сохранение заявки и статуса заявки в модели
            create_application_status(app=app_pk, status=app['status_data'], query=status_queryset)

            # Сохранение заявки и согласования заявки в модели
            create_application_coordination(app=app_pk, coordination=app['coordination_data'], query=coordination_queryset)

            # Сохранение заявки и время обработки заявки в модели
            time_from_request_to_proccssing_data = TimeToProcessingReport.objects.create(
                application=app_pk,
                time_from_request_to_processing=app['time_from_request_to_processing_data'],
            )
            time_from_request_to_proccssing_data.save()

    return HttpResponseRedirect(f"/product_app/get_data/")

