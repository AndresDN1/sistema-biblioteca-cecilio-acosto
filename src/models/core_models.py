from src.extensions import db


class UserModel(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint("char_length(username) >= 3", name="chk_username_length"),
        {"schema": "core"},
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    full_name = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<UserModel id={self.id} username='{self.username}'>"


class VisitorLogModel(db.Model):
    __tablename__ = "visitor_log"
    __table_args__ = {"schema": "core"}

    id = db.Column(db.BigInteger, primary_key=True)
    visitor_id = db.Column(db.Text, nullable=False)
    visitor_name = db.Column(db.Text, nullable=False)
    contact_info = db.Column(db.Text, nullable=True)
    check_in = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    def __repr__(self):
        return f"<VisitorLogModel id={self.id} visitor_name='{self.visitor_name}'>"
