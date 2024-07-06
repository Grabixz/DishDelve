from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import os
from PIL import Image

from recipes.models import RecipePosts, Comments

User = get_user_model()


class RegisterForm(UserCreationForm):
    # This is the form for creating a new user
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'input-field'})
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'input-field'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'input-field'})
    )

    class Meta:
        # It calls the model User and stores it into the following fields
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    # This is to check that the email doesn't already exist in the database
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        # This saves the information and saves it to the user model
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    # This is the form that the user will use when they log into the website
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'input-field'})
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'input-field'})
    )


class EditAccountInformationForm(forms.ModelForm):
    # This is the form the user will use when they want to edit their accounts information

    # This is to get the new password the user wants to use incase they want to change it to something
    # more secure
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        # This calls the User model and uses the following fields from the model and displays the information that is
        # stored in the model in the field
        model = User
        fields = ['first_name', 'last_name', 'profile_picture', 'bio', 'date_of_birth', 'country', 'gender']
        widgets = {
            # This sets the type form input the form must be and the set attribute to it
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # This is to set the following fields requirement to false
        super(EditAccountInformationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['profile_picture'].required = False
        self.fields['bio'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['country'].required = False
        self.fields['gender'].required = False


class RecipeCreationForm(forms.ModelForm):
    # This is the form that will be used when the user will create a new recipe
    TIME_UNIT_CHOICES = [
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
    ]

    prep_time_value = forms.IntegerField(
        label='Prep Time',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '59'}),
    )
    prep_time_unit = forms.ChoiceField(
        choices=TIME_UNIT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cook_time_value = forms.IntegerField(
        label='Cook Time',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '59'}),
    )
    cook_time_unit = forms.ChoiceField(
        choices=TIME_UNIT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        # This calls the RecipePosts model and gathers the following fields from the model
        model = RecipePosts
        fields = ['title', 'category', 'dish_description', 'ingredients', 'directions', 'food_image',
                  'servings', 'tips']
        widgets = {
            # It then creates the following form fields and declares the following attributes for the fields
            'title': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 50}),
            'category': forms.Select(choices=[
                ('breakfast', 'Breakfast'),
                ('snacks', 'Snacks'),
                ('lunch', 'Lunch'),
                ('dinner', 'Dinner'),
                ('dessert', 'Dessert')
            ], attrs={'class': 'form-control'}),
            'dish_description': forms.Textarea(attrs={'class': 'form-control', 'maxlength': 280}),
            'ingredients': forms.HiddenInput(attrs={'class': 'form-control'}),
            'directions': forms.HiddenInput(attrs={'class': 'form-control'}),
            'food_image': forms.FileInput(attrs={'class': 'form-control'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'tips': forms.Textarea(attrs={'class': 'form-control', 'required': False}),
        }

    def __init__(self, *args, **kwargs):
        # This sets the following field requirement to false or true
        super(RecipeCreationForm, self).__init__(*args, **kwargs)
        self.fields['title'].required = True
        self.fields['category'].required = True
        self.fields['dish_description'].required = True
        self.fields['ingredients'].required = True
        self.fields['directions'].required = True
        self.fields['food_image'].required = True
        self.fields['tips'].required = False

    def clean_food_image(self):
        # This is to check that the image that is uploaded is the following file extension and that the image is not
        # corrupted or damaged.
        food_image = self.cleaned_data.get('food_image')

        if food_image:
            # This is to check the file extension type
            ext = os.path.splitext(food_image.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if ext not in valid_extensions:
                raise ValidationError('Unsupported file extension. Please upload a JPG or PNG image.')

            # This is to check if the image is not damaged/corrupted
            try:
                img = Image.open(food_image)
                img.verify()  # This will verify the uploaded image
            except (IOError, SyntaxError):
                raise ValidationError('Upload a valid image. The file you uploaded was either not an image or a '
                                      'corrupted image.')

        return food_image

    def clean(self):
        cleaned_data = super().clean()
        # This will gather the prep time and value. It will then save it as a str
        prep_time_value = cleaned_data.get('prep_time_value')
        prep_time_unit = cleaned_data.get('prep_time_unit')
        if prep_time_unit == 'hours':
            cleaned_data['prep_time'] = f"{prep_time_value}hr"
        else:
            cleaned_data['prep_time'] = f"{prep_time_value}min"

        # This will gather the cooking time and value. It will then save it as a str
        cook_time_value = cleaned_data.get('cook_time_value')
        cook_time_unit = cleaned_data.get('cook_time_unit')
        if cook_time_unit == 'hours':
            cleaned_data['cook_time'] = f"{cook_time_value}hr"
        else:
            cleaned_data['cook_time'] = f"{cook_time_value}min"

        return cleaned_data

    def save(self, commit=True):
        # This then saves the form to the RecipePosts, but delays the commit to false. The continuation of the saving
        # will happen on the views file.
        instance = super().save(commit=False)
        instance.prep_time = self.cleaned_data['prep_time']
        instance.cook_time = self.cleaned_data['cook_time']
        if commit:
            instance.save()
        return instance


class SearchForm(forms.Form):
    # This is the form that will be used when the user wants to search for a recipe post
    search_value = forms.CharField(
        label='Search Recipe Title',
        error_messages={'required': ' '},
        max_length=50,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )


class CommentForm(forms.ModelForm):
    # This is the form that is created when a user wants to comment on a recipe post
    class Meta:
        # It calls the Comments model to create the body field as a form
        model = Comments
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control'}),
        }



