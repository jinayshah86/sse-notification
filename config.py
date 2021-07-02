import os
from dotenv import dotenv_values

CONFIG = {
    **dotenv_values(".env.default"),  # load default values
    **os.environ,  # override loaded values with environment variables
}
