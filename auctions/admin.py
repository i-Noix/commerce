from django.contrib import admin

from .models import AuctionListings, User, Category, Bids, Comments, Watchlist

class AuctionListingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_time', 'author', 'is_active')

class BidsAdmin(admin.ModelAdmin):
    list_display = ('bid_amount', 'bidder', 'bid_time', 'auction__title')

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('author', 'comment', 'comment_time', 'auction__title')
    search_fields = ('comment', 'auction__title')
    list_per_page = 20

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'is_staff')
    list_per_page = 20

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'auction__title', 'auction__author')

# Register your models here.
admin.site.register(AuctionListings, AuctionListingsAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Watchlist, WatchlistAdmin)
