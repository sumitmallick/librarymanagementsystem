from rest_framework import serializers
from .models import Book, Member, Circulation, Reservation


class BookSerializer(serializers.Serializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'copies_available']


class MemberSerializer(serializers.Serializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'email', 'phone']


class CirculationSerializer(serializers.Serializer):
    class Meta:
        model = Circulation
        fields = ['title', 'copies_available', 'event_type', 'event_date']


class ReservationSerializer(serializers.Serializer):
    class Meta:
        model  = Circulation
        fields = ['book', 'member', 'fulfilled']
