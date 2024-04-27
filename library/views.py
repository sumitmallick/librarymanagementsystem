from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Book, Member, Circulation, Reservation
from .serializers import BookSerializer, MemberSerializer, CirculationSerializer, ReservationSerializer


@api_view(['POST'])
@method_decorator(cache_page(60*15))
def checkout_book(request: HttpRequest):
    if request.method == 'POST':
        book_id = request.data.get('book_id')
        member_id = request.data.get('member_id')
        
        try:
            book = Book.objects.get(id=book_id)
            if book.copies_available > 0:
                # Create Circulation record
                circulation = Circulation.objects.create(
                    book=book,
                    member_id=member_id,
                    event_type='checkout'
                )
                
                # Decrement available copies
                book.copies_available -= 1
                book.save()
                cache.delete(f'book_cache_{book_id}')
                book.save()
                cache.set(f'book_cache_{book_id}', book_id, timeout=3000)
                serializer = BookSerializer(book)

                return Response({'data': serializer.data,'message': 'Book checked out successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No copies of the book available'}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@method_decorator(cache_page(60*15))
def return_book(request: HttpRequest):
    if request.method == 'POST':
        book_id = request.data.get('book_id')
        member_id = request.data.get('member_id')
        
        try:
            book = Book.objects.get(id=book_id)
            # Find circulation record for the book and member
            circulation = Circulation.objects.get(book=book, member_id=member_id, event_type='checkout')
            
            # Delete circulation record
            circulation.delete()
            cache.delete(f'circulation_{book_id}')
            
            # Increment available copies
            book.copies_available += 1
            cache.delete(f'book_cache_{book_id}')
            book.save()
            cache.set(f'book_cache_{book_id}', book_id, timeout=3000)
            serializer = BookSerializer(book)

            return Response({'data': BookSerializer.data, 'message': 'Book returned successfully'}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Circulation.DoesNotExist:
            return Response({'message': 'Book not checked out by the member'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@method_decorator(cache_page(60*15))
def reserve_book(request: HttpRequest):
    if request.method == 'POST':
        book_id = request.data.get('book_id')
        member_id = request.data.get('member_id')
        
        try:
            book = Book.objects.get(id=book_id)
            serializer = BookSerializer(book)
            if book.copies_available == 0:
                # Create Reservation record
                reservation = Reservation.objects.create(
                    book=book,
                    member_id=member_id,
                    fulfilled=False
                )
                cache.delete('reservation_cache')
                serializer = ReservationSerializer(reservation)
                return Response({'data': serializer.data, 'message': 'Book reserved successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'data': serializer.data, 'message': 'Copies of the book available. No need to reserve.'}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@method_decorator(cache_page(60*15))
def fulfill_reservation(request: HttpRequest):
    if request.method == 'POST':
        book_id = request.data.get('book_id')
        
        try:
            book_cache = cache.get(f'book_cache_{book_id}')
            if book_cache:
                book = Book(**book_cache)
            else:
                book = Book.objects.get(id=book_id)
            
            # Find and process reservation records for the book
            reservation_cache = cache.get(f'reservation_cache_{book_id}')
            if reservation_cache:
                reservations = Book(**reservation_cache)
            else:
                reservations = Reservation.objects.filter(book=book, fulfilled=False)
            serializer = ReservationSerializer(reservations, many=True)
            for reservation in reservations:
                # Set reservation as fulfilled
                reservation.fulfilled = True
                reservation.save()
                cache.delete(f'reservation_cache_{book_id}')

                # Decrement available copies
                book.copies_available -= 1
                cache.delete(f'book_cache_{book_id}')
                book.save()
                cache.set(f'book_cache_{book_id}', book_id, timeout=3000)
                serializer = BookSerializer(reservations)
            return Response({'data': serializer.data, 'message': 'Reservation fulfilled successfully'}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({'data': serializer.data, 'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
