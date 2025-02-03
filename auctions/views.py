from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django import forms
from django.views.decorators.http import require_POST


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
    existing_category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Category (choose from existing):",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    new_category = forms.CharField(
        max_length=64,
        label="or add a new category:",
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
    auctions = AuctionListings.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "auctions": auctions
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
            existing_category = form.cleaned_data["existing_category"]
            new_category = form.cleaned_data["new_category"]

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

            # Define the category
            if new_category:
                # Creating or get the new category 
                category, created = Category.objects.get_or_create(name=new_category)
            else:
                category = existing_category

            # Add the category to the auction listing
            if category:
                new_auction_listing.categories.add(category)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = CreatePageForm()
        return render(request, "auctions/create_listing.html", {
            "new_auction_form": form
        })

# Create feature add auction to page "Watchlist"
def add_to_watchlist(request, auction_id):
    if request.method == "POST":
        # Check if auction exist in the AuctionListings
        auction = get_object_or_404(AuctionListings, pk=auction_id)
        
        # Add auction to Watchlist
        add_auction = Watchlist(
            user = request.user,
            auction = auction
        )
        # Save auction
        add_auction.save()
        return HttpResponseRedirect(reverse("listing", args=[auction_id]))

# Create feature to remove auction from the page "Watchlist"
def remove_from_watchlist(request, auction_id):
    if request.method == "POST":
        # Check if auction exist in the Watchlist
        auction = get_object_or_404(AuctionListings, pk=auction_id)

        # Remove auction from Watchlist
        Watchlist.objects.filter(user=request.user, auction=auction).delete()
        return HttpResponseRedirect(reverse("listing", args=[auction_id]))
    
# Create page watchlist
def watchlist_page(request):
    user_watchlist = Watchlist.objects.filter(user=request.user)
    auction_ids_from_watchlist = AuctionListings.objects.filter(id__in=user_watchlist.values_list('auction', flat=True))
    return render(request, "auctions/watchlist_page.html", {
        "watchlist": auction_ids_from_watchlist
    })

# Create page listing
def listing(request, auction_id):
    # Take auction from AucionListings
    auction = get_object_or_404(AuctionListings, pk=auction_id)

    # Take object from Bids that has highest bid_amount for this auction
    highest_bid = auction.bids.all().order_by('-bid_amount').first()

    # Take all comments for this auction
    comments = auction.comments.all()

    # if user is authenticated take user watchlist
    if request.user.is_authenticated:
        user_watchlist = Watchlist.objects.filter(user=request.user)
        auction_ids_from_watchlist = user_watchlist.values_list('auction__id', flat=True)
        if highest_bid and request.user == highest_bid.bidder:
            winner = True
            winner_message = f"Conglaturation! Your has won this auction with bid ${highest_bid.bid_amount}"
        else:
            winner = False
            winner_message = None

        return render(request, "auctions/listing.html", {
            "auction": auction,
            "watchlist": auction_ids_from_watchlist,
            "current_bid": highest_bid,
            "success_message": request.session.pop('success_message', None),
            "error_message": request.session.pop('error_message', None),
            "winner_message": winner_message,
            "winner": winner,
            "comments": comments
        })
    
    else:
        return render(request, "auctions/listing.html", {
            "auction": auction,
            "current_bid": highest_bid,
        })

# Feature bid on listing page
@require_POST
def bids(request, auction_id):
    # Take bid that user input
    bid = float(request.POST["bid"])

    # Take auction for this bid
    auction = get_object_or_404(AuctionListings, pk=auction_id)

    # Take all bids of that auction in Bids
    bids_for_auction = auction.bids.all()

    # Take only bid from Queryset and max bid
    only_bids = bids_for_auction.values_list("bid_amount", flat=True)
    max_bid=max(only_bids, default=0)

    # Check if bid >= start bid and > highest bid_amount
    if bid >= auction.start_bid and bid > max_bid:
        # Add bid to Bids
        new_bid = Bids (
            auction = auction,
            bidder = request.user,
            bid_amount = bid
        )
        # Save new bid
        new_bid.save()
        request.session['success_message'] = "Your bid was succeful!"
    else:
        request.session['error_message'] = "Your bid must be higher than current highest bid and the starting bid."
    
    return redirect("listing", auction_id)
    
# Feature for close an auction
@require_POST
def close_auction(request, auction_id):
    # Take auction from AuctionListing or views 404
    auction = get_object_or_404(AuctionListings, pk=auction_id)

    # Change value auction.is_active to False
    auction.is_active = not auction.is_active
    auction.save()
    return redirect('listing', auction_id)

# Feature for add comment
@require_POST
def add_comment(request, auction_id):
    # Take auction from AuctionListing
    auction = get_object_or_404(AuctionListings, pk=auction_id)

    # Creating a new object and adding it to Comments
    new_comment = Comments (
        auction = auction,
        comment = request.POST.get("comment"), 
        author=request.user
        )

    # Save new_comment and save message for user in session
    new_comment.save()
    request.session["add_message"] = "Your comment has been added!"

    # Redirect user to the page listing
    return redirect('listing', auction_id)

# Page Categories
def categories_page(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories_page.html", {
        "categories": categories
    })

# Page Category
def category(request, category_id):
    # Take category from Category
    category = get_object_or_404(Category, pk=category_id)

    # Take all auctions in this category
    auctions = category.auctions.all()

    return render(request, 'auctions/category.html', {
        "category": category,
        "auctions": auctions
    })

def closed_auctions_page(request):
    closed_auctions = AuctionListings.objects.filter(is_active=False)
    winner_list = []
    for auction in closed_auctions:
        # Take the winner of auction use the related name from Bids
        winner_bid = auction.bids.all().order_by('-bid_amount').first()
        winner_list.append(winner_bid)
    return render(request, "auctions/closed_auctions_page.html", {
        "closed_auctions": closed_auctions,
        "winner_list": winner_list
    })
        