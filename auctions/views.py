from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render	, redirect
from django.urls import reverse
from .forms import CreateForm, BidOnListing, PlaceComment, ChooseCategory
from .models import User, Listing, IsLive, AuctionComment, ListingTimes, Watching, Bid, AcquiredArticle, ClosedAuction
from . import models
from datetime import datetime, time, date, timedelta, timezone
import re

def index(request):
	return redirect("auctions:activeListings")
		
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:activeListings"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:activeListings"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:activeListings"))
    else:
        return render(request, "auctions/register.html")

def createListing(request):
	form = CreateForm(request.POST)
	print(f"form is valid?: {form.is_valid()}")
	if form.is_valid():
		thisForm = form.save(commit = False)
		
		# This is because the form gets sent by entering url (???).
		if thisForm.listingName == "" or thisForm.category is None: #of course there could be more conditions. I just took the first two fields; it works.
			return render(request, "auctions/createListing.html",{'form':form})
			
		# To convert the dates in the live listing to the timezone of the user, I guess you have to get the user's timezone from the front-end through JavaScript. So for now I just let the remaining delta show in article description.
		dateStartAuction = datetime.now(timezone.utc) #creates a universal date (UTC timezone) on the backend.
		thisForm.owner = request.user
		
		delta = timedelta(days=thisForm.isLiveTime)
		t = ListingTimes(delta = delta)
		t.startDate = dateStartAuction
		t.endDate = dateStartAuction + delta
		thisForm.times = t
		goLive = IsLive(article = thisForm, seller=request.user, isLive=True)

		t.save()
		thisForm.save()
		goLive.save()
			
		print(f"Name: {thisForm.listingName}\nCategory: {thisForm.category}\nDescription: {thisForm.description}")
		print(f"Is Live?: {goLive.isLive}\nLive Time: {thisForm.isLiveTime}\nStart: {t.startDate}\nEnd: {t.endDate}\nDuration: {t.delta}")
		print(f"Starting Bid: {thisForm.startingBid}")
		
	return redirect("auctions:activeListings")

def activeListings(request): #all listing on website
	hasEnded()
	allListings = IsLive.objects.filter(isLive = True)
	return listAuctions(request, allListings, "All Active Listings")
	
def watchlist(request):
	hasEnded()
	watchedListings = Watching.objects.filter(user = request.user)
	return listAuctions(request, watchedListings, "Your Watchlist")
	
def acquired(request):
	hasEnded()
	acquiredArticles = AcquiredArticle.objects.filter(buyer = request.user)
	return listAuctions(request, acquiredArticles, "Acquired Auctions")
	
def yourActiveAuctions(request):
	hasEnded()
	activeAuctions = IsLive.objects.filter(isLive=True, seller = request.user)
	return listAuctions(request, createdByThisUser, "Your Live Auctions")
	
def closedAuctions(request):
	hasEnded()
	auctionsOver = ClosedAuction.objects.filter(seller = request.user)
	return listAuctions(request, auctionsOver, "Your Closed Auctions")
	
def listAuctions(request, listOfAuctions, listPageName):
	chooseCategory = ChooseCategory(request.POST)
	if chooseCategory.is_valid():
		category = chooseCategory.cleaned_data["category"]
		if category != "All" and category != "": #similar to upper createListing, this is to prevent POST getting sent without information
			tempList = []
			for article in listOfAuctions:
				if article.article.category == category:
					tempList.append(article)
			listOfAuctions = tempList
	return render(request, "auctions/activeListings.html", {"allListings": listOfAuctions, "category":chooseCategory, "listPageName": listPageName})
	
def timeToString(endDate):
	delta = endDate - datetime.now(timezone.utc)
	return re.sub(".[0-9]{6}", "", str(delta)) # cuts off the microseconds
	
def hasEnded():
	allListings = IsLive.objects.filter(isLive = True)
	for isLiveObject in allListings:
		if str(isLiveObject.article.times) == "The auction has ended.":
			isLiveObject.isLive = False
			isLiveObject.save()
			
			closed = ClosedAuction(article=isLiveObject.article, seller=isLiveObject.article.owner)
			closed.save()
			
			try:
				isWatched = Watching.objects.get(article = isLiveObject.article)
				isWatched.delete()
			except (Watching.DoesNotExist, AttributeError):
				pass
			
			try:
				allBids = Bid.objects.filter(article=isLiveObject.article)
				highestBid = allBids.last()
				buyer = AcquiredArticle(article=isLiveObject.article, buyer = highestBid.bidder)
				buyer.save()
			except (Bid.DoesNotExist, AttributeError):
				pass
	
