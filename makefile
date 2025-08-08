prod:
	python manage.py makemigrations
	python manage.py migrate
	python manage.py runserver

dev:
	python manage.py runserver