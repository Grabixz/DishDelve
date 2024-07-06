import os

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

COUNTRY_CHOICES = [
    ('Afghanistan', 'Afghanistan'),
    ('Albania', 'Albania'),
    ('Algeria', 'Algeria'),
    ('Andorra', 'Andorra'),
    ('Angola', 'Angola'),
    ('Antigua and Barbuda', 'Antigua and Barbuda'),
    ('Argentina', 'Argentina'),
    ('Armenia', 'Armenia'),
    ('Australia', 'Australia'),
    ('Austria', 'Austria'),
    ('Azerbaijan', 'Azerbaijan'),
    ('Bahamas', 'Bahamas'),
    ('Bahrain', 'Bahrain'),
    ('Bangladesh', 'Bangladesh'),
    ('Barbados', 'Barbados'),
    ('Belarus', 'Belarus'),
    ('Belgium', 'Belgium'),
    ('Belize', 'Belize'),
    ('Benin', 'Benin'),
    ('Bhutan', 'Bhutan'),
    ('Bolivia', 'Bolivia'),
    ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'),
    ('Botswana', 'Botswana'),
    ('Brazil', 'Brazil'),
    ('Brunei', 'Brunei'),
    ('Bulgaria', 'Bulgaria'),
    ('Burkina Faso', 'Burkina Faso'),
    ('Burundi', 'Burundi'),
    ('Cabo Verde', 'Cabo Verde'),
    ('Cambodia', 'Cambodia'),
    ('Cameroon', 'Cameroon'),
    ('Canada', 'Canada'),
    ('Central African Republic', 'Central African Republic'),
    ('Chad', 'Chad'),
    ('Chile', 'Chile'),
    ('China', 'China'),
    ('Colombia', 'Colombia'),
    ('Comoros', 'Comoros'),
    ('Congo (Congo-Brazzaville)', 'Congo (Congo-Brazzaville)'),
    ('Costa Rica', 'Costa Rica'),
    ('Croatia', 'Croatia'),
    ('Cuba', 'Cuba'),
    ('Cyprus', 'Cyprus'),
    ('Czechia (Czech Republic)', 'Czechia (Czech Republic)'),
    ('Democratic Republic of the Congo', 'Democratic Republic of the Congo'),
    ('Denmark', 'Denmark'),
    ('Djibouti', 'Djibouti'),
    ('Dominica', 'Dominica'),
    ('Dominican Republic', 'Dominican Republic'),
    ('Ecuador', 'Ecuador'),
    ('Egypt', 'Egypt'),
    ('El Salvador', 'El Salvador'),
    ('Equatorial Guinea', 'Equatorial Guinea'),
    ('Eritrea', 'Eritrea'),
    ('Estonia', 'Estonia'),
    ('Eswatini (fmr. "Swaziland")', 'Eswatini (fmr. "Swaziland")'),
    ('Ethiopia', 'Ethiopia'),
    ('Fiji', 'Fiji'),
    ('Finland', 'Finland'),
    ('France', 'France'),
    ('Gabon', 'Gabon'),
    ('Gambia', 'Gambia'),
    ('Georgia', 'Georgia'),
    ('Germany', 'Germany'),
    ('Ghana', 'Ghana'),
    ('Greece', 'Greece'),
    ('Grenada', 'Grenada'),
    ('Guatemala', 'Guatemala'),
    ('Guinea', 'Guinea'),
    ('Guinea-Bissau', 'Guinea-Bissau'),
    ('Guyana', 'Guyana'),
    ('Haiti', 'Haiti'),
    ('Honduras', 'Honduras'),
    ('Hungary', 'Hungary'),
    ('Iceland', 'Iceland'),
    ('India', 'India'),
    ('Indonesia', 'Indonesia'),
    ('Iran', 'Iran'),
    ('Iraq', 'Iraq'),
    ('Ireland', 'Ireland'),
    ('Israel', 'Israel'),
    ('Italy', 'Italy'),
    ('Jamaica', 'Jamaica'),
    ('Japan', 'Japan'),
    ('Jordan', 'Jordan'),
    ('Kazakhstan', 'Kazakhstan'),
    ('Kenya', 'Kenya'),
    ('Kiribati', 'Kiribati'),
    ('Kuwait', 'Kuwait'),
    ('Kyrgyzstan', 'Kyrgyzstan'),
    ('Laos', 'Laos'),
    ('Latvia', 'Latvia'),
    ('Lebanon', 'Lebanon'),
    ('Lesotho', 'Lesotho'),
    ('Liberia', 'Liberia'),
    ('Libya', 'Libya'),
    ('Liechtenstein', 'Liechtenstein'),
    ('Lithuania', 'Lithuania'),
    ('Luxembourg', 'Luxembourg'),
    ('Madagascar', 'Madagascar'),
    ('Malawi', 'Malawi'),
    ('Malaysia', 'Malaysia'),
    ('Maldives', 'Maldives'),
    ('Mali', 'Mali'),
    ('Malta', 'Malta'),
    ('Marshall Islands', 'Marshall Islands'),
    ('Mauritania', 'Mauritania'),
    ('Mauritius', 'Mauritius'),
    ('Mexico', 'Mexico'),
    ('Micronesia', 'Micronesia'),
    ('Moldova', 'Moldova'),
    ('Monaco', 'Monaco'),
    ('Mongolia', 'Mongolia'),
    ('Montenegro', 'Montenegro'),
    ('Morocco', 'Morocco'),
    ('Mozambique', 'Mozambique'),
    ('Myanmar (formerly Burma)', 'Myanmar (formerly Burma)'),
    ('Namibia', 'Namibia'),
    ('Nauru', 'Nauru'),
    ('Nepal', 'Nepal'),
    ('Netherlands', 'Netherlands'),
    ('New Zealand', 'New Zealand'),
    ('Nicaragua', 'Nicaragua'),
    ('Niger', 'Niger'),
    ('Nigeria', 'Nigeria'),
    ('North Korea', 'North Korea'),
    ('North Macedonia', 'North Macedonia'),
    ('Norway', 'Norway'),
    ('Oman', 'Oman'),
    ('Pakistan', 'Pakistan'),
    ('Palau', 'Palau'),
    ('Palestine State', 'Palestine State'),
    ('Panama', 'Panama'),
    ('Papua New Guinea', 'Papua New Guinea'),
    ('Paraguay', 'Paraguay'),
    ('Peru', 'Peru'),
    ('Philippines', 'Philippines'),
    ('Poland', 'Poland'),
    ('Portugal', 'Portugal'),
    ('Qatar', 'Qatar'),
    ('Romania', 'Romania'),
    ('Russia', 'Russia'),
    ('Rwanda', 'Rwanda'),
    ('Saint Kitts and Nevis', 'Saint Kitts and Nevis'),
    ('Saint Lucia', 'Saint Lucia'),
    ('Saint Vincent and the Grenadines', 'Saint Vincent and the Grenadines'),
    ('Samoa', 'Samoa'),
    ('San Marino', 'San Marino'),
    ('Sao Tome and Principe', 'Sao Tome and Principe'),
    ('Saudi Arabia', 'Saudi Arabia'),
    ('Senegal', 'Senegal'),
    ('Serbia', 'Serbia'),
    ('Seychelles', 'Seychelles'),
    ('Sierra Leone', 'Sierra Leone'),
    ('Singapore', 'Singapore'),
    ('Slovakia', 'Slovakia'),
    ('Slovenia', 'Slovenia'),
    ('Solomon Islands', 'Solomon Islands'),
    ('Somalia', 'Somalia'),
    ('South Africa', 'South Africa'),
    ('South Korea', 'South Korea'),
    ('South Sudan', 'South Sudan'),
    ('Spain', 'Spain'),
    ('Sri Lanka', 'Sri Lanka'),
    ('Sudan', 'Sudan'),
    ('Suriname', 'Suriname'),
    ('Sweden', 'Sweden'),
    ('Switzerland', 'Switzerland'),
    ('Syria', 'Syria'),
    ('Taiwan', 'Taiwan'),
    ('Tajikistan', 'Tajikistan'),
    ('Tanzania', 'Tanzania'),
    ('Thailand', 'Thailand'),
    ('Timor-Leste', 'Timor-Leste'),
    ('Togo', 'Togo'),
    ('Tonga', 'Tonga'),
    ('Trinidad and Tobago', 'Trinidad and Tobago'),
    ('Tunisia', 'Tunisia'),
    ('Turkey', 'Turkey'),
    ('Turkmenistan', 'Turkmenistan'),
    ('Tuvalu', 'Tuvalu'),
    ('Uganda', 'Uganda'),
    ('Ukraine', 'Ukraine'),
    ('United Arab Emirates', 'United Arab Emirates'),
    ('United Kingdom', 'United Kingdom'),
    ('United States of America', 'United States of America'),
    ('Uruguay', 'Uruguay'),
    ('Uzbekistan', 'Uzbekistan'),
    ('Vanuatu', 'Vanuatu'),
    ('Venezuela', 'Venezuela'),
    ('Vietnam', 'Vietnam'),
    ('Yemen', 'Yemen'),
    ('Zambia', 'Zambia'),
    ('Zimbabwe', 'Zimbabwe')
]

