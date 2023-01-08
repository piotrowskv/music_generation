from os import environ

from dotenv import load_dotenv

load_dotenv()


class Env:
    """
    Static class holding all environment variables. 
    """
    redis_hostname = environ.get("REDIS_HOSTNAME", "localhost")
    redis_port = int(environ.get("REDIS_PORT", "6379"))
