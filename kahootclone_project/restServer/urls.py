from django.urls import path, include
from . import views
from rest_framework import routers


router = routers.DefaultRouter()

router.register(
    prefix='participant',
    viewset=views.ParticipantViewSet,
    basename='participant'
)
router.register(
    prefix='games',
    viewset=views.GameView,
    basename='game'
)
router.register(
    prefix='guess',
    viewset=views.GuessViewSet,
    basename='guess'
)

urlpatterns = [
    path('', include(router.urls)),
]
