from rest_framework import serializers
from .models import Post, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class PostSerializer(serializers.ModelSerializer):
    # Garder la version détaillée pour la lecture (GET)
    category_detail = CategorySerializer(source='category', read_only=True)

    # Permettre l'envoi de l'ID de catégorie lors de la création/modification
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,  # Seulement pour POST/PUT, pas visible dans GET
        required=True  # Obligatoire lors de la création
    )

    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title','category', 'slug', 'content', 'conclusion', 'image',
             'category_detail', 'author', 'pub_date', 'views', 'likes', 'is_published'
        ]
        read_only_fields = ['author', 'pub_date', 'views', 'likes', 'category_detail'] # ← on protège ces champs