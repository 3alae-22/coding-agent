from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Todo


def _get_stats(todos):
    total = todos.count()
    completed = todos.filter(completed=True).count()
    pending = total - completed
    overdue = sum(1 for t in todos.filter(completed=False) if t.is_overdue)
    return {'total': total, 'completed': completed, 'pending': pending, 'overdue': overdue}


def home(request):
    filter_by = request.GET.get('filter', 'all')
    priority_filter = request.GET.get('priority', 'all')

    todos = Todo.objects.all()

    # Status filter
    if filter_by == 'active':
        todos = todos.filter(completed=False)
    elif filter_by == 'completed':
        todos = todos.filter(completed=True)
    elif filter_by == 'overdue':
        today = timezone.now().date()
        todos = todos.filter(completed=False, due_date__lt=today)

    # Priority filter
    if priority_filter in ('low', 'medium', 'high'):
        todos = todos.filter(priority=priority_filter)

    # Annotate overdue flag for display (avoid repeated DB hits)
    today = timezone.now().date()
    todo_list = []
    for todo in todos:
        todo.overdue = todo.due_date and not todo.completed and todo.due_date < today
        todo_list.append(todo)

    # Sort: pending first (by priority order then due_date), completed last
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    todo_list.sort(key=lambda t: (
        t.completed,
        priority_order.get(t.priority, 1),
        t.due_date or timezone.datetime.max.date(),
    ))

    stats = _get_stats(Todo.objects.all())

    context = {
        'todos': todo_list,
        'filter_by': filter_by,
        'priority_filter': priority_filter,
        'stats': stats,
        'today': today,
    }
    return render(request, 'home.html', context)


def add_todo(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', Todo.PRIORITY_MEDIUM)
        due_date = request.POST.get('due_date') or None

        if not title:
            messages.error(request, '⚠️ Title is required.')
            return redirect('home')

        Todo.objects.create(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        messages.success(request, f'✅ "{title}" added successfully!')
    return redirect('home')


def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    status = 'completed ✅' if todo.completed else 'marked as pending 🔄'
    messages.success(request, f'"{todo.title}" {status}')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def edit_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', Todo.PRIORITY_MEDIUM)
        due_date = request.POST.get('due_date') or None

        if not title:
            messages.error(request, '⚠️ Title is required.')
            return render(request, 'edit_todo.html', {'todo': todo})

        todo.title = title
        todo.description = description
        todo.priority = priority
        todo.due_date = due_date
        todo.save()
        messages.success(request, f'✏️ "{todo.title}" updated successfully!')
        return redirect('home')

    return render(request, 'edit_todo.html', {'todo': todo})


def delete_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        title = todo.title
        todo.delete()
        messages.success(request, f'🗑️ "{title}" deleted.')
    return redirect('home')


def delete_completed(request):
    if request.method == 'POST':
        count, _ = Todo.objects.filter(completed=True).delete()
        messages.success(request, f'🗑️ {count} completed task(s) cleared.')
    return redirect('home')
