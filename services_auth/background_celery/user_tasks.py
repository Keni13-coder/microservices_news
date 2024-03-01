from fastapi_mail import MessageSchema, FastMail, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape

from schemas import OutputUserSchema
from core.config import settings
from background_celery.app_celery import celery 


@celery.task
def send_message(url:str, user: OutputUserSchema) -> None:
    '''Sends an email to the user'''
    loader = FileSystemLoader('background_celery/verifications/', followlinks=True)
    env = Environment(
    loader=loader, # PackageLoader('templates', 'verifications')
    autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('verification.html')
    subject = 'Your verification code (Valid for 30min)'
    html = template.render(
            url=url,
            first_name=user.username,
            subject=subject
        )
    
    message = MessageSchema(
        subject=subject,
        recipients=[user.email],
        body=html,
        subtype=MessageType.html
        )
    fm = FastMail(settings.mail_conf)
    fm.send_message(message=message)
