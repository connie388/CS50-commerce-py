from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="createlisting"),
    path("activelistings/<str:name>", views.active_listings, name="activelistings"),
    path("listingdetail/<int:listingid>", views.listingdetail, name="listingdetail"),
    path("watchlist", views.watch_list, name="watchlist"),
    path("listingwatch/<int:listingid>", views.listing_watch, name="listingwatch"),
    path("close_listing/<int:listingid>", views.close_listing, name="close_listing"),
    path("category/<str:name>", views.category, name="category"),
    path("categories", views.categories, name="categories"),
]
