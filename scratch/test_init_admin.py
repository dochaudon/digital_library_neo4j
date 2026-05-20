import os
import sys
sys.path.append(os.getcwd())

from flask import Flask
from services.auth_utils import init_bcrypt
from services.init_admin import init_admin_account

app = Flask(__name__)
init_bcrypt(app)

with app.app_context():
    print("Initializing admin account...")
    try:
        init_admin_account()
        print("Admin account initialized.")
    except Exception as e:
        import traceback
        traceback.print_exc()
