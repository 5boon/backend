from rest_framework import routers

from api.mood_groups.views import GroupViewSet, MyGroupViewSet, GroupInvitationViewSet

app_name = 'mood_groups'


router = routers.SimpleRouter()
router.register(r'', GroupViewSet, basename='group')
router.register(r'mine', MyGroupViewSet, basename='my_group')
router.register(r'invitation', GroupInvitationViewSet, basename='invitation')
urlpatterns = router.urls
