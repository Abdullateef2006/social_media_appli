from django import forms
from .models import *

# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['content', 'media' , ]
        
        


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'comment-input',
                'placeholder': 'Write your comment here...',
            }),
        }
# forms.py
from django import forms
from .models import Reply

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'comment-input',
                'placeholder': 'Reply the  comment here...',
            }),
        }
