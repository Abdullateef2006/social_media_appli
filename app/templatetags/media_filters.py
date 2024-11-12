from django import template

register = template.Library()

@register.filter
def is_image(media_url):
    return media_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

@register.filter
def is_video(media_url):
    return media_url.lower().endswith(('.mp4', '.webm', '.ogg'))
