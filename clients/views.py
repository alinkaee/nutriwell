from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ClientProfileForm, ClientUserForm
from programs.models import NutritionProgram
from .models import ClientProfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'client':
        print(f"Создаём профиль для {instance.email}")
        ClientProfile.objects.get_or_create(
            user=instance,
            defaults={'nutritionist': None}  # ← можно оставить None, если привязка позже
        )

@login_required
def edit_client_profile(request):
    if request.user.role != 'client':
        return redirect('accounts:dashboard')

    profile = get_object_or_404(ClientProfile, user=request.user)

    if request.method == 'POST':
        user_form = ClientUserForm(request.POST, instance=request.user)
        profile_form = ClientProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('accounts:dashboard')
    else:
        user_form = ClientUserForm(instance=request.user)
        profile_form = ClientProfileForm(instance=profile)

    return render(request, 'clients/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })




@login_required
def view_client_profile(request, client_id):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    profile = get_object_or_404(ClientProfile, id=client_id)

    if not NutritionProgram.objects.filter(
            client=profile,
            nutritionist__user=request.user
    ).exists():
        messages.warning(request, "Этот клиент не привязан к вам.")
        return redirect('accounts:nutritionist_clients')

    return render(request, 'clients/view_client_profile.html', {'profile': profile})

@login_required
def view_profile(request, client_id):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    client = get_object_or_404(ClientProfile, id=client_id)
    # Убедись, что клиент привязан к этому нутрициологу
    if client.nutritionist.user != request.user:
        messages.warning(request, "Этот клиент не привязан к вам.")
        return redirect('accounts:nutritionist_clients')

    return render(request, 'clients/view_profile.html', {
        'client': client,
    })