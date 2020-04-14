from django.conf import settings
from slackweb import slackweb


def notify_slack(attachments, channel):
    if channel:
        slack = slackweb.Slack(url=channel)
        slack.notify(attachments=attachments)
