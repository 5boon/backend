from django.conf import settings
from slackweb import slackweb

from apps.users.models import User


def slack_notify_new_user(user: User, join_type: str = '5boon'):
    channel = settings.SLACK_CHANNEL_JOINED_USER
    attachments = [
        {
            "color": "#36a64f",
            "title": "유저 가입({})".format(join_type),
            "pretext": "새로운 유저가 가입했습니다.",
            "fields": [
                {
                    "title": "아이디",
                    "value": user.username,
                    "short": True
                },
                {
                    "title": "이름",
                    "value": user.name,
                    "short": True
                },
                {
                    "title": "이메일",
                    "value": user.email,
                    "short": True
                }
            ]
        }
    ]

    if channel:
        slack = slackweb.Slack(url=channel)
        slack.notify(attachments=attachments)


def slack_notify_new_group(user_name: str, data: dict):
    channel = settings.SLACK_CHANNEL_CREATE_MOOD
    attachments = [
        {
            "color": "#9966FF",
            "pretext": "아이엠 그룹트!\n`{}`님이 그룹을 생성했습니다!".format(user_name),
            "title": "그룹 생성",
            "fields": [
                {
                    "title": "타이틀",
                    "value": data.get('title'),
                    "short": True
                },
                {
                    "title": "설명",
                    "value": data.get('summary'),
                    "short": True
                }
            ]
        }
    ]

    if channel:
        slack = slackweb.Slack(url=channel)
        slack.notify(attachments=attachments)


def slack_notify_new_mood(status: list, user_name: str, simple_summary: str):
    channel = settings.SLACK_CHANNEL_CREATE_MOOD

    attachments = [
        {
            "color": status[1],
            "title": "기분 생성",
            "pretext": "앙! 기분띠!\n`{}`님이 기분을 생성했습니다!".format(user_name),
            "fields": [
                {
                    "title": "상태",
                    "value": status[0],
                    "short": True
                },
                {
                    "title": "간단 설명",
                    "value": simple_summary,
                    "short": True
                }
            ]
        }
    ]
    if channel:
        slack = slackweb.Slack(url=channel)
        slack.notify(attachments=attachments)
