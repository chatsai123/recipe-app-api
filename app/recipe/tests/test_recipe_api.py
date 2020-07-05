from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sampe_tag(user, name='Main Course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sampe_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setup(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test tht authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setup(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@yahoo.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipers(self):
        """Test retrieving a list of recipes"""
        self.setup()
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        self.setup()
        user2 = get_user_model().objects.create_user(
            'other@yahoo.com',
            'password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail, Added self.setup() """
        self.setup()
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sampe_tag(user=self.user))
        recipe.ingredients.add(sampe_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
