from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils.timezone import now, timedelta

from FanPortal_MMORPG import settings
from FanPortal_MMORPG.settings import SITE_DOMAIN
from .models import Advert, Subscription, Category


@shared_task
def send_weekly_newsletter():
    categories = Category.objects.all()

    one_week_ago = now() - timedelta(days=7)

    for category in categories:
        new_adverts = Advert.objects.filter(
            category=category,
            time_create__gte=one_week_ago,
            is_published=True
        )

        if new_adverts.exists():
            subscribers = Subscription.objects.filter(category=category).values_list('user__email',
                                                                                         flat=True).distinct()

            advert_links = ''.join(
                [f'<p><a href="{SITE_DOMAIN}{advert.get_absolute_url()}">{advert.title}</a></p>' for advert in
                 new_adverts]
            )

            subject = f'Новые объявления в категории "{category.name}" за последнюю неделю'
            text_content = f'Здравствуйте!\n\nВот новые объявления в категории "{category.name}". Перейдите по ссылкам, чтобы узнать подробности.'
            html_content = f'<p>Здравствуйте!</p><p>Вот новые объявления в категории "{category.name}":</p>{advert_links}<p>Перейдите по ссылкам, чтобы узнать подробности.</p>'

            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, list(subscribers))
            msg.attach_alternative(html_content, "text/html")
            msg.send()
