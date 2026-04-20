from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Util:
    @staticmethod
    def send_mail(template_name, data):
        if not getattr(settings, "EMAIL_HOST_PASSWORD", None):
            raise ImproperlyConfigured(
                "EMAIL_HOST_PASSWORD is empty. Please set it in backend .env/.env.local."
            )
        html_content = render_to_string(template_name, data) # 使用模板並插入資料
        text_content = strip_tags(html_content)  # 產生純文字版本
        email = EmailMultiAlternatives(
            subject=data['emailSubject'],
            body=text_content,
            from_email=getattr(settings, "EMAIL_HOST_USER", None),
            to=[data['toEmail']]
        )
        email.attach_alternative(html_content, "text/html")  # 加入 HTML 版本
        email.send()
