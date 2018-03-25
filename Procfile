release: python manage.py migrate --noinput
web: gunicorn stickerEconomy.wsgi --log-file -
web2: daphne stickerEconomy.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker -v2