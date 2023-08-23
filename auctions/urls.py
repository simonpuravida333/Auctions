from django.urls import path
from . import views

app_name = 'auctions'

urlpatterns = [
	path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.createListing, name="createListing"),
    path("activeListings/", views.activeListings, name="activeListings"),
    path("activeListings/delete/<int:id>", views.delete, name="delete"), #DEBUG
    path("article/<int:article_id>", views.article, name="article"),
    path("article/<int:article_id>/removeComment/<int:id>", views.removeComment, name="removeComment"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("activeBiddings/", views.yourActiveBiddings, name="activeBiddings"),
    path("acquiredArticles/", views.acquired, name="acquired"),
    path("activeAuctions", views.yourActiveAuctions, name="activeAuctions"),
    path("closedAuctions/", views.closedAuctions, name="sold"),
]
