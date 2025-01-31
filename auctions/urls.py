from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:auction_id>", views.listing, name="listing"),
    path("listing/<int:auction_id>/add_to_watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("listing/<int:auction_id>/remove_from_watchlist", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("watchlist_page", views.watchlist_page, name="watchlist_page"),
    path("listing/<int:auction_id>/bids", views.bids, name="bids"),
    path("listing/<int:auction_id>/close_auction", views.close_auction, name="close_auction")
]