def article(request, article_id):
	article = Listing.objects.get(id=article_id)
	isWatched = False
	context = {}
	
	onItemList = []
	hasEnded() #Usually the check would happen before activeListings, but it's possible that after an auction has ended, the article page is called before a listing-list page.
	
	isClosed = None
	buyer = None
	try:
		isClosed = ClosedAuction.objects.get(article = article)
		try:
			isAcquired = AcquiredArticle.objects.get(article = article)
			buyer = isAcquired.buyer
		except (AcquiredArticle.DoesNotExist, AttributeError):
			pass
	except (ClosedAuction.DoesNotExist, AttributeError):
		pass
	
	highestBid = article.startingBid	
	amountOfBids = 0
	try:
		allBids = Bid.objects.filter(article=article)
		highestBid = allBids.last().bid
		amountOfBids = len(allBids)
	except (Bid.DoesNotExist, AttributeError):
		pass
	
	if isClosed is None and request.user.is_anonymous is not True:
		try:
			findIt = Watching.objects.get(user = request.user, article=article)
			isWatched = True
		except Watching.DoesNotExist:
			findIt = None
		
		if request.method=='POST' and 'onOffWatchlist' in request.POST:
			if isWatched:
				findIt.delete()
				messages.add_message(request, messages.INFO, 'Removed from Watchlist.')
				isWatched = False
			else:
				watchThis = Watching(user = request.user, article=article)
				watchThis.save()
				messages.add_message(request, messages.INFO, 'Added to Watchlist.')
				isWatched = True
				
		if request.method=='POST' and 'closeAuction' in request.POST:
			liveArticle = IsLive.objects.get(article=article)
			liveArticle.isLive = False
			liveArticle.save()
			allBids = Bid.objects.filter(article=article)
			buyer = allBids.last().bidder
			acquired = AcquiredArticle(article=article, user = buyer)
			acquired.save()
			closed = ClosedAuction(article=article, user = article.owner)
			closed.save()
			try:
				isWatched = Watching.objects.get(article = article)
				isWatched.delete()
			except (Watching.DoesNotExist, AttributeError):
				pass
			
		form = BidOnListing(request.POST)
		if request.method=='POST' and 'hitBidding' in request.POST:
			if form.is_valid():
				bidding = form.cleaned_data["bidding"]
				if bidding is not None and bidding >= highestBid+1:
					b = Bid(article=article, bidder=request.user, bid = bidding)
					b.save()
					allBids = Bid.objects.filter(article=article)
					highestBid = allBids.last().bid
					# why again calling from the model instead of just highestBid = b.bid?
					# because of formatting: If the user bids integers like 354 it will update the page to 354 when submitting the bid. But then, when refreshing the page (call from model) it turns to "354.00" as it's stored as decimals, which makes it an unsmooth experience.
					
					amountOfBids += 1
					
					messages.add_message(request, messages.INFO, 'You are the highest bidder. Good luck!')
				else:
					messages.add_message(request, messages.ERROR, 'Your bid must be at least 1€ above the current bidding.')
					
		commenting = PlaceComment(request.POST)
		if commenting.is_valid():
			comment = commenting.save(commit = False)
			if comment.content != "":
				comment.user = request.user
				comment.article = article
				comment.save()
		
		context['isWatched'] = isWatched
		context['form'] = form
		context['commenting'] = commenting
	
	comments = None
	try:
		comments = AuctionComment.objects.filter(article=article)
	except (AuctionComment.DoesNotExist, AttributeError):
		pass
		
	context['article'] = article
	context['currentBid'] = highestBid
	context['amountOfBids'] = amountOfBids
	context['isClosed'] = isClosed
	context['buyer'] = buyer
	context['comments'] = comments
	
	return render(request, "auctions/listing.html", context)

# FOR DEBUGGING (allows to quickly remove articles)
def delete(request, id):
  	member = Listing.objects.get(id=id)
  	member.delete()
  	return redirect('auctions:activeListings')