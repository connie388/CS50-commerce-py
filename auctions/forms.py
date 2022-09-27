from django import forms
from django.forms import ModelForm
from auctions.models import (
    AuctionListing,
    Bid,
    Category,
    CommentForListing,
    User,
)

# Form to view Auction listing
class ActiveListingForm(forms.ModelForm):
    disabled_fields = (
        "listing_name",
        "description",
        # "price",
        "listing_image_url",
    )

    class Meta:
        model = AuctionListing
        fields = [
            "listing_name",
            "description",
            # "price",
            "listing_image_url",
        ]


# Form to input Auction listing
class ListingForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = AuctionListing
        fields = [
            "listing_name",
            "description",
            "starting_bid",
            "category",
            "listing_image_url",
        ]


class BidForm(forms.Form):
    bid = forms.DecimalField(required=True)


class CommentForListingForm(forms.ModelForm):
    class Meta:
        model = CommentForListing
        fields = ["comment"]
