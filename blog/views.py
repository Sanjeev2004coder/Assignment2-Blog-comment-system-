from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404
from .models import Post, Comment
import json

@csrf_exempt
@require_POST
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
            
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        return JsonResponse({'message': 'User created successfully', 'user_id': user.id}, status=201)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def user_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
@require_POST
def create_post(request):
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        
        if not all([title, content]):
            return JsonResponse({'error': 'Title and content are required'}, status=400)
            
        post = Post.objects.create(
            author=request.user,
            title=title,
            content=content
        )
        return JsonResponse({
            'message': 'Post created successfully',
            'post_id': post.id,
            'title': post.title,
            'author': post.author.username,
            'created_at': post.created_at
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_GET
def list_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'author': post.author.username,
            'created_at': post.created_at,
            'comment_count': post.comments.count()
        })
    return JsonResponse({'posts': posts_data}, safe=False)

@require_GET
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created_at')
    
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'text': comment.text,
            'user': comment.user.username,
            'created_at': comment.created_at
        })
    
    post_data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'created_at': post.created_at,
        'comments': comments_data
    }
    return JsonResponse(post_data)

@csrf_exempt
@login_required
@require_POST
def add_comment(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        data = json.loads(request.body)
        text = data.get('text')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
            
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )
        return JsonResponse({
            'message': 'Comment added successfully',
            'comment_id': comment.id,
            'text': comment.text,
            'user': comment.user.username,
            'created_at': comment.created_at
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)