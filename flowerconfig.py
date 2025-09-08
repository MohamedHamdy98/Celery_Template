from dotenv import dotenv_values
config = dotenv_values(".env")

# config
port = 5555
max_tasks = 10000
auto_refresh = True
# db = "flower.db"

# auth
basic_auth = [f'admin:{config.get("CELERY_FLOWER_PASSWORD")}']