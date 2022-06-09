from api import create_app
from helpers import initiate_logger, print_exception

logger = initiate_logger("entrypoint")
try:
    app = create_app()
except Exception as e:
    print_exception(logger, e)
