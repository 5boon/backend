import string
import random

from django.core.mail import EmailMessage

TEMP_PW_STRING_POLL = string.ascii_uppercase + string.digits + string.punctuation


def send_pw_email(email_address, new_pw):
    content = '안녕하세요! 5boon 입니다!\n' \
              '임시비밀번호를 전송해드립니다!\n' \
              '재접속 후 비밀번호를 재설정 해주세요:D\n' \
              '* 임시 비밀번호: {}'.format(new_pw)

    # from (settings 에 설정해서 작성안해도 됨)
    email = EmailMessage(
        subject='5boon 임시 비밀번호 전송',
        body=content,
        to=[email_address],  # 받는 이메일 리스트
    )

    email.send()


def create_temp_pw():
    """
        임시 비밀번호 생성
    """

    result = ""

    for i in range(8):
        result += random.choice(TEMP_PW_STRING_POLL)

    return result
