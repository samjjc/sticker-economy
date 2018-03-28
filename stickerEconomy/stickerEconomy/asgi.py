"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stickerEconomy.settings")

channel_layer = get_channel_layer()
application = get_channel_layer()

# import os
# import django
# from channels.routing import get_default_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stickerEconomy.settings")
# django.setup()
# application = get_default_application()