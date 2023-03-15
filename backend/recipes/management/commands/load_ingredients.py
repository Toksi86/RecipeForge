import logging
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Команда для загрузки стандартных ингридиентов в базу данных.'

    def handle(self, *args, **options):
        logger.info('Началась загрузка ингредиентов.')
        data_path = settings.BASE_DIR
        with open(f'{data_path}/data/ingredients.json',
                  'r',
                  encoding='utf-8'
                  ) as file:
            ingredients = json.loads(file.read())
            for ingredient in ingredients:
                Ingredient.objects.get_or_create(**ingredient)

        logger.info('Загрузка прошла успешно.')
