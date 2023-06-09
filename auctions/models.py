from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm
from datetime import datetime, time, date, timedelta, timezone
import re

class User(AbstractUser):
   pass
   
categories = [
    ('Gardening', 'Gardening'),
    ('Outdoors', 'Outdoors'),
    ('Sporting Goods', 'Sporting Goods'),
    ('Photography', 'Photography'),
    ('Visual Arts', 'Visual Arts'),
]

daysLive = [
    (3,'3 Days'),
    (5,'5 Days'),
    (7,'7 Days'),
    (10,'10 Days'),
]

class ListingTimes(models.Model):
	startDate = models.DateTimeField()
	endDate = models.DateTimeField()
	delta = models.DurationField()
	
	def __str__(self):
		if self.endDate > datetime.now(timezone.utc):
			delta = self.endDate - datetime.now(timezone.utc)
			return re.sub(".[0-9]{6}", " hours", str(delta))
		else:
			return "The auction has ended."

class Listing(models.Model):
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
	category = models.CharField(max_length=64, choices=categories)
	listingName = models.CharField(max_length=128)
	description = models.TextField(max_length=8192)
	imageLink = models.URLField(blank=True)
	startingBid = models.DecimalField(max_digits=11, decimal_places=2)
	isLiveTime = models.IntegerField(choices=daysLive)
	times = models.OneToOneField(ListingTimes, on_delete=models.CASCADE, related_name="articleDatesTimes") #OneToOne field, as ListingTimes is an extension of Listing
	
class IsLive(models.Model):
	article = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name = "articleIsLive")
	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellerLiveAuction")
	isLive = models.BooleanField()
	
class Watching(models.Model): # association table
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchers")
	article = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchedArticle")
	
class AcquiredArticle(models.Model):
	buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer")
	article = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="boughtArticle")

class ClosedAuction(models.Model):
	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellerClosedAuction")
	article = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="Auction")
	    
class Bid(models.Model):
	article = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidOnArticle")
	bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "bidders")
	bid = models.DecimalField(max_digits=11, decimal_places=2)

class AuctionComment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "commenter")
	article = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="commentedArticle")
	content = models.TextField(max_length=4096, blank=True)
	
	def __str__(self):
		return f"{self.user.username}wrote: {self.content}"