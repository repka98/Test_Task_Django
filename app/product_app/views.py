from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from icecream import ic
from rest_framework.viewsets import ReadOnlyModelViewSet
from datetime import datetime

from users.models import UserClient
from .models import Application, PackageHash, UploadFiles, AppealApplication, StatusApplication,CoordinationApplication,\
            TimeToProcessingReport, StatusBook, AppealBook, CoordinationBook

from .serializers import ApplicationSerializer
from .forms import UploadFileForm, DateOrder
import uuid
from numpy import nan
import json
from .analyze import get_analyzed_data

# Create your views here.

def home(request):
    template = loader.get_template('product_app/home.html')
    return HttpResponse(template.render(request=request))

# class HomeView(TemplateView):
# 	template_name = 'product_app/home.html'

def application(request):
    data = {'title': 'Заявки для работы'}
    for status in StatusBook.STATUS:
        st, create = StatusBook.objects.get_or_create(status=status[1])

    for appeal in AppealBook.APPEAL:
        app, create = AppealBook.objects.get_or_create(appeal=appeal[1])

    for coordination in CoordinationBook.COORDINATION:
        coord, create = CoordinationBook.objects.get_or_create(coordination=coordination[1])


    template = loader.get_template('product_app/application.html')
    return HttpResponse(template.render(request=request, context=data))


def application_list_view(request):
    template = loader.get_template('product_app/application_list.html')
    products = Application.objects.all()
    context = {
        'products': products,
    }
    return HttpResponse(template.render(request=request, context=context))


def get_count_application_all():
    return Application.objects.count()


def get_count():
    return Application.objects.count()


class ApplicationRequests:

    @staticmethod
    def get_count_application_all():
        return Application.objects.count()


    @staticmethod
    def get_count_application_by_date_lt(date_lt: datetime):
        return Application.objects.filter(created_at__lt=date_lt).count()

    @staticmethod
    def get_count_value_application_by_date_range(date_gt: datetime, date_lt: datetime):
        ids_by_period = Application.objects.filter (
            created_at__range=(date_gt, date_lt)).values_list('pk', flat=True)
        count_ids_by_period = ids_by_period.count()
        return {'count_ids_by_period': count_ids_by_period, 'ids_by_period': ids_by_period}


    @staticmethod
    def def_count_appeal(ids, appeal_name: str):
        appeal_id = AppealBook.objects.get(appeal=appeal_name)
        all_appeals = AppealApplication.objects.filter(
            appeal_id = appeal_id).count()

        ids_appeals = AppealApplication.objects.filter(
            application__in=ids
        ).filter(appeal_id = appeal_id).count()

        return {'ids_appeals': ids_appeals, 'all_appeals': all_appeals}

    @staticmethod
    def get_count_status(ids, status_name: str):
        status_id = StatusBook.objects.get(status=status_name)
        all_status = StatusApplication.objects.filter(
            status_id = status_id).count()
        ids_status = StatusApplication.objects.filter(
            application__in = ids
        ).filter(status_id = status_id).count()
        return {'ids_status': ids_status, 'all_status': all_status, }

    @staticmethod
    def get_count_packages(ids):
        all_packages = PackageHash.objects.all().count()
        ids_packages = Application.objects.filter(pk__in=ids).values_list('hash_data', flat=True).distinct().count()
        return {'ids_packages': ids_packages, 'all_packages': all_packages, }


    @staticmethod
    def get_count_user(ids):
        all_users = UserClient.objects.all().count()
        ids_users = Application.objects.filter(pk__in=ids).values_list('user_app', flat=True).distinct().count()
        return {'ids_users': ids_users, 'all_users': all_users, }


def get_data(request, data=None):
    app_cl = ApplicationRequests()
    template = loader.get_template('product_app/product_list.html')
    form = DateOrder(request.POST)
    if form.is_valid():
        app_date_start = form.cleaned_data['date_start']
        app_date_end = form.cleaned_data['date_end']
    else:
        form = DateOrder()
        app_date_start = datetime.today().date()
        app_date_end = datetime.today().date()
    products_count_all = app_cl.get_count_application_all()
    products_count_by_date_lt = app_cl.get_count_application_by_date_lt(app_date_end)
    # products_count_by_date_lt = Application.objects.filter(created_at__lt=app_date_end).count()
    product_by_period = app_cl.get_count_value_application_by_date_range(app_date_start, app_date_end)
    # products_ids_by_period = Application.objects.filter(created_at__range=(app_date_start, app_date_end)).values_list('pk', flat=True)
    #  = products_ids_by_period.count()
    appeal_duplicates = app_cl.def_count_appeal(ids=product_by_period['ids_by_period'], appeal_name='Дубликат')
    appeal_added = app_cl.def_count_appeal(ids=product_by_period['ids_by_period'], appeal_name='Добавление')
    appeal_extended = app_cl.def_count_appeal(ids=product_by_period['ids_by_period'], appeal_name='Расширение')

    status_processing_completed = app_cl.get_count_status(ids=product_by_period['ids_by_period'], status_name='Обработка завершена')
    status_sent_for_processing = app_cl.get_count_status(ids=product_by_period['ids_by_period'], status_name='Отправлена в обработку')
    status_returned_for_clarification = app_cl.get_count_status(ids=product_by_period['ids_by_period'], status_name='Возвращена на уточнение')

    packages = app_cl.get_count_packages(ids=product_by_period['ids_by_period'])

    users = app_cl.get_count_user(ids=product_by_period['ids_by_period'])
    products = {
        'product_by_period': product_by_period['count_ids_by_period'],
        'products_count_all': products_count_all,
    }

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


    # context = products | appeal_duplicates | appeal_added | appeal_extended | status_processing_completed | status_returned_for_clarification | status_sent_for_processing | packages | users

    # context = zip(
    #     products,
    #     appeal_duplicates,
    #     appeal_added,
    #     appeal_extended,
    #     status_processing_completed,
    #     status_sent_for_processing,
    #     status_returned_for_clarification,
    #     packages,
    #     users,
    # )
    # context = {
    #     'products': [products_count_all],
    #     'form': form,
    #     "products_count_by_date_lt": products_count_by_date_lt,
    #     "products_count_all": products_count_all,
    #     'product_by_period': {
    #         'count_ids_by_period': product_by_period['count_ids_by_period'],
    #     },
    #     "appeal_duplicates": {
    #         'all_appeals': appeal_duplicates['all_appeals'],
    #         'ids_appeals': appeal_duplicates['ids_appeals'],
    #     },
    #     "appeal_added": {
    #         'all_appeals': appeal_added['all_appeals'],
    #         'ids_appeals': appeal_added['ids_appeals'],
    #     },
    #     "appeal_extended": {
    #         'all_appeals': appeal_extended['all_appeals'],
    #         'ids_appeals': appeal_extended['ids_appeals'],
    #     },
    # }

    return HttpResponse(template.render(request=request, context= {'form': form, 'product_list': context}))



