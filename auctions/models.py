from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class AuctionListings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(max_digits=10, decimal_places=2)
    categories = models.ManyToManyField(Category, related_name="auctions")
    image_url = models.URLField(max_length=200, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    date_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

class Bids(models.Model):
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid of {self.bid_amount} on {self.auction.title} by {self.bidder.username}"

class Comments(models.Model):
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.auction.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction = models.ForeignKey(AuctionListings, on_delete=models.CASCADE, related_name="watchlist")
    added_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s watchlist item: {self.auction.title}"