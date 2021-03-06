from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'checkout'

    # Override the ready method to import our signals module
    def ready(self):
        import checkout.signals
