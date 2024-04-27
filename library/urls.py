from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_book, name='checkout_book'),
    path('return/', views.return_book, name='return_book'),
    path('reserve/', views.reserve_book, name='reserve_book'),
    path('fulfill/', views.fulfill_reservation, name='fulfill_reservation'),
]
