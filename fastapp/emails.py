from email.message import EmailMessage

import aiosmtplib

import config


async def send_email(receiver_email: str, title: str, message: str) -> bool:
    sender_email: str = config.EMAIL_LOGIN

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = title
    msg.set_content(message)

    username: str = sender_email

    try:
        await aiosmtplib.send(
            msg,
            sender=sender_email,
            recipients=receiver_email,
            hostname=config.EMAIL_SMTP_HOST,
            port=config.EMAIL_SMTP_PORT,
            username=username,
            password=config.EMAIL_PASSWORD,
            use_tls=True
        )
        return True
    except Exception as e:
        print(e)
        return False