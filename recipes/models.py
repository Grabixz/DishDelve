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
        # Check if the email is provided
        if not email:
            raise ValueError('The Email field must be set')
        # Normalize the email address
        email = self.normalize_email(email)
        # Create a user instance with the provided email and extra fields
        user = self.model(email=email, **extra_fields)
        # Set the user's password
        user.set_password(password)
        # Save the user to the database
        user.save(using=self._db)
        # Return the created user instance
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

        # Create and return a regular user with the superuser's properties
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Define the email field as a unique identifier for the user
    email = models.EmailField(unique=True)
    # Define a field for the user's first name with a maximum length of 50 characters
    first_name = models.CharField(max_length=50)
    # Define a field for the user's last name with a maximum length of 50 characters
    last_name = models.CharField(max_length=50)
    # Define a field for the user's profile picture, with optional null and blank values
    profile_picture = models.ImageField(upload_to='user_profile/', null=True, blank=True)
    # Define a field for the user's bio, with optional null and blank values
    bio = models.TextField(null=True, blank=True)
    # Define a field to indicate if the user's account is active, default is True
    is_active = models.BooleanField(default=True)
    # Define a field to indicate if the user is staff, default is False
    is_staff = models.BooleanField(default=False)
    # Define a field to store the date and time the user joined, automatically set on creation
    date_joined = models.DateTimeField(auto_now_add=True)
    # Define a field for the user's date of birth, with optional null and blank values
    date_of_birth = models.DateField(null=True, blank=True)
    # Define a field for the user's gender with predefined choices, optional null and blank values
    gender = models.CharField(max_length=10, choices=GENDER_CHOICE, null=True, blank=True)
    # Define a field for the user's country with predefined choices, optional null and blank values
    country = models.CharField(max_length=80, choices=COUNTRY_CHOICES, null=True, blank=True)

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


# Model to represent a recipe post
class RecipePosts(models.Model):
    # Title of the recipe
    title = models.CharField(max_length=60)
    # Category of the dish (e.g., appetizer, dessert)
    category = models.CharField(max_length=10)
    # Description of the dish
    dish_description = models.TextField()
    # Number of servings
    servings = models.IntegerField()
    # Preparation time in a string format
    prep_time = models.CharField(max_length=10)
    # Cooking time in a string format
    cook_time = models.CharField(max_length=10)
    # Ingredients required for the recipe
    ingredients = models.TextField()
    # Directions to prepare the dish
    directions = models.TextField()
    # Image of the food, optional field
    food_image = models.ImageField(upload_to='food_images/', null=True, blank=True)
    # Date and time the recipe was created, set automatically
    date_created = models.DateTimeField(auto_now_add=True)
    # Date and time the recipe was last modified, optional field
    date_modified = models.DateTimeField(blank=True, null=True)
    # User who uploaded the recipe, linked to the User model
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # Additional tips for the recipe, optional field
    tips = models.TextField(null=True, blank=True)

    # String representation of the recipe post
    def __str__(self):
        return self.title

    # Property to get the total number of likes for the recipe post
    @property
    def total_likes(self):
        return self.likes.count()


# Model to represent a like on a recipe post
class Like(models.Model):
    # User who liked the recipe post, linked to the User model
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # The recipe post that was liked, linked to the RecipePosts model
    recipe_post = models.ForeignKey(RecipePosts, related_name='likes', on_delete=models.CASCADE)
    # Date and time the like was made, set automatically
    liked_at = models.DateTimeField(auto_now_add=True)

    # Meta options to ensure a user can only like a specific post once
    class Meta:
        unique_together = ('user', 'recipe_post')


# Model to represent a comment on a recipe post
class Comments(models.Model):
    # The text of the comment
    body = models.TextField()
    # Date and time the comment was created, set automatically
    created_on = models.DateTimeField(auto_now_add=True)
    # The recipe post that the comment is related to, linked to the RecipePosts model
    post = models.ForeignKey(RecipePosts, on_delete=models.CASCADE, related_name='comments')
    # User who wrote the comment, linked to the User model
    author = models.ForeignKey(User, on_delete=models.CASCADE)
