from django.core.mail import EmailMessage

class Util:
    @staticmethod
    def send_mail(data):
        email = EmailMessage(subject=data['emailSubject'], body=data['emailBody'], to=[data['toEmail']])
        email.send()