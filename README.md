# 🌐 SocialSphere - Complete Social Media Platform Documentation

A comprehensive **Django-based social media platform** with **real-time chat**, **advanced search**, and **interactive community features**.

---

## 🌟 Core Features

### 🔐 Authentication & User Management
- User Registration & Login with email and username  
- Profile Management with bio, contact info, and profile pictures  
- Secure Session Management with login required decorators  
- User Follow System with follower/following counts  

### 📱 Content Management
- Multi-media Posts (text, images, files)  
- Multiple Image Uploads per post with `PostImage` model  
- Tagging System using **Django Taggit** for content categorization  
- Content Organization with creation timestamps  

### 💬 Social Interaction
- Like/Unlike System with AJAX & real-time updates  
- Commenting System with nested replies functionality  
- Follow/Unfollow with mutual following tracking  
- Post Saving for bookmarking content  

### 🔍 Advanced Search & Discovery
- **Fuzzy Search** using FuzzyWuzzy (intelligent matching)  
- Search History with tracking & timestamps  
- Tag-based Discovery (browse posts by hashtags)  
- User & Content Search across platform  
- Smart Suggestions with **60%+ similarity threshold**  

### 🔔 Real-time Notifications
- WebSocket-powered live notifications  
- Notification Types:  
  - Likes on posts  
  - New comments & replies  
  - Follow/unfollow actions  
- Notification Center with read/unread status  

### 💬 Real-time Chat System
- Private Messaging between users  
- Group Chat functionality with room management  
- File Sharing in chat (base64 encoding)  
- Online User Tracking with real-time updates  
- Message Persistence with database storage  

### 🏷️ Community Features
- Chat Groups with creator/member roles  
- Group Management – create, join, leave groups  
- Room-based Chat with sorted usernames for consistency  
- Real-time Member Updates  

---

## 🛠️ Technology Stack

**Backend Framework**
- Django – Web framework  
- Django Channels – WebSocket support  
- ASGI – Asynchronous server support  
- Redis – Channel layer for real-time communication  

**Database & Models**
- PostgreSQL / SQLite – Database management  
- Django ORM – Database operations  
- Taggit – Flexible tagging system  
- Many-to-Many Relationships for social features  

**Real-time Features**
- WebSocket Consumers for chat & notifications  
- Channel Layers for message broadcasting  
- Async/Await for concurrency  
- Online User Tracking with sets  

**Search & AI**
- FuzzyWuzzy – Intelligent string matching  
- Levenshtein Distance – Similarity scoring  
- Q Objects – Complex database queries  

**File Management**
- Pillow – Image processing  
- Multi-file Upload support  
- Base64 Encoding – Secure file transfers  

---

## 🏗️ Project Structure

### Models Architecture
**Core Models**
- `User` – Django’s built-in User model  
- `Profile` – Extended user info (bio, followers, etc.)  
- `Post` – User-generated posts  
- `PostImage` – Multiple images per post  
- `Comment & Reply` – Nested commenting  

**Social Models**
- `Notifications` – Real-time alerts  
- `savedPosts` – Bookmarking system  
- `SearchHistory` – Track searches  

**Chat Models**
- `Message` – Chat persistence  
- `ChatGroup` – Group chat management  

---

### Views Architecture
**Authentication**
- `user_register()` – New user registration  
- `user_login()` – Login handler  
- `user_logout()` – Secure logout  

**Content**
- `posts()` – Main feed (shuffled posts)  
- `create_post()` – Upload multi-media posts  
- `post_detail()` – Post with comments & replies  

**Social**
- `like_post()` – AJAX like/unlike  
- `follow_user()` – Follow/unfollow logic  
- `saved_posts_list()` – Saved posts  

**Search**
- `search_term()` – Fuzzy search across content/users  
- `history_list()` – Manage search history  
- `posts_by_tag()` – Filter posts by tags  

**Chat**
- `user_list()` – Available users for chat  
- `room()` – Private chat room  
- `groupchat()` – Group chat interface  
- `create_group()` – Group creation & management  

---

### Real-time Components
**WebSocket Consumers**
- `NotificationConsumer` – Notifications  
- `ChatConsumer` – Private chat  
- `GroupChatConsumer` – Group chat  

**Channel Layer Features**
- User status tracking  
- Message broadcasting  
- File sharing (base64)  
- Online user updates  

---

## 🛣️ URL Endpoints

### Authentication & Profiles
- `/register/` – User registration  
- `/login/` – Login  
- `/logout/` – Logout  
- `/profile/` – Current user profile  
- `/profile/<id>/` – Other profiles  

### Content Management
- `/posts/` – Main feed  
- `/create_post/` – Post creation  
- `/post/<id>/` – Post details  
- `/saved_posts/` – Bookmarks  

### Social
- `/like/<id>/` – Like/unlike post  
- `/follow/<user_id>/` – Follow user  
- `/saved_posts/<id>/` – Save post  

### Search
- `/search/` – Advanced search  
- `/history/` – Search history  
- `/tag/<tag_name>/` – Tag posts  
- `/clear_history/` – Clear history  

### Chat
- `/chat/users/` – Available users  
- `/chat/room/<room_name>/` – Private chat  
- `/chat/group/<room_name>/` – Group chat  
- `/chat/groups/` – Group list  
- `/chat/create_group/` – New group  

### Notifications
- `/notifications/` – Notification center  
- **WebSocket**: `/ws/notifications/` – Real-time alerts  

---

## ⚙️ Installation Guide

Follow these steps to set up and run the **SocialSphere** project locally.

---

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/socialsphere.git
cd socialsphere
python -m venv env
source env/bin/activate
env\Scripts\activate for windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver



