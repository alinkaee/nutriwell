from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import NutritionistProfile
from .forms import NutritionistProfileForm, NutritionistUserForm

@login_required
def edit_nutritionist_profile(request):
    if request.user.role != 'nutritionist':
        return redirect('accounts:dashboard')

    profile, created = NutritionistProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = NutritionistUserForm(request.POST, instance=request.user)
        profile_form = NutritionistProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('accounts:dashboard')
    else:
        user_form = NutritionistUserForm(instance=request.user)
        profile_form = NutritionistProfileForm(instance=profile)

    return render(request, 'accounts/nutritionist/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })