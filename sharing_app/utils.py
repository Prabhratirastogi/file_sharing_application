import logging
from django.core.mail import send_mail, BadHeaderError
from django.urls import reverse
from django.conf import settings
from smtplib import SMTPException  # Import SMTPException from the smtplib module

logger = logging.getLogger(__name__)  # Set up logging

def send_verification_email(user, token):
    # Construct the verification link
    verification_link = f"{settings.BACKEND_URL}{reverse('verify-email', args=[token])}"
    
    subject = "Verify Your Email"
    message = f"Click the link to verify your email: {verification_link}"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except BadHeaderError:
        logger.error(f"Invalid header found when sending email to {user.email}.")
    except SMTPException as e:
        logger.error(f"Failed to send email to {user.email} due to SMTP error: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred when sending email to {user.email}: {str(e)}")
