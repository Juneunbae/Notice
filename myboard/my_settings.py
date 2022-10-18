import environ
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = environ.Env(DEBUG=(bool, True))

environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)

DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.mysql',
        'USER': env('DATABASE_USER'),
        'NAME': env('DATABASE_NAME'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
        'OPTIONS': {'charset': env('DATABASE_CHARSET')}
    }
}

SECRET_KEY = env('SECRET_KEY')