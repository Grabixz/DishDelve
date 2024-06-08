from datetime import date
from django.core.files import File
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.db.models import Count
from recipes.forms import *
from recipes.models import *


class BlogIndexView(TemplateView):
    # This is the class view for the home page called BlogIndexView
    # It specifies what HTML template will be used for the view
    template_name = "recipes/index.html"

    def get_context_data(self, **kwargs):
        context = super(BlogIndexView, self).get_context_data(**kwargs)
        # This is used to retrieve the first and second random recipe
        first_random_recipe = RecipePosts.objects.order_by('?').first()
        second_random_recipe = RecipePosts.objects.order_by('?').first()
        different_recipes = True

        while different_recipes:
            # It then checks to make sure the two random recipes don't match so that it displays different recipes
            if first_random_recipe.id == second_random_recipe.id:
                second_random_recipe = RecipePosts.objects.order_by('?').first()
            else:
                # If the recipes are different it will end the while loop
                different_recipes = False

        # This then gathers the information in the context and is used in the template using the context name
        context['user'] = self.request.user
        # This gathers the top 10 most recent recipes by date-created
        context['recipes'] = RecipePosts.objects.order_by('-date_created')[:10]
        context['first_random_recipe'] = first_random_recipe
        context['second_random_recipe'] = second_random_recipe
        # This gathers the top 10 most liked recipes
        context['top_liked_recipes'] = RecipePosts.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')[:10]
        return context


class UserRegisterView(CreateView):
    # This view is to register the user if they do not have an account already with us
    template_name = "recipes/register.html"
    form_class = RegisterForm
    # They will be redirected to the login page if they registered successfully
    success_url = reverse_lazy('user_login')

    def form_valid(self, form):
        user = form.save(commit=False)
        # This is to assign the default user profile to the user when they first sign up with us.
        default_image_path = 'recipes/static/recipes/default-profile-picture.png'
        with open(default_image_path, 'rb') as image:
            user.profile_picture.save('default-profile-picture.png', File(image), save=True)
        user.save()
        # This displays the success message if their account was successfully created
        messages.success(self.request, 'You registered successfully!')
        return super().form_valid(form)


class UserLoginView(View):
    # This view is for when the user logs into their account
    form_class = LoginForm
    template_name = 'recipes/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # This is to check if the information matches the information in the database
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # This keeps the user logged in the website so they don't have constantly log in each time
                login(request, user)
                # It then displays the success message and redirects them to their profile page
                messages.success(request, f'You logged in successfully! Welcome {user.get_full_name()}')
                return redirect('account_information')
            else:
                # This displays the error message if the email or password is incorrect
                messages.error(request, 'Invalid Email or Password!')
        return render(request, self.template_name, {'form': form})


class RecipeAdditionView(LoginRequiredMixin, View):
    # This view is to create a new recipe on the website
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')
    template_name = 'recipes/recipe_addition.html'

    def get(self, request):
        form = RecipeCreationForm()
        # This uses the form RecipeCreationForm
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RecipeCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # If the forms information is correct, the following will happen
            recipe = form.save(commit=False)
            # This sets the user who created the recipe to the user who is logged in
            recipe.uploaded_by = request.user
            recipe.save()
            # This displays the success message and redirects them to the recipe they just uploaded
            messages.success(request, 'Your Recipe Was Successfully Added')
            return redirect('recipe_view', post_id=recipe.id)
        else:
            # If the form is not valid, it will inform the user which one has an error
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
            for error in form.non_field_errors():
                messages.error(request, error)
            return render(request, self.template_name, {'form': form})


class AccountInformationView(LoginRequiredMixin, TemplateView):
    # This view is used to view the account information
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')
    template_name = 'recipes/account.html'

    def get_context_data(self, **kwargs):
        # It gathers the user who is currently logged in and gets their information for the template
        context = super(AccountInformationView, self).get_context_data(**kwargs)
        user_information = self.request.user
        context['user'] = user_information
        return context


class EditAccountInformationView(LoginRequiredMixin, TemplateView):
    # This view is to edit the account information if the user wants to add or change something
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')
    template_name = 'recipes/edit_account.html'

    def get_context_data(self, **kwargs):
        # It gathers the existing information of the user and displays it in the form fields
        context = super(EditAccountInformationView, self).get_context_data(**kwargs)
        user_information = self.request.user
        form = EditAccountInformationForm(instance=user_information)
        context['form'] = form
        context['user'] = user_information
        return context

    def post(self, request, *args, **kwargs):
        # If the user decides to edit their profile, the following will happen.
        form = EditAccountInformationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # If the form is valid, it will update it on the form and will update the password here
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                # This sets the new password for the user on their profile on the database model
                user.set_password(new_password)
            user.save()
            if new_password:
                # It then hashes the password for the user in the database to be more secure
                update_session_auth_hash(request, user)
                # It then displays the success message and redirects them to their profile
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('account_information')
        else:
            # If the form is not valid, it will display the following message and display which fields
            messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {'form': form})


