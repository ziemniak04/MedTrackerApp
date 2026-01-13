import datetime, os
from django.utils import timezone
from .models import Note
from .models import Medicament


def last_notes_for_med(med_id:int, limit=10):
    notes = Note.objects.filter(medication_id=med_id).order_by('-created_at')
    result=[]
    for n in notes[:limit]:
        if n.text != None:
            result.append(n.text)
    return result


def days_since(date):
    now = timezone.now()
    delta = now.date() - date
    return delta.days
