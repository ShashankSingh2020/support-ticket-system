from rest_framework import viewsets, permissions, filters
from apps.knowledge_base.models import Article
from apps.knowledge_base.serializers import ArticleSerializer
from apps.users.models import User
from apps.users.permissions import IsManager, IsAdminUserRole


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "content", "category"]

    def get_queryset(self):
        user = self.request.user
        # Staff can inspect drafts and archived articles; Customers only see PUBLISHED
        if user.is_authenticated and user.role in [User.Role.ADMIN, User.Role.MANAGER, User.Role.AGENT]:
            return Article.objects.select_related("author").all()
        return Article.objects.select_related("author").filter(status=Article.Status.PUBLISHED)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        # Only Managers and Admins can create, update, or delete articles
        return [permissions.IsAuthenticated(), (IsManager | IsAdminUserRole)()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)