class CategoryView(TemplateView):
    # This view is for the specific category
    template_name = 'recipes/category_page.html'

    def get_context_data(self, **kwargs):
        # This displays the specific category the user selected to reuse the code.
        context = super(CategoryView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        # Here it gathers the category name the user has selected to view
        category_name = self.kwargs.get('category_name')
        context['category_name'] = category_name
        # it uses the custom paginate function if the recipes are more than 5
        context['recipes'] = custom_paginate_qs(RecipePosts.objects.filter(category=category_name), page)
        return context


class AccountRecipesView(LoginRequiredMixin, TemplateView):
    # This view is used to view the recipes the user that is logged in.
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')
    template_name = 'recipes/account_recipes.html'

    def get_context_data(self, **kwargs):
        # It gathers all the recipes the user has uploaded to the website
        context = super(AccountRecipesView, self).get_context_data(**kwargs)
        user_information = self.request.user
        page = self.request.GET.get('page', 1)
        # here it gathers all the recipes the user uploaded
        all_recipes = RecipePosts.objects.filter(uploaded_by=user_information)
        context['recipe_pages'] = custom_paginate_qs(all_recipes, page)
        context['recipes'] = all_recipes
        return context


class ViewRecipeView(TemplateView):
    # This view is used to view a specific recipe
    template_name = 'recipes/recipe_view.html'

    def get_context_data(self, **kwargs):
        # This gathers all the information of the specific recipe the user wants to view
        context = super(ViewRecipeView, self).get_context_data(**kwargs)
        # This get_object_or_404 will get the object, if it can't find it a 404 page will be displayed
        post = get_object_or_404(RecipePosts, id=self.kwargs['post_id'])
        page = self.request.GET.get('page', 1)
        context['user'] = self.request.user
        context['recipe'] = post
        # This splits the ingredients and directions by the special key so it can display it nicely
        context['ingredients'] = post.ingredients.split('§')
        context['directions'] = post.directions.split('§')

        # This checks if the user is logged in, if they are they will be able to like the post or check if they already
        # liked the post. If they are not logged in, they won't be able to like the post and it will be set to false
        if self.request.user.is_authenticated:
            context['is_liked'] = Like.objects.filter(user=self.request.user, recipe_post=post).exists()
        else:
            context['is_liked'] = False

        context['post_user_id'] = post.uploaded_by.id
        # This displays the CommentForm so the user can upload a comment on the post
        context['form'] = CommentForm()
        context['comments'] = custom_paginate_qs(post.comments.all(), page)
        return context

    def post(self, request, *args, **kwargs):
        # This is to upload the comment on the specific post the user wants to make
        post = get_object_or_404(RecipePosts, id=self.kwargs['post_id'])
        form = CommentForm(request.POST)
        if form.is_valid():
            # This will upload and save the comment on the model Comment
            comment = form.save(commit=False)
            comment.post = post
            comment.author = self.request.user
            comment.save()
            # It will then display the success message and will take the user back to the current page
            messages.success(self.request, 'Your comment was uploaded successfully!')
            return redirect('recipe_view', post_id=post.id)

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)


class DeleteCommentView(LoginRequiredMixin, View):
    # This view is used to delete the comment the user posted or another comment if they are the user
    # of the post or admin.
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')

    def post(self, request, comment_id, *args, **kwargs):
        # It gathers the comment and deletes it
        comment = get_object_or_404(Comments, id=comment_id)
        comment.delete()
        # it then displays the success message and redirects them to the current page they were on
        messages.success(request, 'Your comment has successfully been removed')
        return redirect('recipe_view', post_id=comment.post.id)


class RecipeDeleteView(LoginRequiredMixin, View):
    # This view is used to delete a recipe post
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')

    def post(self, request, post_id, *args, **kwargs):
        # This gathers the recipe ID from the URL and then deletes it from the model
        recipe = get_object_or_404(RecipePosts, pk=post_id)
        recipe.delete()
        # it then displays a success message and redirects the user to the home page
        messages.success(request, 'Your recipe has been successfully deleted')
        return redirect('blog_index')


class LikePostView(LoginRequiredMixin, View):
    # This view is used to like a recipe post
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')

    def post(self, request, *args, **kwargs):
        # it will gather the post id from the URL
        post_id = self.kwargs['post_id']
        post = get_object_or_404(RecipePosts, id=post_id)
        # it will then gather or create a new object in the Like model
        like, created = Like.objects.get_or_create(user=request.user, recipe_post=post)

        # if the user presses the like button, it will be that they unlike the post and delete the like
        # from the Like model
        if not created:
            like.delete()

        return redirect('recipe_view', post_id=post_id)


