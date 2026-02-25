from django import forms
from .models import Announcement, Courses

class SendAnnouncement(forms.ModelForm):
    target_courses = forms.ModelMultipleChoiceField(
        queryset=Courses.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'course-checkbox'}),
        required=False,
        help_text="Select specific courses (optional)"
    )
    
    class Meta:
        model = Announcement
        fields = ('title', 'description', 'priority', 'target_trainers', 'target_trainees', 
                 'target_admins', 'target_courses', 'file', 'scheduled_for', 'expires_at')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter announcement title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Write your announcement message here...'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'target_trainers': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_trainees': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'target_admins': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'scheduled_for': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
        }
        labels = {
            'description': 'Announcement Message',
            'target_trainers': 'Send to Trainers',
            'target_trainees': 'Send to Trainees', 
            'target_admins': 'Send to Admins',
            'target_courses': 'Target Specific Courses',
            'scheduled_for': 'Schedule for Later (Optional)',
            'expires_at': 'Expiry Date (Optional)',
        }