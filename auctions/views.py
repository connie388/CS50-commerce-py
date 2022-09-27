from django.contrib.auth import authenticate, login, logout
from django.db import DatabaseError, IntegrityError
from django.db.models import Count, Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from auctions.forms import (
    ListingForm,
    ActiveListingForm,
    BidForm,
    CommentForListingForm,
)
from .models import AuctionListing, User, Bid
from auctions.models import AuctionListing, Category, CommentForListing, User


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
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
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
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def index(request):
    try:
        auctionlist = AuctionListing.objects.filter(is_active=True)
    except AuctionListing.DoesNotExist:
        return render(request, "auctions/errormsg.html", status=404)
    form = ActiveListingForm(request)
    return render(
        request,
        "auctions/index.html",
        {"auctionlist": auctionlist, "title": "Active Listing"},
    )


def active_listings(request, name):
    try:
        category_instance = Category.objects.get(category_name=name)
    except Category.DoesNotExist:
        render(request, "auctions/errormsg.htm", status=404)

    auctionlist = AuctionListing.objects.filter(
        category=category_instance, is_active=True
    ).all()

    return render(
        request,
        "auctions/index.html",
        {"auctionlist": auctionlist, "title": "Active Listing By Category: " + name},
    )


@login_required
def watch_list(request):
    return render(
        request,
        "auctions/index.html",
        {"auctionlist": request.user.watchlist.all(), "title": "Watchlist"},
    )


def category(request, name):
    try:
        category = Category.objects.get(category_name=name)
    except Category.DoesNotExist:
        return render(request, "auctions/errormsg.html", status=404)
    list = AuctionListing.objects.filter(category=category, is_active=True)
    return render(
        request,
        "auctions/index.html",
        {"auctionlist": list, "title": "Active Listing By Category: " + name},
    )


def categories(request):
    return render(
        request, "auctions/categories.html", {"categories": Category.objects.all()}
    )


@login_required
def create_listing(request):
    # If this is a POST request then process the Form data
    if request.method == "POST":

        # Create a form instance and populate it with data from the request (binding):
        form = ListingForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            listing_instance = AuctionListing()
            listing_instance.listing_name = form.cleaned_data["listing_name"]
            listing_instance.description = form.cleaned_data["description"]
            listing_instance.starting_bid = form.cleaned_data["starting_bid"]
            listing_instance.listing_image_url = form.cleaned_data["listing_image_url"]
            listing_instance.category = form.cleaned_data["category"]
            listing_instance.user_created = request.user
            listing_instance.save()
            messages.add_message(
                request,
                messages.INFO,
                "listing saved!",
            )
            # redirect to a new URL:
        return render(request, "auctions/createlisting.html", {"form": form})

    # If this is a GET (or any other method) create the default form.
    else:
        form = ListingForm()
        return render(request, "auctions/createlisting.html", {"form": form})


def listingdetail(request, listingid):
    try:
        listing_instance = AuctionListing.objects.get(id=listingid)
    except AuctionListing.DoesNotExist:
        render(request, "auctions/errormsg.html", status=404)

    if request.method == "POST":
        if "placebid" in request.POST:
            save_bid(request, listing_instance)
        elif "addcomment" in request.POST:
            save_comment(request, listing_instance)
        return HttpResponseRedirect(
            reverse("listingdetail", kwargs={"listingid": listingid})
        )
    else:
        if (
            request.user.id == listing_instance.currentbidby()
            and listing_instance.is_active is False
        ):
            messages.add_message(
                request,
                messages.INFO,
                "You won the bid of this listing!",
            )
        return render(
            request,
            "auctions/listingdetail.html",
            {
                "listing": listing_instance,
                "commentlist": CommentForListing.objects.filter(
                    listing=listing_instance
                ).all(),
            },
        )


@require_POST
@login_required
def save_comment(request, listing):
    if listing.is_active is False:
        messages.add_message(
            request,
            messages.ERROR,
            "This is an inactive listing!",
        )
        return
    form = CommentForListingForm(request.POST)
    if form.is_valid():
        comment = CommentForListing()
        comment.comment = form.cleaned_data["comment"]
        comment.listing = listing
        comment.person_posted = request.user
        comment.save()
        messages.add_message(request, messages.SUCCESS, "Comment saved!")
    return


@require_POST
@login_required
def save_bid(request, listing):
    if listing.is_active is False:
        messages.add_message(
            request,
            messages.ERROR,
            "This is an inactive listing!",
        )
        return

    form = BidForm(request.POST)
    if form.is_valid():
        bid_input = form.cleaned_data["bid"]

        if not (
            (listing.bid_count() > 0 and float(bid_input) > listing.price())
            or (listing.bid_count() == 0 and float(bid_input) >= listing.starting_bid)
        ):
            messages.add_message(
                request,
                messages.ERROR,
                "Bid must be greater than highest bid price or equal to starting bid!",
            )

            return

        bid_instance = Bid()
        bid_instance.bid_price = float(bid_input)
        bid_instance.person_bid = request.user
        bid_instance.listing = listing
        bid_instance.save()
        messages.add_message(request, messages.SUCCESS, "Bid saved!")
    return


@login_required
def listing_watch(request, listingid):
    try:
        listing_instance = AuctionListing.objects.get(id=listingid)
    except AuctionListing.DoesNotExist:
        render(request, "auctions/errormsg.html", status=404)

    watchlist = request.user.watchlist
    try:
        if listing_instance in watchlist.all():
            watchlist.remove(listing_instance)
        else:
            watchlist.add(listing_instance)
    except DatabaseError:
        messages.add_message(request, messages.ERROR, "Action failed for watchlist!")
        return HttpResponseRedirect(
            reverse("listingdetail", kwargs={"listingid": listingid})
        )

    messages.add_message(request, messages.ERROR, "Action success for watchlist!")
    return HttpResponseRedirect(
        reverse("listingdetail", kwargs={"listingid": listingid})
    )


@require_POST
@login_required
def close_listing(request, listingid):
    print("test")
    try:
        listing_instance = AuctionListing.objects.get(id=listingid)
    except AuctionListing.DoesNotExist:
        render(request, "auctions/errormsg.html", status=404)
    if request.user == listing_instance.user_created:
        try:
            listing_instance.is_active = False
            listing_instance.save()
        except DatabaseError:
            messages.add_message(request, messages.ERROR, "Close failed!")
    else:
        messages.add_message(
            request, messages.ERROR, "You are not the person create this listing!"
        )
    return HttpResponseRedirect(
        reverse("listingdetail", kwargs={"listingid": listingid})
    )
