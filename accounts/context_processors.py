from notifications.models import Notification
from programs.models import NutritionProgram
from clients.models import ClientProfile

def notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {
            'unread_notifications_count': unread_count,
            'has_unread_notifications': unread_count > 0,
        }
    return {}

def active_program(request):
    if request.user.is_authenticated and request.user.role == 'client':
        program = NutritionProgram.objects.filter(
            client__user=request.user,
            status='active'
        ).first()
        return {
            'active_program': program
        }
    return {}

def chat_context(request):
    context = {}
    if request.user.is_authenticated and request.user.role == 'client':
        try:
            profile = request.user.client_profile
            context['active_nutritionist'] = profile.nutritionist
        except ClientProfile.DoesNotExist:
            context['active_nutritionist'] = None
    return context