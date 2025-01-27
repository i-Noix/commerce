from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, AuctionListings

class CreatePageForm(forms.Form):
    title = forms.CharField(
        max_length=64,
        label="Title for the auction listing",
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    description = forms.CharField(
        max_length=255,
        label="Description of the auction listing",
        widget=forms.Textarea(attrs={'class': 'form-control'})
        )
    start_bid = forms.IntegerField(
        label="Initial bid",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
        )
    category = forms.CharField(
        max_length=64,
        label="Category",
        widget=forms.TextInput(attrs={'class': 'form-control'})
        )
    image_url = forms.URLField(
        max_length=200,
        label="Url address of item auction listing",
        widget=forms.URLInput(attrs={'class': 'form-control'})
        )

# Views all active auction in page active listing
def index(request):
    active_auctions = AuctionListings.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": active_auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Create page: Çreate Listing
def create_listing(request):
    if request.method == "POST":
        form = CreatePageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            start_bid = form.cleaned_data["start_bid"]
            category = form.cleaned_data["category"]
            image_url = form.cleaned_data["image_url"]

            # Creating a new object to AuctionListings
            new_auction_listing = AuctionListings(
                title=title,
                description=description,
                start_bid=start_bid,
                category=category,
                image_url=image_url,
                author=request.user
            )

            # Save object to database AuctionListings
            new_auction_listing.save()
            return HttpResponseRedirect(reverse("index"))

    new_auction_form = CreatePageForm()
    return render(request, "auctions/create_listing.html", {
        "new_auction_form": new_auction_form
    })

# Create page "Watchlist"



# Create page listing
def listing(request, title):
    auction_listing = AuctionListings.objects.get(title=title)
    return render(request, "auctions/listing.html", {
        "auction_listing": auction_listing
    })
