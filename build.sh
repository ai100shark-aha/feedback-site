pip install gunicorn
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
echo "from django.contrib.auth import get_user_model; U=get_user_model(); U.objects.filter(username='mr0white').exists() or U.objects.create_superuser('mr0white','','admin1234')" | python manage.py shell