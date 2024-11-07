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


def get_data(request, data=None):
    template = loader.get_template('product_app/product_list.html')
    form = DateOrder(request.POST)
    if form.is_valid():
        app_date_start = form.cleaned_data['date_start']
        app_date_end = form.cleaned_data['date_end']
    else:
        form = DateOrder()
        app_date_start = datetime.today().date()
        app_date_end = datetime.today().date()
    products_count_all = Application.objects.count()
    products_count_by_date_lt = Application.objects.filter(created_at__lt=app_date_end).count()
    products_count_by_period = Application.objects.filter(created_at__range=(app_date_start, app_date_end)).count()
    ic()
    context = {
        'products': [products_count_all],
        'form': form,
        "products_count_by_date_lt": products_count_by_date_lt,
        "products_count_all": products_count_all,
        "products_count_by_period": products_count_by_period,
    }

    return HttpResponse(template.render(request=request, context=context))



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
