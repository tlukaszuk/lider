from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('application_rate/new/', views.ar_form, name="ar_new"),
    path('application_rate/<int:ar_id>/edit', views.ar_form, name="ar_edit"),
    path('application_rate/<int:ar_id>/remove', views.ar_remove, name="ar_remove"),
    path('application_rate/report_pdf/', views.create_report_pdf, name='report_pdf'),
    path('application_rate/<int:ar_id>/report_pdf', views.create_report_pdf, name='report_pdf_by_id'),
    path('application_rate/prepare_order/', views.prepare_order, name='prepare_order'),
    path('application_rate/<str:ar_ids>/prepare_order', views.prepare_order, name='prepare_order_by_ids'),

    path('order/order_pdf/', views.create_order_pdf, name='order_pdf'),
    path('order/order_pdf_with_save/', views.create_order_pdf, {'save': True}, name='order_pdf_with_save'),
    path('order/<int:order_id>/order_pdf/', views.create_order_pdf, name='order_pdf_by_id'),

    path('application_rate/index', views.history, name="history"),
    path('order/orders/', views.orders, name='orders'),

    path('login/', views.account_login, name='login'),
    path('logout/', views.account_logout, name='logout'),

    path('ajax/growing_fields_by_farmer/', views.growing_fields_by_farmer, name='growing_fields_by_farmer'),
    path('ajax/add_farmer/', views.add_farmer, name='add_farmer'),
    path('ajax/add_growing_field/', views.add_growing_field, name='add_growing_field'),
    path('ajax/orders_by_farmer/', views.orders_by_farmer, name='orders_by_farmer'),
    path('ajax/application_rates_by_farmer/', views.application_rates_by_farmer, name='application_rates_by_farmer'),
]