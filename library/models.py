from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    author = models.CharField(max_length=100)
    copies_available = models.IntegerField(default=0)
# Create your models here.

class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=10, unique=True, db_index=True)


class Circulation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_index=True)
    event_type = models.CharField(max_length=20)
    event_date = models.DateTimeField(auto_now_add=True)


class Reservation(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, db_index=True)
    fulfilled = models.BooleanField(default=False)

