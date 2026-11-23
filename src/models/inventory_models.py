from src.extensions import db


class BookModel(db.Model):
    __tablename__ = "books"
    __table_args__ = {"schema": "inventory"}

    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.Text, unique=True, nullable=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    publisher = db.Column(db.Text, nullable=False)
    publication_year = db.Column(db.SmallInteger, nullable=True)
    dewey_code = db.Column(db.Text, nullable=True)
    is_braille = db.Column(db.Boolean, nullable=False, default=False)
    is_audiobook = db.Column(db.Boolean, nullable=False, default=False)
    classification_system = db.Column(db.Text, nullable=False, server_default="Dewey")

    items = db.relationship(
        "ItemModel", backref="book", lazy=True, cascade="all, delete-orphan"
    )
    interests = db.relationship(
        "InterestModel", backref="book", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<BookModel id={self.id} title='{self.title}'>"


class ItemModel(db.Model):
    __tablename__ = "items"
    __table_args__ = {"schema": "inventory"}

    id = db.Column(db.BigInteger, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("inventory.books.id"), nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    shelf_location = db.Column(db.Text, nullable=False)
    entry_date = db.Column(
        db.Date, nullable=False, server_default=db.func.current_date()
    )

    def __repr__(self):
        return f"<ItemModel id={self.id} book_id={self.book_id}>"


class InterestModel(db.Model):
    __tablename__ = "interests"
    __table_args__ = {"schema": "inventory"}

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("inventory.books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("core.users.id"), nullable=False)

    def __repr__(self):
        return f"<InterestModel user_id={self.user_id} book_id={self.book_id}>"
