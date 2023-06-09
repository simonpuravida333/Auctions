from django.contrib import admin
from .models import User, Listing, AuctionComment

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(AuctionComment)
# Register your models here.
