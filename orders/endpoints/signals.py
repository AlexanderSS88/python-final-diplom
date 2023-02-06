from django.dispatch import Signal

new_user_registered = Signal(providing_args=['user_id'],)