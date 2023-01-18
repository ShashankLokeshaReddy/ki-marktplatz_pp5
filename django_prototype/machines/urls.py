from django.urls import path

from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register('machines', MachinesViewSet)


urlpatterns = router.urls