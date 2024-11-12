from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.http import HttpResponseForbidden

@login_required(login_url='login')
def user_list(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'user_list.html', {'users': users})


@login_required(login_url='login')
def room(request, room_name):
    # Ensure room_name consistency by sorting the usernames alphabetically
    usernames = sorted(room_name.split('_'))
    if len(usernames) != 2 or request.user.username not in usernames:
        return HttpResponseForbidden("You are not authorized to join this chat.")

    room_name = '_'.join(usernames)
    messages = Message.objects.filter(room_name=room_name).order_by('timestamp')
    return render(request, 'room.html', {
        'room_name': room_name,
        'messages': messages,
        'username': request.user.username,
    })
    
    
# yourapp/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


    

# yourapp/views.py
@login_required(login_url='login')
def groupchat(request, room_name):
    group = get_object_or_404(ChatGroup, name=room_name)

    # Check if the user is a member of the group
    if request.user not in group.members.all():
        messages.error(request, "You are not a member of this group.")
        return redirect('group_list')

    # Pass the group and its members to the template
    return render(request, 'chat.html', {
        'room_name': room_name,
        'username': request.user.username,
        'members': group.members.all(),  # Pass the members to the template
    })



# yourapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatGroup
from .forms import ChatGroupForm

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            messages.success(request, f"Group '{group.name}' created successfully!")
            return redirect('chat:group_list')  # Redirect to a list of all groups or group details
    else:
        form = ChatGroupForm()

    return render(request, 'create_group.html', {'form': form})

# yourapp/views.py (add this in the same file)
@login_required(login_url='login')
def delete_group(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)

    # Only the creator can delete the group
    if group.creator != request.user:
        messages.error(request, "You do not have permission to delete this group.")
        return redirect('chat:group_list')  # Redirect to the list of groups

    if request.method == 'POST':
        group.delete()
        messages.success(request, f"Group '{group.name}' deleted successfully!")
        return redirect('chat:group_list')  # Redirect to the group list after deletion

    return render(request, 'delete_group.html', {'group': group})


# yourapp/views.py (add this in the same file)
@login_required(login_url='login')
def group_list(request):
    groups = ChatGroup.objects.all()
    return render(request, 'group_list.html', {'groups': groups})





# yourapp/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import ChatGroup

@login_required(login_url='login')
def join_group(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)

    # Add the user to the group if they are not already a member
    if request.user not in group.members.all():
        group.members.add(request.user)
        group.save()
        messages.success(request, f"You have joined the group '{group.name}'!")
    else:
        messages.info(request, f"You are already a member of '{group.name}'.")

    return redirect('chat:group_list')

@login_required(login_url='login')

def leave_group(request, group_id):
    group = get_object_or_404(ChatGroup, id= group_id)
    if request.user in group.members.all():
        group.members.remove(request.user)
        group.save()
        messages.success(request, f"you have successfully left '{group.name}")
    else:
        messages.info(request, f"You are already removed from '{group.name}'.")
    return redirect('chat:group_list')

        
    
