from rest_framework.routers import DefaultRouter
from apps.knowledge_base.views import ArticleViewSet

router = DefaultRouter()
router.register(r"articles", ArticleViewSet, basename="article")

urlpatterns = router.urls