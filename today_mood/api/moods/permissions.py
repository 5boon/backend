from rest_framework.permissions import BasePermission

from apps.mood_groups.models import UserMoodGroup


class IsUserMoodGroup(BasePermission):

    def has_permission(self, request, view):
        show_summary_group_ids = request.data.get('group_list', [])  # 기분 설명(summary) 보여줄 그룹

        if show_summary_group_ids:
            # 현재 속한 그룹 리스트 가져옴
            mood_group_ids = list(UserMoodGroup.objects.filter(
                user_id=request.user.id
            ).values_list('mood_group_id', flat=True))

            # 내가 속하지 않은 그룹의 id인 경우 permission error
            if set(show_summary_group_ids) - set(mood_group_ids):
                return False

        return True
