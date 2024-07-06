from datetime import date
from PIL.ImageDraw import ImageDraw
from reportlab.lib.units import cm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib import messages
from django.db.models import Count
from recipes.forms import *
from recipes.models import *
import os
import io
import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image as PILImage, ImageDraw


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
        context['top_liked_recipes'] = RecipePosts.objects.annotate(num_likes=Count('likes')).order_by('-num_likes')[
                                       :10]
        return context


class UserRegisterView(CreateView):
    # This view is to register the user if they do not have an account already with us
    template_name = "recipes/register.html"
    form_class = RegisterForm
    # They will be redirected to the login page if they registered successfully
    success_url = reverse_lazy('user_login')

    def dispatch(self, request, *args, **kwargs):
        # This will check if the user is logged in already
        if request.user.is_authenticated:
            # If the user is logged in, they will be redirected to the home page, so they can't
            # create another account while being logged into the account
            return redirect('blog_index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        # This displays the success message if their account was successfully created
        messages.success(self.request, 'You registered successfully!')
        return super().form_valid(form)


class UserLoginView(View):
    # This view is for when the user logs into their account
    form_class = LoginForm
    template_name = 'recipes/login.html'

    def dispatch(self, request, *args, **kwargs):
        # This will check if the user is logged in already
        if request.user.is_authenticated:
            # If the user is logged in, they will be redirected to the home page, so they can't
            # create another account while being logged into the account
            return redirect('blog_index')
        return super().dispatch(request, *args, **kwargs)

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
        all_recipes = RecipePosts.objects.filter(uploaded_by=user_information).order_by('-date_created')
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
    # This view is used to delete the recipe post
    # This will redirect the user to the login page if they are not logged in
    login_url = reverse_lazy('user_login')

    # This is used to delete the recipe post
    def post(self, request, post_id, *args, **kwargs):
        # It gathers the recipe then calls for the delete function in the Models file.
        recipe = get_object_or_404(RecipePosts, pk=post_id)
        recipe.delete()
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
        all_recipes = Like.objects.filter(user=self.request.user.id).order_by("-liked_at")
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
        context['user_profile'] = User.objects.filter(id=user_id).get()
        context['user'] = self.request.user
        context['recipes'] = custom_paginate_qs(RecipePosts.objects.filter(uploaded_by=user_id).order_by("title"), page)
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
            queryset = queryset.filter(title__icontains=search_value).order_by('title')
        return queryset

    def get_context_data(self, **kwargs):
        # This gathers all the information of the recipe posts
        context = super().get_context_data(**kwargs)
        # it checks the search value
        search_value = self.request.GET.get('search_value', '')
        page = self.request.GET.get('page', 1)

        if search_value:
            # It will display the searched item the user is looking for
            queryset = RecipePosts.objects.filter(title__icontains=search_value).order_by("title")
        else:
            # if the user has not searched anything yet, it will display all the recipes on the site
            queryset = RecipePosts.objects.all().order_by("title")

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


def generate_recipe_pdf(request, recipe_id):
    # This is to create a PDF document for the recipe the user wants to save if they want to print it or share a hard
    # copy to their friends and family.
    recipe = get_object_or_404(RecipePosts, id=recipe_id)
    directions = recipe.directions.split('§')
    ingredients = recipe.ingredients.split('§')
    buffer = io.BytesIO()
    SimpleDocTemplate(buffer, pagesize=letter)
    font_path = os.path.join(settings.BASE_DIR, 'recipes/static/fonts')

    # Here are the downloaded font styles that will be used in the PDF.
    pdfmetrics.registerFont(TTFont('BarlowSemiCondensed', os.path.join(font_path, 'BarlowSemiCondensed-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('BarlowSemiCondensedBold', os.path.join(font_path, 'BarlowSemiCondensed-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DancingScript', os.path.join(font_path, 'DancingScript-Regular.ttf')))

    # Below are all the styles for the font in the PDF. It sets it for the PDF.
    styles = getSampleStyleSheet()
    # Style for the Title of the Recipe
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontName='BarlowSemiCondensedBold',
        fontSize=20,
        textColor=colors.HexColor('#0e342a'),
        spaceAfter=14,
        alignment=1
    )
    # Style for the subheadings for Directions and Ingredients
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading4'],
        fontName='BarlowSemiCondensedBold',
        fontSize=18,
        textColor=colors.HexColor('#8f5b2e'),
        spaceAfter=10,
    )
    # Style for the ingredients being displayed
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['BodyText'],
        fontName='BarlowSemiCondensed',
        fontSize=12,
        spaceAfter=12,
        alignment=4
    )
    # Style for the company logo/font style
    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontName='DancingScript',
        fontSize=25,
        textColor=colors.HexColor('#8a582d'),
        alignment=1,
        spaceAfter=30
    )
    # Style for the description of the dish
    description_style = ParagraphStyle(
        'DescriptionStyle',
        parent=styles['Normal'],
        fontName='BarlowSemiCondensed',
        fontSize=12,
        alignment=1,
        spaceAfter=5,
        leading=15
    )
    # Style for the nuber step for the directions
    step_style = ParagraphStyle(
        'StepStyle',
        parent=styles['Normal'],
        fontName='BarlowSemiCondensedBold',
        fontSize=12,
        textColor=colors.HexColor('#113f33'),
        spaceAfter=10,
    )

    # This is to create a canvas to draw on the custom elements on the PDF.
    width, height = letter
    c = canvas.Canvas(buffer, pagesize=letter)
    left_padding = 2 * cm
    right_padding = 2 * cm
    bottom_margin = 2 * cm
    top_margin = 2 * cm

    # This displays the company name on the PDF when it is created.
    company_name = "DishDelve"
    company_p = Paragraph(company_name, company_style)
    company_frame = Frame(0, height - 1.8 * cm, width, 1.5 * cm, showBoundary=0)
    company_frame.addFromList([company_p], c)

    # This is to display the image of the food from the recipe. It gathers the Food Recipe URL.
    image_url = recipe.food_image.url
    if not image_url.startswith(('http://', 'https://')):
        image_url = f"{request.scheme}://{request.get_host()}{image_url}"
    img_data = requests.get(image_url).content
    img = PILImage.open(io.BytesIO(img_data))

    # This is the set height and width of the image that should be displayed
    target_width = int(17.13 * cm)
    target_height = int(6.91 * cm)

    # This is to calculate the aspect ratio of the image and the target dimensions
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    # It will then resize and crop the image to fit target dimensions with object-fit: cover effect in CSS
    if img_ratio > target_ratio:
        # If the image is wider than target area
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        # If the image is taller than target area
        new_width = target_width
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), PILImage.LANCZOS)

    # This is to center the cropped image
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = (new_width + target_width) / 2
    bottom = (new_height + target_height) / 2
    img = img.crop((left, top, right, bottom))

    # This is to create the round corners
    mask = PILImage.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=25, fill=255)
    img.putalpha(mask)

    # This is to save the new temp image that was created onto the PDF
    img.save("temp_recipe_image.png")
    img_width = 17.13 * cm
    img_height = 6.91 * cm
    img_x = (width - img_width) / 2
    img_y = height - img_height - 2 * cm

    # Here is the code where it adds the image to the canvas on the PDF
    c.drawImage("temp_recipe_image.png", img_x, img_y, img_width, img_height, mask='auto')
    c.setStrokeColor(colors.HexColor('#0b2e13'))
    c.setLineWidth(4)
    c.roundRect(img_x, img_y, img_width, img_height, radius=25, stroke=1, fill=0)

    # This is to display the recipe title on the PDF
    title_p = Paragraph(recipe.title, title_style)
    title_frame = Frame(0, img_y - 1.8 * cm, width, 1.5 * cm, showBoundary=0)
    title_frame.addFromList([title_p], c)

    # This is to display the description of the recipe on the PDF
    description_p = Paragraph(recipe.dish_description, description_style)
    description_frame = Frame(left_padding, img_y - 7.5 * cm, width - left_padding - right_padding, 6 * cm,
                              showBoundary=0)
    description_frame.addFromList([description_p], c)
    y_position = img_y - 5 * cm

    # This is to set the information regarding the recipe
    data_info = [
        ['Created By:', 'Prep Time:', 'Cook Time:', 'Servings:', 'Category:'],
        [recipe.uploaded_by.get_full_name(), recipe.prep_time, recipe.cook_time, recipe.servings, recipe.category]
    ]

    # This is to create the table, which will store the data_info in an invisible table.
    table_info = Table(data_info, colWidths=[3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm])
    table_info.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'BarlowSemiCondensedBold'),
        ('FONTNAME', (0, 1), (-1, -1), 'BarlowSemiCondensed'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#113f33')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#8a582d')),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
    ]))
    # This then sets and creates the table onto the PDF
    table_info.wrapOn(c, width, height)
    table_info.drawOn(c, left_padding, y_position - 0.1 * cm)
    y_position -= 0.5 * cm

    # This function changes between the two columns for the ingredients
    def get_frame(column):
        return left_frame if column == 0 else right_frame

    # Initialize variables for ingredients
    column = 0  # 0 for left column, 1 for right column

    # This is to define the left and right frames for the Ingredients
    left_frame = Frame(left_padding, bottom_margin, (width / 2) - left_padding - right_padding - (0.5 * cm),
                       y_position - 1.3 * cm - bottom_margin, showBoundary=0)
    right_frame = Frame((width / 2) + (0.5 * cm), bottom_margin, (width / 2) - right_padding - (0.5 * cm),
                        y_position - 1.3 * cm - bottom_margin, showBoundary=0)

    # This is to create the Title of Ingredients and adds it to the PDF
    ingredient_title_p = Paragraph("Ingredients:", subtitle_style)
    ingredient_title_frame = Frame(left_padding, y_position - 6 * cm, width - left_padding - right_padding, 6 * cm,
                                   showBoundary=0)
    ingredient_title_frame.addFromList([ingredient_title_p], c)
    y_position -= 1.5 * cm

    # This loops through all the ingredients and displays it on the PDF
    for ingredient in ingredients:
        ingredient_p = Paragraph(f"- {ingredient}", normal_style)
        width_available = (width / 2) - left_padding - right_padding - (0.5 * cm)
        text_height = ingredient_p.wrap(width_available, height)[1]
        frame = get_frame(column)
        frame.addFromList([ingredient_p], c)
        y_position -= text_height + 0.5 * cm
        column = 1 - column  # Switch column (0 to 1, 1 to 0)

    # This creates a new page on the PDF document to continue with the Directions of the Recipe.
    c.showPage()
    y_position = height

    # This is to create the Title of Directions and adds it to the PDF
    direction_title_p = Paragraph("Directions:", subtitle_style)
    direction_title_frame = Frame(left_padding, height - 2 * cm, width - left_padding - right_padding, 1.5 * cm,
                                  showBoundary=0)
    direction_title_frame.addFromList([direction_title_p], c)

    # This loops through all the directions and displays it onto the PDF with the step number as well
    for counter, direction in enumerate(directions, start=1):
        # Check if the y_position goes below the bottom margin to continue on a new page.
        if y_position < bottom_margin:
            c.showPage()
            y_position = height - top_margin
        counter_p = Paragraph(f"STEP {counter}:", step_style)
        direction_p = Paragraph(direction, normal_style)
        width_available = width - left_padding - right_padding
        text_height = direction_p.wrap(width_available, height)[1]
        counter_frame = Frame(left_padding, y_position - 1.3 * cm - bottom_margin, width - left_padding - right_padding,
                              1.5 * cm,
                              showBoundary=0)
        direction_frame = Frame(left_padding, y_position - 1.8 * cm - bottom_margin,
                                width - left_padding - right_padding, 1.5 * cm,
                                showBoundary=0)
        counter_frame.addFromList([counter_p], c)
        direction_frame.addFromList([direction_p], c)
        y_position -= text_height + 1 * cm

    # This then saves the canvas that was created, and it then creates the PDF document and saves it by the recipe name
    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'{recipe.title}.pdf')
