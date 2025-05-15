from django import forms
from .models import Profile, Read, Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ("title", "author", "genre", "number_of_pages")
        labels = {
            'title': 'Titel',
            'author': 'Auteur',
            'genre': 'Genre',
            'number_of_pages': 'Aantal Pagina\'s',
        }


class ReadForm(forms.ModelForm):
    class Meta:
        model = Read
        fields = ("book", "date", "score")
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                    }),
        }
        labels = {
            'book': 'Boek',
            'date': 'Datum',
            'score': 'Score',
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("biotext", "city", "date_of_birth")
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                    }),
        }
        labels = {
            'biotext': 'Bio',
            'city': 'Woonplaats',
            'date_of_birth': 'Geboortedatum',
        }
