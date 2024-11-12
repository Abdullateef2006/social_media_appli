
from django import forms
from .models import ChatGroup

class ChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['name']
        labels = {
            'name': 'Group Name'
        }

