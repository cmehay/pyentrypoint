import os


def clean_env():
    for key in os.environ.copy().keys():
        if key.startswith('ENTRYPOINT_'):
            del os.environ[key]
