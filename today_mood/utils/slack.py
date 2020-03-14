from django.conf import settings
from slackweb import slackweb


def notify_slack(attachments, channel):
    slack = slackweb.Slack(url=settings.SLACK_CHANNEL_JOINED_USER)
    slack.notify(channel=channel, attachments=attachments)
