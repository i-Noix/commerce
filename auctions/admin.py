from django.contrib import admin

from .models import AuctionListings, User, Category, Bids, Comments, Watchlist

# Register your models here.
admin.site.register(AuctionListings)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)
