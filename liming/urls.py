from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('form/', views.form, name="form"),
    path('form/<int:ar_id>/', views.form, name="form_edit"),
    path('remove/<int:ar_id>/', views.remove, name="remove"),
    path('history/', views.history, name="history"),
    path('login/', views.account_login, name='login'),
    path('logout/', views.account_logout, name='logout'),
    path('report_pdf/', views.create_report_pdf, name='report_pdf'),
    path('report_pdf/<int:ar_id>/', views.create_report_pdf, name='report_pdf_by_id'),
    path('prepare_order/', views.prepare_order, name='prepare_order'),
    path('prepare_order/<str:ar_ids>/', views.prepare_order, name='prepare_order_by_ids'),
    path('order_select/', views.order_select, name='order_select'),

    path('ajax/growing_fields_by_farmer/', views.growing_fields_by_farmer, name='growing_fields_by_farmer'),
    path('ajax/add_farmer/', views.add_farmer, name='add_farmer'),
    path('ajax/add_growing_field/', views.add_growing_field, name='add_growing_field'),
]