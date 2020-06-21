import hashlib

from chunkator import chunkator

from apps.mood_groups.models import MoodGroup

CHUNK_SIZE = 1000


def insert_group_code():
    no_code_group_qs = MoodGroup.objects.filter(code='')

    for group in chunkator(no_code_group_qs, CHUNK_SIZE):
        code = hashlib.sha256(group.title.encode()).hexdigest()
        group.code = code
        group.save(update_fields=['code'])


def run():
    insert_group_code()
