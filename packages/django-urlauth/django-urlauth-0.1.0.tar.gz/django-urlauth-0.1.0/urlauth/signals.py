from django.dispatch import Signal

key_loaded = Signal(providing_args=['key', 'request'])
key_processed = Signal(providing_args=['key', 'request'])
