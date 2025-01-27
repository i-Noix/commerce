from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=255)
    start_bid = models.IntegerField()
    category = models.CharField(max_length=64)
    image_url = models.URLField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    