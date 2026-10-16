from rest_framework import serializers
from apps.knowledge_base.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "slug",
            "category",
            "content",
            "status",
            "author_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author_email", "created_at", "updated_at")