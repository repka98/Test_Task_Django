from django.urls import path

from .views import home, application,\
    application_upload_view, application_success_view, get_data

urlpatterns = [
    # домашняя страница приложения
    path("", home, name="home"),
    # страница предложения выбраить файл
    path("application_all/", application, name="application_all"),
    # страница выбора файла
    path("application_upload/", application_upload_view, name="application_upload"),
    # страница загрузка данных в модели
    path("success/<int:pk>/", application_success_view, name="success"),
    # страница отчета по данным из файла
    path("get_data/",get_data, name="get_data"),
]