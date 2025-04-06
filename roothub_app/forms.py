from django import forms
from .models import Announcement

class SendAnnouncement(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'description', 'file')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-group local-forms col-12 col-sm-4'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'description': 'Write your Announcement here',
        }