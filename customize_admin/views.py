from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.apps import apps
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count
import sys
from django.db import models

import pkg_resources
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)
def is_admin(user):
    return user.is_superuser

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('customize_admin:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')
    
    return render(request, 'customize_admin/login.html')

def admin_logout(request):
    logout(request)
    return redirect('customize_admin:login')

@user_passes_test(is_admin)
def dashboard(request):
    app_models = {}
    for app_config in apps.get_app_configs():
        try:
            models_list = list(app_config.get_models())
            app_models[app_config.label] = len(models_list)
        except Exception as e:
            logger.warning(f"Error getting models for app {app_config.label}: {e}")
            app_models[app_config.label] = 0

    total_models = sum(app_models.values())

    recent_activities = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            try:
                recent = model.objects.all().order_by('-pk')[:3]
                for item in recent:
                    pk_field = model._meta.pk.name
                    pk_value = getattr(item, pk_field, None)
                    if pk_value:  # skip if PK is missing
                        recent_activities.append({
                            'model': model.__name__,
                            'app': app_config.label,
                            'object': str(item),
                            'id': pk_value
                        })
            except Exception as e:
                logger.warning(f"Error fetching recent for {model.__name__}: {e}")
                continue

    recent_activities = recent_activities[:10]

    User = get_user_model()
    try:
        user_count = User.objects.count()
        admin_count = User.objects.filter(is_staff=True).count()
    except Exception as e:
        logger.warning(f"User count error: {e}")
        user_count = 0
        admin_count = 0

    context = {
        'total_models': total_models,
        'app_models': app_models,
        'recent_activities': recent_activities,
        'user_count': user_count,
        'admin_count': admin_count
    }
    return render(request, 'customize_admin/dashboard.html', context)


@user_passes_test(is_admin)
def models_list(request):
    app_models = []
    
    for app_config in apps.get_app_configs():
        if app_config.models_module is not None:
            app_models_info = []
            for model in app_config.get_models():
                try:
                    count = model.objects.count()
                except:
                    count = 0
                    
                app_models_info.append({
                    'name': model.__name__,
                    'count': count,
                    'app': app_config.label,
                    'model': model.__name__.lower()
                })
            
            if app_models_info:
                app_models.append({
                    'app_name': app_config.verbose_name,
                    'app_label': app_config.label,
                    'models': app_models_info
                })
    
    context = {
        'app_models': app_models
    }
    return render(request, 'customize_admin/models.html', context)

def model_detail(request, app_label, model_name):
    model = apps.get_model(app_label=app_label, model_name=model_name)
    items = model.objects.all()

    # Debug: print records with missing PKs
    for item in items:
        if not item.pk:
            print("⚠️ Record with missing PK:", item)

    fields = [field.name for field in model._meta.fields]

    context = {
        'model_name': model.__name__,
        'app_label': app_label,
        'items': items,
        'fields': fields
    }
    return render(request, 'customize_admin/model_detail.html', context)

@user_passes_test(is_admin)
def model_edit(request, app_label, model_name, pk):
    model = apps.get_model(app_label=app_label, model_name=model_name)
    item = model.objects.select_related('prod_id').get(pk=pk)  # Preload related fields
    
    if request.method == 'POST':
        for field in model._meta.fields:
            if field.name in request.POST and field.name != 'id':
                setattr(item, field.name, request.POST.get(field.name))
        
        item.save()
        messages.success(request, f"{model_name} updated successfully")
        return redirect('customize_admin:model_detail', app_label=app_label, model_name=model_name)
    
    context = {
        'model_name': model.__name__,
        'app_label': app_label,
        'item': item,
        'fields': [field for field in model._meta.fields if field.name != 'id']
    }
    return render(request, 'customize_admin/model_edit.html', context)

@user_passes_test(is_admin)
def model_delete(request, app_label, model_name, pk):
    model = apps.get_model(app_label=app_label, model_name=model_name)
    item = get_object_or_404(model, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, f"{model_name} deleted successfully")
        return redirect('customize_admin:model_detail', app_label=app_label, model_name=model_name)
    
    context = {
        'model_name': model.__name__,
        'app_label': app_label,
        'item': item
    }
    return render(request, 'customize_admin/model_delete.html', context)

@user_passes_test(is_admin)
def model_create(request, app_label, model_name):
    model = apps.get_model(app_label=app_label, model_name=model_name)
    
    if request.method == 'POST':
        # Handle the User assignment properly
        user = request.user  # Assuming the logged-in user should be assigned
        
        # Handle creating the new item
    new_item = model()
    for field in model._meta.fields:
        if field.name in request.POST and field.name != 'id':
            if isinstance(field, models.ForeignKey):  # Check if it's a ForeignKey
                related_model = field.related_model
                related_object = related_model.objects.get(id=request.POST.get(field.name))
                setattr(new_item, field.name, related_object)
            elif field.name == 'User_id':
                setattr(new_item, field.name, user)  # Correctly assign the user object
            else:
                setattr(new_item, field.name, request.POST.get(field.name))

        new_item.save()

        messages.success(request, f"{model_name} created successfully")
        return redirect('customize_admin:model_detail', app_label=app_label, model_name=model_name)
    
    context = {
        'model_name': model.__name__,
        'app_label': app_label,
        'fields': [field for field in model._meta.fields if field.name != 'id' and not field.auto_created]
    }
    return render(request, 'customize_admin/model_create.html', context)


@user_passes_test(is_admin)
def system_info(request):
    # Get installed packages
    installed_packages = sorted([f"{p.key} {p.version}" for p in pkg_resources.working_set])
    
    # Get Django-related info
    django_apps = []
    for app_config in apps.get_app_configs():
        models_list = list(app_config.get_models())  # Convert the generator to a list
        django_apps.append({
        'name': app_config.verbose_name,
        'app_label': app_config.label,
        'models_count': len(models_list)  # Now we can safely use len() on the list
        })

    
    # Python version
    python_version = sys.version
    
    # Admin-related packages
    admin_packages = []
    for package in installed_packages:
        if any(x in package.lower() for x in ['admin', 'dashboard', 'jazzmin', 'flask']):
            admin_packages.append(package)
    
    context = {
        'python_version': python_version,
        'installed_packages': installed_packages,
        'django_apps': django_apps,
        'admin_packages': admin_packages
    }
    return render(request, 'customize_admin/system_info.html', context)