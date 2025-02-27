from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('expense/', views.expense_page, name='expense'),
    path('manage-categories/', views.manage_categories_page, name='manage_categories'),
    path('manage-payment-methods/', views.manage_payment_methods_page, name='manage_payment_methods'),
    path('manage-source-of-income/', views.manage_source_of_income, name='manage_source_of_income'),
    path('budget/', views.budget_management, name='budget_management'),
    path('graph/', views.graph_view, name='graph'),
]