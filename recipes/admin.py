# This is the page where all the information that is display on the admin will be shown here
from django.contrib import admin
from recipes.models import RecipePosts, Comments, User, Like


class AuthorsAdmin(admin.ModelAdmin):
    # This is for the Users that are created
    list_display = ['first_name', 'last_name', 'email']
    search_fields = ['first_name', 'last_name', 'email']


class RecipePostsAdmin(admin.ModelAdmin):
    # This is for all the recipes that are created
    search_fields = ['title', 'category']
    list_display_links = ['title']
    list_display = ['title', 'category', 'uploaded_by', 'date_created', 'total_likes']


class CommentsAdmin(admin.ModelAdmin):
    # This is for all the comments that have been created
    list_display = ['body', 'post', 'created_on']
    list_display_links = ['post']


class LikeAdmin(admin.ModelAdmin):
    # This is for all the liked recipe posts
    list_display = ['user', 'recipe_post', 'liked_at']
    list_display_links = ['recipe_post']


# This is how you declare and create the admin class to view it on the admin site
admin.site.register(User, AuthorsAdmin)
admin.site.register(RecipePosts, RecipePostsAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Like, LikeAdmin)
