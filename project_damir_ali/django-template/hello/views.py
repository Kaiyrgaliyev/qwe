from django.utils.timezone import datetime
from django.shortcuts import render, redirect
from hello.forms import LogMessageForm
from hello.models import LogMessage
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from .models import ChatMessage
from django.contrib.auth.models import User

@login_required
def chat(request):
    """Отображает чат пользователя."""
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        content = request.POST.get('content')
        try:
            recipient = User.objects.get(username=recipient_username)
            ChatMessage.objects.create(sender=request.user, recipient=recipient, content=content)
        except User.DoesNotExist:
            return render(request, 'hello/chat.html', {'error': 'Recipient does not exist.'})

    messages = ChatMessage.objects.filter(recipient=request.user) | ChatMessage.objects.filter(sender=request.user)
    messages = messages.order_by('-timestamp')
    return render(request, 'hello/chat.html', {'messages': messages})

@login_required
def user_profile(request):
    """Отображает личный кабинет пользователя."""
    user_messages = LogMessage.objects.filter(user=request.user)  # Сообщения текущего пользователя
    return render(request, 'hello/user_profile.html', {'user_messages': user_messages})

class HomeListView(ListView):
    """Renders the home page, with a list of all messages."""
    model = LogMessage
    queryset = LogMessage.objects.order_by("-log_date")[:5]  # Ограничиваем до 5 последних сообщений
    context_object_name = "message_list"
    template_name = "hello/home.html"


def about(request):
    """Renders the about page."""
    return render(request, "hello/about.html")


def log_message(request):
    """Handles the log message form."""
    form = LogMessageForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.log_date = datetime.now()
            message.save()
            return redirect("home")
    return render(request, "hello/log_message.html", {"form": form})


def log_message_list(request):
    """Displays a list of all log messages with search functionality."""
    query = request.GET.get('q', '')  # Получаем поисковый запрос из параметров URL
    if query:
        messages = LogMessage.objects.filter(message__icontains=query)  # Фильтрация по тексту
    else:
        messages = LogMessage.objects.all()
    return render(request, 'hello/log_message_list.html', {'messages': messages, 'query': query})


def log_message_create(request):
    """Creates a new log message."""
    if request.method == 'POST':
        form = LogMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('log_message_list')
    else:
        form = LogMessageForm()
    return render(request, 'hello/log_message_create.html', {'form': form})