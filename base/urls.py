from django.urls import path, include
from django.conf.urls import handler404
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('logout', views.logout_user, name="logout_user"),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name="register"),
    #path("book/<str:title>/", views.book, name="book"),
    path("books/", views.books, name="books"),
    path("bookform/", views.bookform, name="bookform"),
    path("bookform/<int:pk>/", views.edit_book, name="edit_book"),
    path("readform/", views.readform, name="readform"),
    path("unapproved_reads/", views.unapproved_books, name="unapproved_books"),
    path("approve_book/<int:pk>/", views.approve_book, name="approve_book"),
    path("deny_book/<int:pk>/", views.deny_book, name="deny_book"),
    path("books/<str:name>/", views.specific_book, name="book"),
    path("ratings/", views.ratings, name="ratings"),
    path("edit_rating/<int:rating_id>/", views.edit_rating, name="edit_rating"),
    path("delete_rating/<int:rating_id>/", views.delete_rating, name="delete_rating"),
    path("profile/", views.profile, name="user_profile"),
    path("profile/edit", views.edit_profile, name="edit_profile"),
    path("profile/<str:name>/", views.view_profile, name="profile"),
    path("change_password/", views.change_password, name="change_password")
]

handler404 = views.custom_404_view