import os

from dotenv import load_dotenv
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from src import initialize_app
from src.extensions import db
from src.models.core_models import UserModel

load_dotenv()

if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql://postgres:postgres@localhost:5432/biblioteca_db"
    )


app = initialize_app()


def init_db_and_seed() -> None:
    with app.app_context():
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS core;"))
        db.session.execute(text("CREATE SCHEMA IF NOT EXISTS inventory;"))
        db.session.commit()

        db.create_all()

        admin = db.session.query(UserModel).filter_by(username="admin").first()
        hashed_pw = generate_password_hash("admin123")

        if not admin:
            admin_user = UserModel()
            admin_user.username = "admin"
            admin_user.password_hash = hashed_pw
            admin_user.full_name = "Administrador Principal"
            admin_user.is_admin = True
            admin_user.is_active = True
            db.session.add(admin_user)
        else:
            admin.password_hash = hashed_pw
            admin.full_name = "Administrador Principal"
            admin.is_admin = True
            admin.is_active = True

        db.session.commit()


if __name__ == "__main__":
    init_db_and_seed()
