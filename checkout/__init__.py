# Tell django the default config class for the app
# Without this line, django would'nt know about our
# custom ready method so our signals wouldn't work
# notice signals are imported within the config function
default_app_config = 'checkout.apps.CheckoutConfig'