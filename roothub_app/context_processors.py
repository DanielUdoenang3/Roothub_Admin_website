from datetime import datetime
from .models import Announcement


def current_year(request):
    return {'current_year': datetime.now().year}

def announcements_processor(request):
    announcements = Announcement.objects.all()
    return {"announcements": announcements}