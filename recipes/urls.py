from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    BlogIndexView,
    UserRegisterView,
    UserLoginView,
    RecipeSearchView,
    AccountInformationView,
    RecipeAdditionView,
    EditAccountInformationView,
    AccountRecipesView,
    ViewRecipeView,
    LikePostView,
    RecipeUpdateView,
    LikedRecipesView,
    ViewUserView,
    DeleteCommentView,
    CategoryView,
    RecipeDeleteView,
    generate_recipe_pdf
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
      # Home page
      path('', BlogIndexView.as_view(), name='blog_index'),

      # User authentication
      path('login/', UserLoginView.as_view(), name='user_login'),
      path('register/', UserRegisterView.as_view(), name='user_register'),
      path('logout/', LogoutView.as_view(next_page='blog_index'), name='logout'),

      # Account management
      path('account-information/', AccountInformationView.as_view(), name='account_information'),
      path('edit-account-information/', EditAccountInformationView.as_view(), name='edit_account_information'),
      path('account-recipes/', AccountRecipesView.as_view(), name='account_recipes'),
      path('liked-recipes/', LikedRecipesView.as_view(), name='liked_recipes'),

      # Recipe management
      path('recipe-creation/', RecipeAdditionView.as_view(), name='recipe_creation'),
      path('recipe-view/<int:post_id>/', ViewRecipeView.as_view(), name='recipe_view'),
      path('edit-recipe/<int:post_id>/', RecipeUpdateView.as_view(), name='edit_recipe'),
      path('recipe/<int:post_id>/delete/', RecipeDeleteView.as_view(), name='recipe_delete'),

      # Recipe interaction
      path('post/<int:post_id>/like/', LikePostView.as_view(), name='like_post'),
        path('comment/delete/<int:comment_id>/', DeleteCommentView.as_view(), name='delete_comment'),
        path('recipe/<int:recipe_id>/pdf/', generate_recipe_pdf, name='generate_recipe_pdf'),

      # Search and category view
      path('search-recipe/', RecipeSearchView.as_view(), name='search_recipe'),
      path('category/<str:category_name>/', CategoryView.as_view(), name='category_view'),

      # User profile view
      path('user-view/<int:user_id>/', ViewUserView.as_view(), name='user_view'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
