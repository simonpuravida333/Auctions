from django import forms
from .models import Listing, Watching, AuctionComment
from django.forms import ModelForm, TextInput #, Textarea, URLInput
from django.utils.translation import gettext_lazy as _

class CreateForm(ModelForm):
	class Meta:
		model = Listing
	
		# fields = ['listingName','category','description','imageLink', 'startingBid'.....] or simply:
		fields = '__all__'
		exclude = {
			'owner',
			'times',
			'isLive',
		}
		widgets = {
			'category': forms.Select(attrs={'required': 'True'}),
			'listingName': forms.TextInput(attrs={'required': 'True'}),
			'description': forms.Textarea(attrs={'required': 'True'}),
			'startingBid': forms.NumberInput(attrs={'required': 'True', 'min': 1, 'class': 'formBottomSection','id':'leftBottomFeature'}),
			'isLiveTime': forms.Select(attrs={'required': 'True', 'class': 'formBottomSection','id':'centreBottomFeature'}),
			'isLive': forms.Select(attrs={'required': 'True', 'class': 'formBottomSection','id':'rightBottomFeature'}),
		}
		labels = {
			'listingName': _('Name of the Article'),
			'imageLink': _('URL Link for an Image (optional):'),
			#'startingBid': _('Starting Bid'),
			#'isLiveTime': _('For how many days will the article be live?'),
			'startingBid': _('Enter the desired starting bid and choose for how many days the auction will be public.'),
			'isLiveTime': _(''),
		}
	
	# this function removes the HTML UL errorlist message / label ("this field is required") from every field. Otherwise django plugs before every form feature that is not blank = true in models this message. It just looks bad and out of place. To still ensure required fields to be filled, upper the widgets list makes the fields required again, but in a more subtle way: a speech bubble pops up at the field required if the user wanted to submit without having filled out the field.
	def __init__(self, *args, **kwargs):
			super(CreateForm, self).__init__(*args, **kwargs)
			for field in self.fields.values():
				field.required = False
				
class PlaceComment(forms.Form):
	comment = forms.CharField(widget=forms.Textarea(attrs={"rows":"2"}), label="")
	def __init__(self, *args, **kwargs):
		super(PlaceComment, self).__init__(*args, **kwargs)
		self.fields['comment'].required = False

class BidOnListing(forms.Form):
	bidding = forms.DecimalField(max_digits=8, decimal_places=2, label="")
	def __init__(self, *args, **kwargs):
		super(BidOnListing, self).__init__(*args, **kwargs)
		self.fields['bidding'].required = False


categories = [
	('All','All'),
    ('Gardening', 'Gardening'),
    ('Outdoors', 'Outdoors'),
    ('Sporting Goods', 'Sporting Goods'),
    ('Photography', 'Photography'),
    ('Visual Arts', 'Visual Arts'),
]		
		
class ChooseCategory(forms.Form):
	category = forms.ChoiceField(choices = categories,widget=forms.Select(attrs={'onchange': 'submit();'}))
	def __init__(self, *args, **kwargs):
		super(ChooseCategory, self).__init__(*args, **kwargs)
		self.fields['category'].required = False
		self.fields['category'].label = ""