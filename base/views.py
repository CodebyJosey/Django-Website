from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Min, Max, Avg
from .models import Profile, Book, Read
from .forms import ReadForm, BookForm, ProfileForm
from django.db.models import Q

def index(request):
    return render(request, "base/index.html")

@login_required
def readform(request):
    book_id = request.GET.get("book")

    if request.method == "POST":
        form = ReadForm(request.POST)
        if form.is_valid():
            read = form.save(commit=False)
            read.user = request.user

            if Read.objects.filter(user=request.user, book=read.book, date=read.date).exists():
                messages.error(request, "Je hebt dit boek al gelezen op deze datum!")
                return redirect("ratings")

            read.save()
            messages.success(request, "Beoordeling succesvol toegevoegd")
            return redirect("ratings")
    else:
        initial_data = {}
        if book_id:
            initial_data["book"] = book_id
        form = ReadForm(initial=initial_data)

    context = {"form": form}

    return render(request, "base/add_form.html", context)


@staff_member_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)

        if "delete" in request.POST:
            book.delete()
            messages.success(request, "Boek verwijderd")
            return redirect("books")

        if form.is_valid():
            form.save()
            messages.success(request, "Boek succesvol aangepast")
            return redirect("books")
    else:
        form = BookForm(instance=book)

    context = {
        "form": form,
        "edit": True,
        "book": book,
    }
    return render(request, "base/edit_book.html", context)

@login_required
def bookform(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            if request.user.is_staff:
                book.approved = True
            book.user = request.user
            book.save()
            messages.success(request, "Boek succesvol toegevoegd")
            return redirect("books")
    else:
        form = BookForm()

    context = {"form": form, "user": request.user}
    return render(request, "base/add_form.html", context)

@staff_member_required
def unapproved_books(request):
    books = Book.objects.filter(approved=False)

    context = {"books": books}
    return render(request, "base/unapproved_books.html", context)

@staff_member_required
def approve_book(request, pk):
    book = Book.objects.get(pk=pk)
    book.approved = True
    book.approved_by = request.user
    book.save()
    messages.success(request, "Boek goedgekeurd")
    return redirect("unapproved_books")

@staff_member_required
def deny_book(request, pk):
    book = Book.objects.get(pk=pk)
    book.delete()
    messages.success(request, "Boek afgekeurd")
    return redirect("unapproved_books")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def books(request):
    books = Book.objects.filter(approved=True)

    context = {"books": books, "total": books.count()}
    return render(request, "base/approved_books.html", context)


@login_required
def specific_book(request, name: str):
    book = Book.objects.get(title=name)
    readings = Read.objects.filter(book=book)
    average_score = readings.aggregate(Avg('score'))['score__avg']
    
    if average_score:
        total_stars = []
        stars = average_score / 2
        for i in range(1, 6):
            if stars >= i:
                total_stars.append("full")
            elif stars >= i - 0.5:
                total_stars.append("half")
            else:
                total_stars.append("empty")

        context = {"book": book,
                'reads': readings.count(),
                'average': total_stars}
    else:
        context = {"book": book,
                'reads': readings.count()}

    return render(request, "base/specific_book.html", context)

@login_required
def ratings(request):
    all_ratings = Read.objects.select_related("book", "user").order_by("-date")

    for read in all_ratings:
        stars = []
        score = read.score / 2 
        for i in range(1, 6):
            if score >= i:
                stars.append("full")
            elif score >= i - 0.5:
                stars.append("half")
            else:
                stars.append("empty")
        read.star_images = stars

    context = {
        "ratings": all_ratings,
        "total": all_ratings.count(),
    }

    return render(request, "base/ratings.html", context)

@login_required
@staff_member_required
def delete_rating(request, rating_id):
    if request.method == 'POST':
        rating = Read.objects.filter(pk=rating_id)
        rating.delete()
    
    return redirect('ratings')

def edit_rating(request, rating_id):
    rating = get_object_or_404(Read, pk=rating_id)

    if request.method == "POST":
        form = ReadForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, "Beoordeling succesvol bewerkt")
            return redirect("user_profile")
    else:
        form = ReadForm(instance=rating)

    context = {"form": form, "edit": True}
    return render(request, "base/edit_rating.html", context)


def custom_404_view(request, exception):
    return render(request, "base/404.html", status=404)

@login_required
def view_profile(request, name: str):
    try:
        user = User.objects.get(username=name)
        profile = Profile.objects.get(user=user)
        all_ratings = Read.objects.select_related("book", "user").filter(user=user).order_by("-date")
    except:
        return redirect("ratings")

    for read in all_ratings:
        stars = []
        score = read.score / 2 
        for i in range(1, 6):
            if score >= i:
                stars.append("full")
            elif score >= i - 0.5:
                stars.append("half")
            else:
                stars.append("empty")
        read.star_images = stars

    context = {
        "profile": profile,
        "ratings": all_ratings,
        "total": all_ratings.count(),
        "edit": False
    }
    return render(request, "base/profile.html", context)
    
@login_required
def profile(request):
    all_ratings = Read.objects.select_related("book", "user").filter(user=request.user).order_by("-date")
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    for read in all_ratings:
        stars = []
        score = read.score / 2 
        for i in range(1, 6):
            if score >= i:
                stars.append("full")
            elif score >= i - 0.5:
                stars.append("half")
            else:
                stars.append("empty")
        read.star_images = stars

    context = {
        "profile": profile,
        "ratings": all_ratings,
        "total": all_ratings.count(),
        "edit": False
    }
    return render(request, "base/profile.html", context)

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profiel succesvol bewerkt")
            return redirect("user_profile")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "edit": True
    }
    return render(request, "base/profile.html", context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('user_profile')
    else:
        form = SetPasswordForm(user=request.user)
    return render(request, 'base/add_form.html', {'form': form})