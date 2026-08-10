# ==================== manage.py ====================
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_manager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()


# ==================== client_manager/__init__.py ====================
from .celery import app as celery_app

__all__ = ('celery_app',)


# ==================== client_manager/settings.py ====================
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'django_filters',
    'import_export',
    'corsheaders',
    'celery',
    'django_celery_beat',

    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'client_manager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notifications_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'client_manager.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'client_manager'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CORS_ALLOW_ALL_ORIGINS = bool(DEBUG)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}


# ==================== client_manager/urls.py ====================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import CustomLoginView, register
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ==================== client_manager/wsgi.py ====================
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_manager.settings')
application = get_wsgi_application()


# ==================== client_manager/asgi.py ====================
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_manager.settings')
application = get_asgi_application()


# ==================== client_manager/celery.py ====================
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_manager.settings')

app = Celery('client_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# ==================== core/__init__.py ====================
# Пустой файл


# ==================== core/models.py ====================
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta, date


class Client(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'Высокий'),
        ('medium', 'Средний'),
        ('low', 'Низкий'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('pending', 'В ожидании'),
        ('archived', 'В архиве'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client_profile',
        null=True,
        blank=True
    )
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    date_of_birth = models.DateField('Дата рождения', null=True, blank=True)
    address = models.TextField('Адрес', blank=True)

    priority = models.CharField('Приоритет', max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_clients'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    notes = models.TextField('Заметки', blank=True)
    tags = models.JSONField('Теги', default=list, blank=True)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-priority', 'last_name']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def get_progress_summary(self):
        progress_records = self.progress_records.all()
        if not progress_records:
            return None

        latest = progress_records.latest('date')
        return {
            'latest': latest,
            'total': progress_records.count(),
            'last_week': progress_records.filter(date__gte=timezone.now() - timedelta(days=7)).count(),
        }

    def get_wellness_trend(self):
        records = self.wellness_records.order_by('-date')[:7]
        if records:
            avg_wellness = sum(r.wellness_level for r in records) / len(records)
            return round(avg_wellness, 1)
        return None


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)
    color = models.CharField('Цвет', max_length=7, default='#007bff')
    icon = models.CharField('Иконка', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
        (4, 'Критический'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
        ('overdue', 'Просрочена'),
    ]

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    priority = models.IntegerField('Приоритет', choices=PRIORITY_CHOICES, default=2)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')

    due_date = models.DateTimeField('Срок выполнения')
    start_date = models.DateTimeField('Дата начала', null=True, blank=True)
    completed_at = models.DateTimeField('Дата завершения', null=True, blank=True)

    estimated_hours = models.DecimalField('Планируемое время (часы)', max_digits=5, decimal_places=1, default=1.0)
    actual_hours = models.DecimalField('Фактическое время (часы)', max_digits=5, decimal_places=1, default=0.0)

    is_recurring = models.BooleanField('Повторяющаяся', default=False)
    recurrence_rule = models.JSONField('Правила повторения', default=dict, blank=True)

    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    tags = models.JSONField('Теги', default=list, blank=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-priority', 'due_date']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False

    @property
    def days_until_due(self):
        delta = self.due_date - timezone.now()
        return delta.days

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    @staticmethod
    def get_overdue_tasks():
        return Task.objects.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        )

    def get_priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, '')


class WellnessRecord(models.Model):
    MOOD_CHOICES = [
        (1, 'Очень плохое'),
        (2, 'Плохое'),
        (3, 'Нейтральное'),
        (4, 'Хорошее'),
        (5, 'Отличное'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='wellness_records')
    date = models.DateTimeField('Дата записи', default=timezone.now)

    wellness_level = models.IntegerField(
        'Уровень самочувствия',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )

    mood = models.IntegerField('Настроение', choices=MOOD_CHOICES, default=3)
    energy_level = models.IntegerField(
        'Уровень энергии',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    sleep_quality = models.IntegerField(
        'Качество сна',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )
    stress_level = models.IntegerField(
        'Уровень стресса',
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=5
    )

    physical_activity = models.IntegerField(
        'Физическая активность (мин/день)',
        default=0
    )
    water_intake = models.IntegerField(
        'Потребление воды (мл)',
        default=0
    )
    medication_taken = models.BooleanField('Прием лекарств', default=False)

    symptoms = models.JSONField('Симптомы', default=list, blank=True)
    notes = models.TextField('Заметки', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись самочувствия'
        verbose_name_plural = 'Записи самочувствия'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['client', 'date']),
        ]

    def __str__(self):
        return f"{self.client} - {self.date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def overall_health_score(self):
        return round((self.wellness_level + self.energy_level + (10 - self.stress_level) + self.sleep_quality) / 4, 1)


class ProgressRecord(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='progress_records')
    date = models.DateTimeField('Дата записи', default=timezone.now)

    metric_1 = models.FloatField('Метрика 1', default=0)
    metric_2 = models.FloatField('Метрика 2', default=0)
    metric_3 = models.FloatField('Метрика 3', default=0)
    metric_4 = models.FloatField('Метрика 4', default=0)
    metric_5 = models.FloatField('Метрика 5', default=0)

    custom_metrics = models.JSONField('Пользовательские метрики', default=dict, blank=True)

    progress_percentage = models.IntegerField(
        'Процент прогресса',
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )

    notes = models.TextField('Заметки', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись прогресса'
        verbose_name_plural = 'Записи прогресса'
        ordering = ['-date']
        indexes = [
            models.Index(fields=['client', 'date']),
        ]

    def __str__(self):
        return f"{self.client} - {self.date.strftime('%Y-%m-%d')} - {self.progress_percentage}%"


class ClientGoal(models.Model):
    GOAL_STATUS_CHOICES = [
        ('not_started', 'Не начата'),
        ('in_progress', 'В процессе'),
        ('achieved', 'Достигнута'),
        ('abandoned', 'Отменена'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField('Название цели', max_length=200)
    description = models.TextField('Описание', blank=True)

    target_date = models.DateField('Целевая дата')
    achieved_date = models.DateField('Дата достижения', null=True, blank=True)

    status = models.CharField('Статус', max_length=20, choices=GOAL_STATUS_CHOICES, default='not_started')
    progress = models.IntegerField('Прогресс %', default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    milestones = models.JSONField('Вехи', default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Цель клиента'
        verbose_name_plural = 'Цели клиентов'
        ordering = ['-progress', 'target_date']

    def __str__(self):
        return f"{self.client} - {self.title}"

    def is_on_track(self):
        if self.status == 'achieved':
            return True
        days_total = (self.target_date - self.created_at.date()).days
        if days_total <= 0:
            return False
        days_elapsed = (date.today() - self.created_at.date()).days
        expected_progress = min(100, (days_elapsed / days_total) * 100)
        return self.progress >= expected_progress


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('task_due', 'Срок задачи'),
        ('task_overdue', 'Просрочка задачи'),
        ('wellness_alert', 'Тревога по самочувствию'),
        ('goal_milestone', 'Веха цели'),
        ('system', 'Системное уведомление'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField('Заголовок', max_length=200)
    message = models.TextField('Сообщение')
    notification_type = models.CharField('Тип', max_length=20, choices=NOTIFICATION_TYPES)

    is_read = models.BooleanField('Прочитано', default=False)
    read_at = models.DateTimeField('Дата прочтения', null=True, blank=True)

    link = models.CharField('Ссылка', max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])


# ==================== core/admin.py ====================
from django.contrib import admin
from .models import (
    Client, Task, WellnessRecord, ProgressRecord,
    ClientGoal, Category, Notification
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'priority', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'first_name', 'last_name', 'middle_name', 'phone', 'email')
        }),
        ('Дополнительная информация', {
            'fields': ('date_of_birth', 'address', 'priority', 'status')
        }),
        ('Назначения', {
            'fields': ('assigned_to', 'notes', 'tags')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'priority', 'due_date', 'assigned_to']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['title', 'description', 'client__first_name', 'client__last_name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        for task in queryset:
            task.mark_completed()
        self.message_user(request, f'{queryset.count()} задач отмечены как выполненные')
    mark_completed.short_description = 'Отметить выбранные задачи как выполненные'


@admin.register(WellnessRecord)
class WellnessRecordAdmin(admin.ModelAdmin):
    list_display = ['client', 'date', 'wellness_level', 'mood', 'energy_level', 'stress_level']
    list_filter = ['date', 'mood', 'medication_taken']
    search_fields = ['client__first_name', 'client__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProgressRecord)
class ProgressRecordAdmin(admin.ModelAdmin):
    list_display = ['client', 'date', 'progress_percentage', 'metric_1', 'metric_2']
    list_filter = ['date', 'progress_percentage']
    search_fields = ['client__first_name', 'client__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ClientGoal)
class ClientGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'progress', 'target_date']
    list_filter = ['status', 'target_date']
    search_fields = ['title', 'client__first_name', 'client__last_name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color']
    search_fields = ['name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message']
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        for notification in queryset:
            notification.mark_as_read()
        self.message_user(request, f'{queryset.count()} уведомлений отмечены как прочитанные')
    mark_as_read.short_description = 'Отметить выбранные уведомления как прочитанные'


# ==================== core/forms.py ====================
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .models import (
    Client, Task, WellnessRecord, ProgressRecord,
    ClientGoal, Category, Notification
)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name', 'last_name', 'middle_name',
            'phone', 'email', 'date_of_birth', 'address',
            'priority', 'status', 'assigned_to', 'notes', 'tags'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'Теги через запятую'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        if len(cleaned_phone) < 10:
            raise forms.ValidationError('Номер телефона должен содержать минимум 10 цифр')
        return phone

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if isinstance(tags, str):
            return [t.strip() for t in tags.split(',') if t.strip()]
        return tags


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'client', 'category',
            'priority', 'status', 'due_date', 'start_date',
            'estimated_hours', 'assigned_to', 'tags', 'is_recurring'
        ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Теги через запятую'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = Client.objects.filter(status='active')

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise forms.ValidationError('Срок выполнения не может быть в прошлом')
        return due_date

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if isinstance(tags, str):
            return [t.strip() for t in tags.split(',') if t.strip()]
        return tags


class WellnessRecordForm(forms.ModelForm):
    class Meta:
        model = WellnessRecord
        fields = [
            'client', 'wellness_level', 'mood', 'energy_level',
            'sleep_quality', 'stress_level', 'physical_activity',
            'water_intake', 'medication_taken', 'symptoms', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'symptoms': forms.TextInput(attrs={'placeholder': 'Симптомы через запятую'}),
        }

    def clean_symptoms(self):
        symptoms = self.cleaned_data.get('symptoms')
        if isinstance(symptoms, str):
            return [s.strip() for s in symptoms.split(',') if s.strip()]
        return symptoms


class ProgressRecordForm(forms.ModelForm):
    class Meta:
        model = ProgressRecord
        fields = [
            'client', 'metric_1', 'metric_2', 'metric_3',
            'metric_4', 'metric_5', 'progress_percentage', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ClientGoalForm(forms.ModelForm):
    class Meta:
        model = ClientGoal
        fields = [
            'client', 'title', 'description', 'target_date',
            'status', 'progress', 'milestones'
        ]
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'milestones': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Вехи в формате JSON'}),
        }


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Обязательное поле. 150 символов или менее. Только буквы, цифры и @/./+/-/_.'
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email


class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', 'Все')] + list(Task.STATUS_CHOICES), required=False)
    priority = forms.ChoiceField(choices=[('', 'Все')] + list(Task.PRIORITY_CHOICES), required=False)
    client = forms.ModelChoiceField(queryset=Client.objects.all(), required=False, empty_label='Все клиенты')
    due_date_from = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    due_date_to = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )


# ==================== core/views.py ====================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import logging

from .models import (
    Client, Task, WellnessRecord, ProgressRecord,
    ClientGoal, Notification, Category
)
from .forms import (
    ClientForm, TaskForm, WellnessRecordForm,
    ProgressRecordForm, ClientGoalForm,
    CustomUserCreationForm, TaskFilterForm
)
from .utils import (
    generate_wellness_chart_data,
    generate_progress_chart_data,
    get_priority_score,
    check_overdue_tasks,
    check_upcoming_tasks
)

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Client.objects.create(
                user=user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone='',
                status='active'
            )
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    clients = Client.objects.filter(assigned_to=request.user)
    if not clients.exists():
        clients = Client.objects.all()

    total_clients = clients.count()
    active_clients = clients.filter(status='active').count()

    tasks = Task.objects.filter(assigned_to=request.user)
    pending_tasks = tasks.filter(status='pending').count()
    overdue_tasks = tasks.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    ).count()
    completed_tasks = tasks.filter(
        status='completed',
        completed_at__gte=timezone.now() - timedelta(days=7)
    ).count()

    today = timezone.now().date()
    wellness_today = WellnessRecord.objects.filter(
        client__in=clients,
        date__date=today
    ).aggregate(
        avg_wellness=Avg('wellness_level'),
        avg_energy=Avg('energy_level'),
        avg_stress=Avg('stress_level')
    )

    recent_progress = ProgressRecord.objects.filter(
        client__in=clients
    ).order_by('-date')[:10]

    recent_tasks = tasks.select_related('client').order_by('-created_at')[:5]

    active_goals = ClientGoal.objects.filter(
        client__in=clients,
        status__in=['not_started', 'in_progress']
    ).select_related('client')[:5]

    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    last_week = timezone.now() - timedelta(days=7)
    wellness_trend = WellnessRecord.objects.filter(
        client__in=clients,
        date__gte=last_week
    ).values('date__date').annotate(
        avg_wellness=Avg('wellness_level')
    ).order_by('date__date')

    progress_trend = ProgressRecord.objects.filter(
        client__in=clients,
        date__gte=last_week
    ).values('date__date').annotate(
        avg_progress=Avg('progress_percentage')
    ).order_by('date__date')

    context = {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'completed_tasks': completed_tasks,
        'wellness_today': wellness_today,
        'recent_progress': recent_progress,
        'recent_tasks': recent_tasks,
        'active_goals': active_goals,
        'notifications': notifications,
        'wellness_trend': list(wellness_trend),
        'progress_trend': list(progress_trend),
    }

    return render(request, 'dashboard.html', context)


@login_required
def client_list(request):
    clients = Client.objects.all().select_related('assigned_to')

    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')

    if status_filter:
        clients = clients.filter(status=status_filter)
    if priority_filter:
        clients = clients.filter(priority=priority_filter)
    if search_query:
        clients = clients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    paginator = Paginator(clients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
    }
    return render(request, 'client_list.html', context)


@login_required
def client_detail(request, client_id):
    client = get_object_or_404(Client.objects.select_related('assigned_to'), id=client_id)

    tasks = client.tasks.select_related('category', 'assigned_to').order_by('-priority', 'due_date')
    wellness_records = client.wellness_records.all().order_by('-date')[:30]
    progress_records = client.progress_records.all().order_by('-date')[:30]
    goals = client.goals.all()

    latest_wellness = wellness_records.first()
    latest_progress = progress_records.first()

    stats = {
        'total_tasks': tasks.count(),
        'completed_tasks': tasks.filter(status='completed').count(),
        'overdue_tasks': tasks.filter(
            status__in=['pending', 'in_progress'],
            due_date__lt=timezone.now()
        ).count(),
        'avg_wellness': wellness_records.aggregate(Avg('wellness_level'))['wellness_level__avg'],
        'avg_progress': progress_records.aggregate(Avg('progress_percentage'))['progress_percentage__avg'],
    }

    wellness_data = list(wellness_records.values('date', 'wellness_level', 'mood', 'energy_level', 'stress_level')[:14])
    progress_data = list(progress_records.values('date', 'progress_percentage')[:14])

    priority_score = get_priority_score(client)

    context = {
        'client': client,
        'tasks': tasks[:10],
        'wellness_records': wellness_records[:10],
        'progress_records': progress_records[:10],
        'goals': goals,
        'latest_wellness': latest_wellness,
        'latest_progress': latest_progress,
        'stats': stats,
        'wellness_data': wellness_data,
        'progress_data': progress_data,
        'priority_score': priority_score,
    }
    return render(request, 'client_detail.html', context)


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.assigned_to = request.user
            client.save()
            messages.success(request, f'Клиент {client.full_name} успешно создан!')
            return redirect('client_detail', client_id=client.id)
    else:
        form = ClientForm()

    return render(request, 'client_form.html', {'form': form, 'title': 'Создание клиента'})


@login_required
def client_edit(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Клиент {client.full_name} успешно обновлен!')
            return redirect('client_detail', client_id=client.id)
    else:
        form = ClientForm(instance=client)

    return render(request, 'client_form.html', {'form': form, 'title': 'Редактирование клиента'})


@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user).select_related('client', 'category')

    form = TaskFilterForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data.get('status'):
            tasks = tasks.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('priority'):
            tasks = tasks.filter(priority=form.cleaned_data['priority'])
        if form.cleaned_data.get('client'):
            tasks = tasks.filter(client=form.cleaned_data['client'])
        if form.cleaned_data.get('due_date_from'):
            tasks = tasks.filter(due_date__date__gte=form.cleaned_data['due_date_from'])
        if form.cleaned_data.get('due_date_to'):
            tasks = tasks.filter(due_date__date__lte=form.cleaned_data['due_date_to'])

    paginator = Paginator(tasks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            if not task.assigned_to:
                task.assigned_to = request.user
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('task_list')
    else:
        form = TaskForm(initial={'assigned_to': request.user})

    return render(request, 'task_form.html', {'form': form, 'title': 'Создание задачи'})


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача успешно обновлена!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {'form': form, 'title': 'Редактирование задачи'})


@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.mark_completed()
    messages.success(request, 'Задача отмечена как выполненная!')
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


@login_required
def wellness_tracker(request):
    clients = Client.objects.filter(assigned_to=request.user)
    selected_client_id = request.GET.get('client')

    if selected_client_id:
        client = get_object_or_404(Client, id=selected_client_id)
        records = client.wellness_records.all().order_by('-date')
    else:
        records = WellnessRecord.objects.filter(client__in=clients).order_by('-date')
        client = None

    stats = records.aggregate(
        avg_wellness=Avg('wellness_level'),
        avg_energy=Avg('energy_level'),
        avg_sleep=Avg('sleep_quality'),
        avg_stress=Avg('stress_level'),
    )

    recent_records = records[:10]
    chart_data = list(records.values('date', 'wellness_level', 'mood', 'energy_level', 'stress_level')[:30])

    context = {
        'clients': clients,
        'selected_client': client,
        'records': recent_records,
        'stats': stats,
        'chart_data': chart_data,
    }
    return render(request, 'wellness_tracker.html', context)


@login_required
def wellness_add(request):
    if request.method == 'POST':
        form = WellnessRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Запись самочувствия добавлена!')

            if record.wellness_level <= 3 or record.stress_level >= 8:
                Notification.objects.create(
                    user=request.user,
                    title='⚠️ Тревожный сигнал самочувствия',
                    message=f'У клиента {record.client.full_name} низкий уровень самочувствия ({record.wellness_level}/10) или высокий уровень стресса ({record.stress_level}/10)',
                    notification_type='wellness_alert',
                    link=f'/clients/{record.client.id}/'
                )

            return redirect('wellness_tracker')
    else:
        form = WellnessRecordForm(initial={'date': timezone.now()})
        if request.GET.get('client'):
            form.fields['client'].initial = request.GET.get('client')

    return render(request, 'wellness_form.html', {'form': form, 'title': 'Добавление записи самочувствия'})


@login_required
def progress_tracker(request):
    clients = Client.objects.filter(assigned_to=request.user)
    selected_client_id = request.GET.get('client')

    if selected_client_id:
        client = get_object_or_404(Client, id=selected_client_id)
        records = client.progress_records.all().order_by('-date')
    else:
        records = ProgressRecord.objects.filter(client__in=clients).order_by('-date')
        client = None

    stats = records.aggregate(
        avg_progress=Avg('progress_percentage'),
        max_progress=Max('progress_percentage'),
        min_progress=Min('progress_percentage'),
        count=Count('id'),
    )

    goals = client.goals.all() if client else []
    chart_data = list(records.values('date', 'progress_percentage')[:30])

    context = {
        'clients': clients,
        'selected_client': client,
        'records': records[:10],
        'stats': stats,
        'goals': goals,
        'chart_data': chart_data,
    }
    return render(request, 'progress_tracker.html', context)


@login_required
def progress_add(request):
    if request.method == 'POST':
        form = ProgressRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Запись прогресса добавлена!')

            if record.progress_percentage >= 100:
                Notification.objects.create(
                    user=request.user,
                    title='🎉 Прогресс достиг 100%!',
                    message=f'Клиент {record.client.full_name} достиг 100% прогресса!',
                    notification_type='goal_milestone',
                    link=f'/clients/{record.client.id}/'
                )

            return redirect('progress_tracker')
    else:
        form = ProgressRecordForm(initial={'date': timezone.now()})
        if request.GET.get('client'):
            form.fields['client'].initial = request.GET.get('client')

    return render(request, 'progress_form.html', {'form': form, 'title': 'Добавление записи прогресса'})


@login_required
def goal_list(request):
    goals = ClientGoal.objects.filter(client__assigned_to=request.user).select_related('client')

    status_filter = request.GET.get('status', '')
    if status_filter:
        goals = goals.filter(status=status_filter)

    paginator = Paginator(goals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
    }
    return render(request, 'goal_list.html', context)


@login_required
def goal_create(request):
    if request.method == 'POST':
        form = ClientGoalForm(request.POST)
        if form.is_valid():
            goal = form.save()
            messages.success(request, 'Цель успешно создана!')
            return redirect('goal_list')
    else:
        form = ClientGoalForm()

    return render(request, 'goal_form.html', {'form': form, 'title': 'Создание цели'})


@login_required
def goal_edit(request, goal_id):
    goal = get_object_or_404(ClientGoal, id=goal_id)

    if request.method == 'POST':
        form = ClientGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Цель успешно обновлена!')
            return redirect('goal_list')
    else:
        form = ClientGoalForm(instance=goal)

    return render(request, 'goal_form.html', {'form': form, 'title': 'Редактирование цели'})


@login_required
def notifications(request):
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.mark_as_read()
            return JsonResponse({'success': True})

        # Mark all as read
        notifications_list.update(is_read=True, read_at=timezone.now())
        messages.success(request, 'Все уведомления отмечены как прочитанные')
        return redirect('notifications')

    unread_count = notifications_list.filter(is_read=False).count()

    paginator = Paginator(notifications_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
    }
    return render(request, 'notifications.html', context)


@login_required
def api_stats(request):
    clients = Client.objects.filter(assigned_to=request.user)

    data = {
        'clients': {
            'total': clients.count(),
            'active': clients.filter(status='active').count(),
            'inactive': clients.filter(status='inactive').count(),
        },
        'tasks': {
            'total': Task.objects.filter(assigned_to=request.user).count(),
            'pending': Task.objects.filter(assigned_to=request.user, status='pending').count(),
            'overdue': Task.objects.filter(
                assigned_to=request.user,
                status__in=['pending', 'in_progress'],
                due_date__lt=timezone.now()
            ).count(),
            'completed_today': Task.objects.filter(
                assigned_to=request.user,
                status='completed',
                completed_at__date=timezone.now().date()
            ).count(),
        },
        'wellness': {
            'avg_wellness': WellnessRecord.objects.filter(
                client__in=clients
            ).aggregate(Avg('wellness_level'))['wellness_level__avg'],
            'avg_energy': WellnessRecord.objects.filter(
                client__in=clients
            ).aggregate(Avg('energy_level'))['energy_level__avg'],
        },
        'progress': {
            'avg_progress': ProgressRecord.objects.filter(
                client__in=clients
            ).aggregate(Avg('progress_percentage'))['progress_percentage__avg'],
            'total_records': ProgressRecord.objects.filter(client__in=clients).count(),
        }
    }

    return JsonResponse(data)


# ==================== core/urls.py ====================
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('clients/', views.client_list, name='client_list'),
    path('clients/create/', views.client_create, name='client_create'),
    path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
    path('clients/<int:client_id>/edit/', views.client_edit, name='client_edit'),

    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/complete/', views.task_complete, name='task_complete'),

    path('wellness/', views.wellness_tracker, name='wellness_tracker'),
    path('wellness/add/', views.wellness_add, name='wellness_add'),

    path('progress/', views.progress_tracker, name='progress_tracker'),
    path('progress/add/', views.progress_add, name='progress_add'),

    path('goals/', views.goal_list, name='goal_list'),
    path('goals/create/', views.goal_create, name='goal_create'),
    path('goals/<int:goal_id>/edit/', views.goal_edit, name='goal_edit'),

    path('notifications/', views.notifications, name='notifications'),

    path('api/stats/', views.api_stats, name='api_stats'),
]


# ==================== core/serializers.py ====================
from rest_framework import serializers
from .models import Client, Task, WellnessRecord, ProgressRecord, ClientGoal


class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'full_name',
            'phone', 'email', 'date_of_birth', 'age', 'address',
            'priority', 'status', 'assigned_to', 'notes', 'tags',
            'created_at', 'updated_at'
        ]

    def get_full_name(self, obj):
        return obj.full_name

    def get_age(self, obj):
        return obj.age


class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.SerializerMethodField()
    days_until_due = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'client', 'category',
            'priority', 'priority_display', 'status', 'status_display',
            'due_date', 'start_date', 'completed_at', 'estimated_hours',
            'actual_hours', 'is_recurring', 'tags', 'is_overdue',
            'days_until_due', 'created_at', 'updated_at'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue

    def get_days_until_due(self, obj):
        return obj.days_until_due

    def get_priority_display(self, obj):
        return obj.get_priority_display()

    def get_status_display(self, obj):
        return dict(Task.STATUS_CHOICES).get(obj.status, '')


class WellnessRecordSerializer(serializers.ModelSerializer):
    overall_health_score = serializers.SerializerMethodField()
    mood_display = serializers.SerializerMethodField()

    class Meta:
        model = WellnessRecord
        fields = [
            'id', 'client', 'date', 'wellness_level', 'mood',
            'mood_display', 'energy_level', 'sleep_quality',
            'stress_level', 'physical_activity', 'water_intake',
            'medication_taken', 'symptoms', 'notes',
            'overall_health_score', 'created_at', 'updated_at'
        ]

    def get_overall_health_score(self, obj):
        return obj.overall_health_score

    def get_mood_display(self, obj):
        return dict(WellnessRecord.MOOD_CHOICES).get(obj.mood, '')


class ProgressRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressRecord
        fields = [
            'id', 'client', 'date', 'metric_1', 'metric_2',
            'metric_3', 'metric_4', 'metric_5', 'custom_metrics',
            'progress_percentage', 'notes', 'created_at', 'updated_at'
        ]


class ClientGoalSerializer(serializers.ModelSerializer):
    is_on_track = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = ClientGoal
        fields = [
            'id', 'client', 'title', 'description', 'target_date',
            'achieved_date', 'status', 'status_display', 'progress',
            'milestones', 'is_on_track', 'created_at', 'updated_at'
        ]

    def get_is_on_track(self, obj):
        return obj.is_on_track()

    def get_status_display(self, obj):
        return dict(ClientGoal.GOAL_STATUS_CHOICES).get(obj.status, '')


# ==================== core/utils.py ====================
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import WellnessRecord, ProgressRecord, Task


def generate_wellness_chart_data(client=None, days=30):
    start_date = timezone.now() - timedelta(days=days)

    records = WellnessRecord.objects.filter(
        date__gte=start_date
    )

    if client:
        records = records.filter(client=client)

    data = records.values('date__date').annotate(
        avg_wellness=Avg('wellness_level'),
        avg_mood=Avg('mood'),
        avg_energy=Avg('energy_level'),
        avg_stress=Avg('stress_level'),
        avg_sleep=Avg('sleep_quality'),
        count=Count('id')
    ).order_by('date__date')

    return {
        'labels': [d['date__date'].strftime('%Y-%m-%d') for d in data],
        'datasets': {
            'wellness': [float(d['avg_wellness'] or 0) for d in data],
            'mood': [float(d['avg_mood'] or 0) for d in data],
            'energy': [float(d['avg_energy'] or 0) for d in data],
            'stress': [float(d['avg_stress'] or 0) for d in data],
            'sleep': [float(d['avg_sleep'] or 0) for d in data],
        }
    }


def generate_progress_chart_data(client=None, days=90):
    start_date = timezone.now() - timedelta(days=days)

    records = ProgressRecord.objects.filter(
        date__gte=start_date
    )

    if client:
        records = records.filter(client=client)

    data = records.values('date__date').annotate(
        avg_progress=Avg('progress_percentage'),
        count=Count('id')
    ).order_by('date__date')

    return {
        'labels': [d['date__date'].strftime('%Y-%m-%d') for d in data],
        'progress': [float(d['avg_progress'] or 0) for d in data],
    }


def check_overdue_tasks():
    from .models import Notification, Task

    overdue_tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    ).select_related('client', 'assigned_to')

    notifications = []
    for task in overdue_tasks:
        existing = Notification.objects.filter(
            notification_type='task_overdue',
            message__icontains=task.title,
            created_at__date=timezone.now().date()
        )

        if not existing.exists() and task.assigned_to:
            notifications.append(
                Notification(
                    user=task.assigned_to,
                    title='⏰ Просроченная задача',
                    message=f'Задача "{task.title}" для клиента {task.client.full_name} просрочена!',
                    notification_type='task_overdue',
                    link=f'/tasks/{task.id}/edit/'
                )
            )

    if notifications:
        Notification.objects.bulk_create(notifications)

    return len(notifications)


def check_upcoming_tasks(days_ahead=1):
    from .models import Notification, Task

    upcoming = timezone.now() + timedelta(days=days_ahead)

    tasks = Task.objects.filter(
        status__in=['pending', 'in_progress'],
        due_date__date=upcoming.date()
    ).select_related('client', 'assigned_to')

    notifications = []
    for task in tasks:
        if task.assigned_to:
            notifications.append(
                Notification(
                    user=task.assigned_to,
                    title='📅 Приближается срок задачи',
                    message=f'Задача "{task.title}" для клиента {task.client.full_name} должна быть выполнена завтра!',
                    notification_type='task_due',
                    link=f'/tasks/{task.id}/edit/'
                )
            )

    if notifications:
        Notification.objects.bulk_create(notifications)

    return len(notifications)


def get_wellness_stats(client):
    records = client.wellness_records.all()

    if not records.exists():
        return None

    last_week = timezone.now() - timedelta(days=7)
    last_month = timezone.now() - timedelta(days=30)

    stats = {
        'current': {
            'wellness': records.first().wellness_level,
            'energy': records.first().energy_level,
            'stress': records.first().stress_level,
            'mood': records.first().mood,
        },
        'week_avg': records.filter(date__gte=last_week).aggregate(
            wellness=Avg('wellness_level'),
            energy=Avg('energy_level'),
            stress=Avg('stress_level'),
        ),
        'month_avg': records.filter(date__gte=last_month).aggregate(
            wellness=Avg('wellness_level'),
            energy=Avg('energy_level'),
            stress=Avg('stress_level'),
        ),
        'total_records': records.count(),
    }

    return stats


def get_priority_score(client):
    score = 0

    priority_weights = {'high': 3, 'medium': 2, 'low': 1}
    score += priority_weights.get(client.priority, 1) * 2

    overdue_count = client.tasks.filter(
        status__in=['pending', 'in_progress'],
        due_date__lt=timezone.now()
    ).count()
    score += overdue_count

    latest_wellness = client.wellness_records.first()
    if latest_wellness and latest_wellness.wellness_level <= 5:
        score += (10 - latest_wellness.wellness_level)

    tasks_today = client.tasks.filter(
        status__in=['pending', 'in_progress'],
        due_date__date=timezone.now().date()
    ).count()
    score += tasks_today

    return score


# ==================== core/tasks.py ====================
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Task, Notification, WellnessRecord
from .utils import check_overdue_tasks, check_upcoming_tasks
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_tasks_task():
    return check_overdue_tasks()


@shared_task
def check_upcoming_tasks_task():
    return check_upcoming_tasks()


@shared_task
def generate_weekly_report():
    from django.contrib.auth.models import User
    from .utils import get_wellness_stats

    for user in User.objects.all():
        clients = user.assigned_clients.all()

        if not clients:
            continue

        total_clients = clients.count()
        active_clients = clients.filter(status='active').count()

        avg_wellness = WellnessRecord.objects.filter(
            client__in=clients,
            date__gte=timezone.now() - timedelta(days=7)
        ).values('client').annotate(avg=Avg('wellness_level'))

        avg_wellness_value = avg_wellness.aggregate(Avg('avg'))['avg__avg'] or 0

        Notification.objects.create(
            user=user,
            title='📊 Еженедельный отчет',
            message=f'За неделю: {total_clients} клиентов, {active_clients} активных. '
                    f'Среднее самочувствие: {avg_wellness_value:.1f}',
            notification_type='system',
            link='/dashboard/'
        )


@shared_task
def send_wellness_alert():
    from django.contrib.auth.models import User
    from django.db.models import Avg

    low_wellness = WellnessRecord.objects.filter(
        date__gte=timezone.now() - timedelta(days=1),
        wellness_level__lte=4
    ).values('client').annotate(avg_wellness=Avg('wellness_level'))

    for item in low_wellness:
        client = Client.objects.filter(id=item['client']).first()
        if client and client.assigned_to:
            Notification.objects.create(
                user=client.assigned_to,
                title='⚠️ Тревога по самочувствию',
                message=f'У клиента {client.full_name} низкий уровень самочувствия '
                        f'({item["avg_wellness"]:.1f}/10) за последние 24 часа',
                notification_type='wellness_alert',
                link=f'/clients/{client.id}/'
            )


# ==================== core/context_processors.py ====================
from .models import Notification


def notifications_context(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}


# ==================== core/signals.py ====================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Client, Task, Notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_client(sender, instance, created, **kwargs):
    if created:
        Client.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or '',
                'last_name': instance.last_name or '',
                'email': instance.email or '',
                'phone': '',
            }
        )


@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to,
            title='📌 Новая задача',
            message=f'Создана новая задача: {instance.title} для клиента {instance.client.full_name}',
            notification_type='system',
            link=f'/tasks/{instance.id}/edit/'
        )


@receiver(post_delete, sender=Client)
def cleanup_client_data(sender, instance, **kwargs):
    notifications = Notification.objects.filter(
        user=instance.assigned_to,
        message__icontains=instance.full_name
    )
    notifications.delete()


# ==================== core/apps.py ====================
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals


# ==================== core/management/commands/check_tasks.py ====================
from django.core.management.base import BaseCommand
from core.tasks import check_overdue_tasks_task, check_upcoming_tasks_task


class Command(BaseCommand):
    help = 'Проверка задач и создание уведомлений'

    def handle(self, *args, **options):
        self.stdout.write('Проверка просроченных задач...')
        overdue = check_overdue_tasks_task()
        self.stdout.write(f'Создано {overdue} уведомлений о просроченных задачах')

        self.stdout.write('Проверка предстоящих задач...')
        upcoming = check_upcoming_tasks_task()
        self.stdout.write(f'Создано {upcoming} уведомлений о предстоящих задачах')

        self.stdout.write(self.style.SUCCESS('Проверка завершена успешно'))


# ==================== core/tests.py ====================
from django.test import TestCase, Client as TestClient
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import Client, Task, WellnessRecord, ProgressRecord, ClientGoal


class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_obj = Client.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='+7 999 999-99-99',
            priority='high',
            status='active'
        )

    def test_client_creation(self):
        self.assertEqual(self.client_obj.full_name, 'User Test')
        self.assertEqual(self.client_obj.priority, 'high')

    def test_client_str(self):
        self.assertEqual(str(self.client_obj), 'User Test')

    def test_client_age(self):
        self.assertIsNone(self.client_obj.age)


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client_obj = Client.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='+7 999 999-99-99'
        )
        self.task = Task.objects.create(
            title='Test Task',
            client=self.client_obj,
            assigned_to=self.user,
            due_date=timezone.now() + timedelta(days=1),
            priority=3,
            status='pending'
        )

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.status, 'pending')

    def test_task_overdue(self):
        self.task.due_date = timezone.now() - timedelta(days=1)
        self.task.save()
        self.assertTrue(self.task.is_overdue)

    def test_task_complete(self):
        self.task.mark_completed()
        self.assertEqual(self.task.status, 'completed')
        self.assertIsNotNone(self.task.completed_at)


class WellnessRecordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client_obj = Client.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='+7 999 999-99-99'
        )
        self.record = WellnessRecord.objects.create(
            client=self.client_obj,
            wellness_level=8,
            mood=4,
            energy_level=7,
            sleep_quality=6,
            stress_level=3
        )

    def test_record_creation(self):
        self.assertEqual(self.record.wellness_level, 8)
        self.assertEqual(self.record.mood, 4)

    def test_overall_health_score(self):
        self.assertGreater(self.record.overall_health_score, 0)
        self.assertLessEqual(self.record.overall_health_score, 10)


class ViewTest(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_dashboard_view_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login


# ==================== init_db.py ====================
import os
import django
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'client_manager.settings')
django.setup()

from core.models import Client, Task, Category, WellnessRecord, ProgressRecord, ClientGoal


def create_test_data():
    categories = [
        {'name': 'Консультация', 'color': '#0d6efd'},
        {'name': 'Документы', 'color': '#198754'},
        {'name': 'Звонок', 'color': '#ffc107'},
        {'name': 'Встреча', 'color': '#dc3545'},
        {'name': 'Отчет', 'color': '#6f42c1'},
    ]

    for cat in categories:
        Category.objects.get_or_create(name=cat['name'], defaults={'color': cat['color']})

    user, _ = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@example.com',
            'first_name': 'Иван',
            'last_name': 'Петров',
        }
    )
    user.set_password('manager123')
    user.save()

    clients_data = [
        {'first_name': 'Анна', 'last_name': 'Смирнова', 'phone': '+7 911 123-45-67', 'priority': 'high'},
        {'first_name': 'Михаил', 'last_name': 'Иванов', 'phone': '+7 922 234-56-78', 'priority': 'medium'},
        {'first_name': 'Елена', 'last_name': 'Козлова', 'phone': '+7 933 345-67-89', 'priority': 'high'},
        {'first_name': 'Дмитрий', 'last_name': 'Соколов', 'phone': '+7 944 456-78-90', 'priority': 'medium'},
        {'first_name': 'Ольга', 'last_name': 'Петрова', 'phone': '+7 955 567-89-01', 'priority': 'low'},
    ]

    clients = []
    for data in clients_data:
        client = Client.objects.create(
            user=None,
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data['phone'],
            email=f"{data['first_name'].lower()}.{data['last_name'].lower()}@example.com",
            priority=data['priority'],
            status='active',
            assigned_to=user,
            date_of_birth=datetime(1980 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28))
        )
        clients.append(client)

    categories = Category.objects.all()
    task_titles = [
        'Первичная консультация',
        'Сбор документов',
        'Звонок для уточнения',
        'Встреча в офисе',
        'Подготовка отчета',
        'Проверка прогресса',
        'Обсуждение плана',
        'Анализ результатов',
        'Планирование следующего шага',
        'Финальный отчет'
    ]

    for client in clients:
        for _ in range(random.randint(3, 6)):
            due_date = datetime.now() + timedelta(days=random.randint(-5, 10))
            Task.objects.create(
                title=random.choice(task_titles),
                client=client,
                category=random.choice(categories),
                assigned_to=user,
                priority=random.randint(1, 4),
                status=random.choice(['pending', 'in_progress', 'completed']),
                due_date=due_date,
                estimated_hours=random.randint(1, 5),
            )

    for client in clients:
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            WellnessRecord.objects.create(
                client=client,
                date=date,
                wellness_level=random.randint(3, 10),
                mood=random.randint(1, 5),
                energy_level=random.randint(3, 10),
                sleep_quality=random.randint(3, 10),
                stress_level=random.randint(1, 8),
                physical_activity=random.randint(0, 60),
                water_intake=random.randint(500, 2000),
                medication_taken=random.choice([True, False]),
            )

    for client in clients:
        progress = 0
        for i in range(20):
            date = datetime.now() - timedelta(days=i*2)
            progress = min(100, progress + random.randint(2, 10))
            ProgressRecord.objects.create(
                client=client,
                date=date,
                metric_1=random.uniform(0, 100),
                metric_2=random.uniform(0, 100),
                metric_3=random.uniform(0, 100),
                progress_percentage=progress,
            )

    goal_titles = [
        'Завершить программу реабилитации',
        'Достичь целевого показателя',
        'Улучшить физическую форму',
        'Стабилизировать состояние',
        'Пройти полный курс'
    ]

    for client in clients:
        for _ in range(random.randint(1, 2)):
            ClientGoal.objects.create(
                client=client,
                title=random.choice(goal_titles),
                target_date=datetime.now() + timedelta(days=random.randint(30, 90)),
                status=random.choice(['not_started', 'in_progress', 'achieved']),
                progress=random.randint(0, 100),
            )

    print(f"Создано тестовых данных:")
    print(f" - Пользователей: 1")
    print(f" - Клиентов: {len(clients)}")
    print(f" - Задач: {Task.objects.count()}")
    print(f" - Записей самочувствия: {WellnessRecord.objects.count()}")
    print(f" - Записей прогресса: {ProgressRecord.objects.count()}")
    print(f" - Целей: {ClientGoal.objects.count()}")


if __name__ == '__main__':
    create_test_data()
    print("\nТестовые данные успешно созданы!")
    print(f"Логин: manager")
    print(f"Пароль: manager123")
