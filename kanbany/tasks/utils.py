from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_task_notification(task, notification_type):
    """
    Send email notifications about task updates.
    notification_type can be: 'assigned', 'status_update', 'completed'
    """
    subject_templates = {
        'assigned': f'New Task Assignment: {task.title}',
        'status_update': f'Task Status Update: {task.title}',
        'completed': f'Task Completed: {task.title}'
    }

    context = {
        'task': task,
        'notification_type': notification_type,
    }

    html_content = render_to_string('tasks/email/task_notification.html', context)
    
    recipients = [task.assigned_to.email] if task.assigned_to else []
    if task.created_by.email:
        recipients.append(task.created_by.email)

    if recipients:
        send_mail(
            subject=subject_templates.get(notification_type, 'Task Update'),
            message='',
            html_message=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=True
        )