GENDER_CHOICE = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]


class CustomUserManager(BaseUserManager):
    # Method to create a regular user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Create a user instance with the provided email and extra fields
        user = self.model(email=email, **extra_fields)
        # Set the user's password
        user.set_password(password)
        # Save the user to the database
        user.save(using=self._db)
        return user

    # Method to create a superuser
    def create_superuser(self, email, password=None, **extra_fields):
        # Set default values for is_staff and is_superuser fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Ensure that is_staff is set to True
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        # Ensure that is_superuser is set to True
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Create and return a regular user with the superusers properties
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, help_text="Email address of user which is unique in database")
    first_name = models.CharField(max_length=50, help_text="First name of user")
    last_name = models.CharField(max_length=50, help_text="Last name of user")
    profile_picture = models.ImageField(upload_to='user_profile/', null=True, blank=True, help_text="Profile picture of user")
    bio = models.TextField(null=True, blank=True, help_text="Short bio of user when another user views profile")
    is_active = models.BooleanField(default=True, help_text="Whether user is active")
    is_staff = models.BooleanField(default=False, help_text="Whether user is staff")
    date_joined = models.DateTimeField(auto_now_add=True, help_text="Date the account was created")
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of birth of user")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, null=True, blank=True, help_text="Gender of user")
    country = models.CharField(max_length=80, choices=COUNTRY_CHOICES, null=True, blank=True, help_text="Country of user")

    # Set the custom user manager for this model
    objects = CustomUserManager()

    # Define the field that will be used as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    # List of fields that will be prompted when creating a user via createsuperuser
    REQUIRED_FIELDS = []

    # String representation of the user object
    def __str__(self):
        return self.email

    # Method to get the user's full name
    def get_full_name(self):
        return f'{self.first_name.title()} {self.last_name.title()}'


