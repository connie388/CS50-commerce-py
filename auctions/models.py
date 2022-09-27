from tkinter import CASCADE
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        help_text=_("Required. 20 characters or fewer."),
        error_messages={
            "unique": _("This category name already exists."),
        },
    )

    def __str__(self):
        return self.category_name


class AuctionListing(models.Model):
    id = models.BigAutoField(primary_key=True)
    listing_name = models.CharField(
        max_length=150,
        unique=True,
        help_text=_("Required. 150 characters or fewer."),
        error_messages={
            "unique": _("A listing with that name already exists."),
        },
    )
    description = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        help_text=_("Required. 150 characters or fewer."),
    )
    starting_bid = models.FloatField(null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this listing should be treated as active. "),
    )
    date_created = models.DateTimeField(_("date created"), default=timezone.now)
    user_created = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_image_url = models.URLField(
        max_length=250,
        null=True,
        blank=True,
        help_text=_("Required. 250 characters or fewer."),
    )
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def bid_count(self):
        return self.bids.all().count()

    def price(self):
        if self.bid_count() > 0:
            return self.bids.first().bid_price
        else:
            return self.starting_bid

    def currentbidby(self):
        if self.bid_count() > 0:
            return self.bids.first().person_bid.id
        else:
            return float("-inf")

    def __str__(self):
        return self.listing_name


class Bid(models.Model):
    id = models.BigAutoField(primary_key=True)
    person_bid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids"
    )
    bid_price = models.FloatField(blank=False, null=False)
    date_created = models.DateTimeField(_("date created"), default=timezone.now)

    class Meta:
        ordering = ("-bid_price",)


class CommentForListing(models.Model):
    id = models.BigAutoField(primary_key=True)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, blank=False)
    date_created = models.DateTimeField(_("date created"), default=timezone.now)
    person_posted = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-date_created",)
