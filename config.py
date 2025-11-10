import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ecommerce.db")
JWT_EXP_SECONDS = int(os.getenv("JWT_EXP_SECONDS", 60*60*24))
