"""
URL configuration for contacts app
"""

from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Public endpoints
    path('inquiry/', views.ContactInquiryCreateView.as_view(), name='contact_inquiry_create'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('newsletter/unsubscribe/', views.NewsletterUnsubscribeView.as_view(), name='newsletter_unsubscribe'),
    
    # Admin endpoints
    path('inquiries/', views.ContactInquiryListView.as_view(), name='contact_inquiry_list'),
    path('inquiries/<uuid:pk>/', views.ContactInquiryDetailView.as_view(), name='contact_inquiry_detail'),
    path('inquiries/bulk-update/', views.bulk_update_inquiries, name='bulk_update_inquiries'),
    
    # Response management
    path('responses/', views.InquiryResponseCreateView.as_view(), name='inquiry_response_create'),
    
    # Analytics and reporting
    path('analytics/', views.contact_analytics, name='contact_analytics'),
    
    # Contact lists and templates
    path('lists/', views.ContactListView.as_view(), name='contact_list'),
    path('templates/', views.EmailTemplateView.as_view(), name='email_template'),
]