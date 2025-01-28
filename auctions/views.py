from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import AuctionListings, User, Category, Bids, Comments, Watchlist

class CreatePageForm(forms.Form):
    title = forms.CharField(
        max_length=64,
        label="Title for the auction listing:",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description of the auction listing:",
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    category = forms.CharField(
        max_length=64,
        label="Category:",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    start_bid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Initial bid:",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    image_url = forms.URLField(
        max_length=200,
        label="Url address of item auction listing:",
        widget=forms.URLInput(attrs={'class': 'form-control'}),
        required=False
    )

# Views all active auction in page active listing
def index(request):
    return render(request, "auctions/index.html", {
        "auctions": AuctionListings.objects.all()
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
            image_url = form.cleaned_data["image_url"]
            category_name = form.cleaned_data["category"]

            # Creating a new object to AuctionListings
            new_auction_listing = AuctionListings(
                title=title,
                description=description,
                start_bid=start_bid,
                image_url=image_url,
                author=request.user
            )
            
            # Save object to database AuctionListings
            new_auction_listing.save()

            # Creating or getting the Category object
            category, created = Category.objects.get_or_create(name=category_name)

            # Add the category to the auction listing
            new_auction_listing.categories.add(category)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CreatePageForm()
        return render(request, "auctions/create_listing.html", {
            "new_auction_form": form
        })

# Create feature add auction to page "Watchlist"


    
    
# def watchlist_page(request):
    


# Create page listing
def listing(request, auction_id):
    try:
        auction = AuctionListings.objects.get(pk=auction_id)
        return render(request, "auctions/listing.html", {
            "auction": auction
    })
    except AuctionListings.DoesNotExist:
        return render(request, "auctions/error.html", {
            "message": "Auction listing does not exist"
        })
