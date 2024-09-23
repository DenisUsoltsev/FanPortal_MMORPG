from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_save, sender=get_user_model())
def assign_permissions_to_new_user(sender, instance, created, **kwargs):
    if created:
        advert_permissions = [
            'add_advert',
            'change_advert',
            'delete_advert',
            'view_advert',
        ]

        response_permissions = [
            'add_response',
            'change_response',
            'delete_response',
            'view_response',
        ]

        advert_content_type = ContentType.objects.get(app_label='adverts', model='advert')
        response_content_type = ContentType.objects.get(app_label='adverts', model='response')

        for perm in advert_permissions:
            try:
                permission = Permission.objects.get(codename=perm, content_type=advert_content_type)
                instance.user_permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"Permission '{perm}' not found for model Advert")

        for perm in response_permissions:
            try:
                permission = Permission.objects.get(codename=perm, content_type=response_content_type)
                instance.user_permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"Permission '{perm}' not found for model Response")
