from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('flaticons/', views.flaticons, name='flaticons'),
    path('job_details/<int:id>/', views.job_details, name='job_details'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('add_offer/', views.add_offer, name='add_offer'),
    path('account_settings/', views.account_settings, name='account_settings'),
    path('upload_cv', views.upload_cv, name='upload_cv'),
    path('change_password', views.change_password, name='change_password'),
    path('get_cv', views.get_cv, name='get_cv'),
    path('apply/<int:offerid>', views.apply, name='apply'),
    path('your_offers', views.your_offers, name='your_offers'),
    path('register', views.register, name='register'),
    path('request_company', views.request_company, name='request_company'),
    path('delete_offer/<int:offerid>', views.delete_offer, name='delete_offer'),
    path('activate_offer/<int:offerid>', views.activate_offer, name='activate_offer'),
    path('deactivate_offer/<int:offerid>', views.deactivate_offer, name='deactivate_offer'),
    path('edit_offer/<int:offerid>', views.edit_offer, name='edit_offer'),
    path('company_settings/', views.company_settings, name='company_settings'),
]
