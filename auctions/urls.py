from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
	path("", views.index, name="index"),
	path("auction/", views.index, name="index"),
	path("auctions/", views.index, name="index"),
    path("auctions/index/", views.index, name="index"),
    path("auctions/login/", views.login_view, name="login"),
    path("auctions/logout/", views.logout_view, name="logout"),
    path("auctions/register/", views.register, name="register"),
    path("auctions/create/", views.createListing, name="createListing"),
    path("auctions/activeListings/", views.activeListings, name="activeListings"),
    path("auctions/activeListings/delete/<int:id>", views.delete, name="delete"), #DEBUG
    path("auctions/article/<int:article_id>", views.article, name="article"),
    path("auctions/article/<int:article_id>/removeComment/<int:id>", views.removeComment, name="removeComment"),
    path("auctions/watchlist/", views.watchlist, name="watchlist"),
    path("auctions/activeBiddings/", views.yourActiveBiddings, name="activeBiddings"),
    path("auctions/acquiredArticles/", views.acquired, name="acquired"),
    path("auctions/activeAuctions/", views.yourActiveAuctions, name="activeAuctions"),
    path("auctions/closedAuctions/", views.closedAuctions, name="sold"),
]
