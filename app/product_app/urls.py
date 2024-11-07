from django.urls import path

from .views import home, application, application_list_view, \
    application_upload_view, application_success_view, get_data

urlpatterns = [
    path("", home, name="home"),
    path("application_all/", application, name="application_all"),
    path("application_list/", application_list_view, name="application_list"),
    path("application_upload/", application_upload_view, name="application_upload"),
    path("success/<int:pk>/", application_success_view, name="success"),
    path("get_data/",get_data, name="get_data"),
]