class RecipeUpdateView(LoginRequiredMixin, View):
    # this view is used to update the Recipe post they made
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')
    template_name = 'recipes/recipe_edit.html'

    def get(self, request, post_id):
        # This gathers the recipe post id and stores the existing information into the RecipeCreation Form
        recipe = get_object_or_404(RecipePosts, pk=post_id, uploaded_by=request.user)
        form = RecipeCreationForm(instance=recipe)
        # it splits the ingredients and directions by the special key
        ingredients = recipe.ingredients.split('§')
        directions = recipe.directions.split('§')

        return render(request, self.template_name, {
            'form': form,
            'ingredients': ingredients,
            'directions': directions,
        })

    def post(self, request, post_id):
        # this will be used if the user wants to upload the new changes to the post
        recipe = get_object_or_404(RecipePosts, pk=post_id, uploaded_by=request.user)
        form = RecipeCreationForm(request.POST, request.FILES, instance=recipe)

        if form.is_valid():
            # if the form was valid the following changes are made
            recipe = form.save(commit=False)
            recipe.uploaded_by = request.user
            ingredients = request.POST.getlist('ingredient')
            directions = request.POST.getlist('direction')
            recipe.ingredients = '§'.join(ingredients)
            recipe.directions = '§'.join(directions)
            # the date_modified is then used/created
            recipe.date_modified = date.today()
            recipe.save()
            # The success message will be displayed and they will be redirected to the recipe view page
            messages.success(request, 'Your Recipe Was Successfully Updated')
            return redirect('recipe_view', post_id=recipe.pk)
        else:
            # This will display if the form was not valid
            messages.error(request, 'Please correct the error below.')

        # This gathers the ingredients and directions as a list
        ingredients = request.POST.getlist('ingredient')
        directions = request.POST.getlist('direction')

        return render(request, self.template_name, {
            'form': form,
            'ingredients': ingredients,
            'directions': directions,
        })


class LikedRecipesView(LoginRequiredMixin, TemplateView):
    # THis view is used for when the user wants to view the posts they have liked
    # The login_url is used if the user is not logged in, it will redirect them to the login page
    login_url = reverse_lazy('user_login')
    template_name = 'recipes/liked_recipes.html'

    def get_context_data(self, **kwargs):
        # This gathers all the recipe posts they have liked on the website
        context = super(LikedRecipesView, self).get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        all_recipes = Like.objects.filter(user=self.request.user.id)
        context['liked_recipes'] = custom_paginate_qs(all_recipes, page)
        return context


class ViewUserView(TemplateView):
    # This view is used to view other users profiles
    template_name = 'recipes/account_view.html'

    def get_context_data(self, **kwargs):
        # it gathers all the users information the user wants to view and all the recipes the specific
        # user has uploaded to the website.
        context = super(ViewUserView, self).get_context_data(**kwargs)
        user_id = self.kwargs.get('user_id')
        page = self.request.GET.get('page', 1)
        context['user'] = get_object_or_404(User, id=user_id)
        context['recipes'] = custom_paginate_qs(RecipePosts.objects.filter(uploaded_by=user_id), page)
        return context


class RecipeSearchView(ListView):
    # This view is used to search for a recipe
    model = RecipePosts
    template_name = 'recipes/search.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        # This gathers the search field of what the user wants to search for
        queryset = RecipePosts.objects.all()
        search_value = self.request.GET.get('search_value', '')
        if search_value:
            queryset = queryset.filter(title__icontains=search_value)
        return queryset

    def get_context_data(self, **kwargs):
        # This gathers all the information of the recipe posts
        context = super().get_context_data(**kwargs)
        # it checks the search value
        search_value = self.request.GET.get('search_value', '')
        page = self.request.GET.get('page', 1)

        if search_value:
            # It will display the searched item the user is looking for
            queryset = RecipePosts.objects.filter(title__icontains=search_value).order_by("-title")
        else:
            # if the user has not searched anything yet, it will display all the recipes on the site
            queryset = RecipePosts.objects.all().order_by("-title")

        context['recipes'] = custom_paginate_qs(queryset, page)
        context['search_form'] = SearchForm(self.request.GET or None)
        context['search_value'] = search_value
        context['user'] = self.request.user
        return context


def custom_paginate_qs(qs, page, item_count: int = 5):
    # This is the custom function that is created to go through the recipes, if it is more than 5 recipes
    paginator = Paginator(qs, item_count)
    try:
        paginated_qs = paginator.page(page)
    except PageNotAnInteger:
        paginated_qs = paginator.page(1)
    except EmptyPage:
        paginated_qs = paginator.page(paginator.num_pages)
    return paginated_qs
