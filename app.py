import os
import logging
from dotenv import load_dotenv
from app import create_app

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = create_app(os.getenv('FLASK_ENV') or 'development')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])