class RecipePosts(models.Model):
    title = models.CharField(max_length=60, help_text="Recipe Title/Name")
    category = models.CharField(max_length=10, help_text="Category of recipe")
    dish_description = models.TextField(help_text="The description of the recipe")
    servings = models.IntegerField(help_text="Number of servings")
    prep_time = models.CharField(max_length=10, help_text="Preparation time in a string format")
    cook_time = models.CharField(max_length=10, help_text="Cook time in a string format")
    ingredients = models.TextField(help_text="The ingredients to create the recipe. Split by '§' symbol.")
    directions = models.TextField(help_text="The directions to create the recipe. Split by '§' symbol.")
    food_image = models.ImageField(upload_to='food_images/', null=True, blank=True, help_text="Image of the Recipe")
    date_created = models.DateTimeField(auto_now_add=True, help_text="Date of creation set automatically")
    date_modified = models.DateTimeField(blank=True, null=True, help_text="Date of modification was made")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The user who created the recipe")
    tips = models.TextField(null=True, blank=True, help_text="Any tips for the recipe to make it better")

    # String representation of the recipe post
    def __str__(self):
        return self.title

    # Property to get the total number of likes for the recipe post
    @property
    def total_likes(self):
        return self.likes.count()

    # This function is used to delete the image path saved in the folder and the recipe information in model.
    def delete(self, *args, **kwargs):
        if self.food_image:
            if os.path.isfile(self.food_image.path):
                os.remove(self.food_image.path)
        super(RecipePosts, self).delete(*args, **kwargs)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The user who liked the recipe")
    recipe_post = models.ForeignKey(RecipePosts, related_name='likes', on_delete=models.CASCADE, help_text="Liked recipe")
    liked_at = models.DateTimeField(auto_now_add=True, help_text="Date of like set automatically")

    # Meta options to ensure a user can only like a specific post once
    class Meta:
        unique_together = ('user', 'recipe_post')


class Comments(models.Model):
    body = models.TextField(help_text="The body of the comment")
    created_on = models.DateTimeField(auto_now_add=True, help_text="Date of comment set automatically")
    post = models.ForeignKey(RecipePosts, on_delete=models.CASCADE, related_name='comments', help_text="Comment on Recipe post")
    author = models.ForeignKey(User, on_delete=models.CASCADE, help_text="The user who created the comment")
