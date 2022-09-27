from django.contrib import admin
from .models import Category, AuctionListing, Bid, CommentForListing


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name",)


admin.site.register(Category, CategoryAdmin)


class ListingAdmin(admin.ModelAdmin):
    list_display = ("listing_name", "description")


admin.site.register(AuctionListing, ListingAdmin)


class BidAdmin(admin.ModelAdmin):
    list_display = ("person_bid", "date_created", "listing", "bid_price")


admin.site.register(Bid, BidAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("person_posted", "listing", "comment", "date_created")


admin.site.register(CommentForListing, CommentAdmin)