def application_upload_view(request):
    template = loader.get_template('product_app/product_upload.html')
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            template = loader.get_template('product_app/success_upload.html')
            fp = UploadFiles(file=form.cleaned_data['file'])
            fp.save()
            return HttpResponse(template.render(request=request, context={'pk': fp.pk}))
            # return render(request, 'product_app/success_upload.html', {'form': fp})
            # return HttpResponseRedirect(f"/product_app/success/{fp.pk}")
    else:
        form = UploadFileForm()
    return HttpResponse(template.render(request=request, context={'form': form}))
    # return render(request, "product_app/product_upload.html", {"form": form})


def get_or_create_user(user: dict):
    user_data, created = UserClient.objects.get_or_create(**user)
    return user_data

def get_or_create_hash(hash: str):
    hash_data, created = PackageHash.objects.get_or_create(hash=hash)
    return hash_data


def create_application_appeal(app, appeal, query):
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
    status_query = [status_data for status_data in query if
                    status_data.status == status]
    status_data = StatusApplication.objects.create (
        application=app,
        status_id=status_query[0],
    )
    status_data.save ()
    return status_data


def create_application_coordination(app, coordination, query):
    coordination_query = [coordination_data for coordination_data in query if
                    coordination_data.coordination == coordination]
    coordination_data = CoordinationApplication.objects.create (
        application=app,
        coordination_id=coordination_query[0],
    )
    coordination_data.save ()
    return coordination_data



def application_success_view(request, pk):
    template = loader.get_template('product_app/product_list.html')
    data_req = {'pk': pk, 'title': 'Заявки для работы'}
    if request.method == "GET":

        fp = UploadFiles.objects.filter(pk=pk).values()
        application_from_file = get_analyzed_data(fp[0]['file'])
        status_queryset  = StatusBook.objects.all()
        ic(status_queryset)
        appeal_queryset = AppealBook.objects.all()
        ic(appeal_queryset)
        coordination_queryset = CoordinationBook.objects.all()
        ic(coordination_queryset)
        for app in application_from_file:
            user_pk = get_or_create_user(app['user_data'])
            hash_pk = get_or_create_hash(app['ids_package_data'])

            app_pk = Application.objects.create(
                user_app=user_pk,
                hash_data=hash_pk,
                number_app = app['number_app_data'],
                created_at = datetime.strptime(app['created_data'], "%d.%m.%Y %H:%M:%S"),
                finished_at = datetime.strptime(app['finished_data'], "%d.%m.%Y %H:%M:%S") if app['finished_data'] is not nan else None,
            )
            app_pk.save()
            # appeal_query = [appeal_data for appeal_data in appeal_queryset if appeal_data.appeal == app['appeal_data']['appeal']]
            # appeal_data = AppealApplication.objects.create(
            #     application=app_pk,
            #     appeal_id=appeal_query[0],
            #     appel_view=app['appeal_data']['appel_view'],
            # )
            # appeal_data.save()
            create_application_appeal(app=app_pk, appeal=app['appeal_data'], query=appeal_queryset)
            # status_query = [status_data for status_data in status_queryset if status_data.status == app['status_data']]
            # status_data = StatusApplication.objects.create(
            #     application=app_pk,
            #     status=status_query[0],
            # )
            # status_data.save()
            create_application_status(app=app_pk, status=app['status_data'], query=status_queryset)

            time_from_request_to_proccssing_data = TimeToProcessingReport.objects.create(
                application=app_pk,
                time_from_request_to_processing=app['time_from_request_to_processing_data'],
            )
            time_from_request_to_proccssing_data.save()
            # coordination_query = [coordination_data for coordination_data in coordination_queryset if coordination_data.coordination == app['coordination_data']]
            # coordination_data = CoordinationApplication.objects.create(
            #     application=app_pk,
            #     coordination=coordination_query,
            # )
            # coordination_data.save()
            create_application_coordination(app=app_pk, coordination=app['coordination_data'], query=coordination_queryset)
    return HttpResponseRedirect(f"/product_app/get_data/")
    # return HttpResponse(template.render(request=request, context=data_req))
    # return render(request, 'product_app/product_list.html', context=data_req)
