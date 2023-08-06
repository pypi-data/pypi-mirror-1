

def main():
    from celery.loaders.default import Loader
    loader = Loader()
    conf = loader.read_configuration()
    from django.core.management import call_command, setup_environ
    print("Creating database tables...")
    setup_environ(conf)
    call_command("syncdb")

if __name__ == "__main__":
    main()
