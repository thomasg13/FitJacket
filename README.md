# FitJacket

## How to Run Project locally
git clone
cd FitJacket
Create .env file with a OPENAI_API_KEY = YOUR_OPENAI_KEY SECRET_KEY = DJANGO_KEY DJANGO_DEBUG = TRUE for local host

pip install dotenv openai requests pytz

python manage.py makemigrations  
python manage.py migrate  
python manage.py runserver
