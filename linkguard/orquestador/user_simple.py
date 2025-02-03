from flask_login import UserMixin

from linkguard.orquestador.db import get_db

class UserSimple(UserMixin):
    def __init__(self, id_, name, email,password):
        self.id = id_
        self.name = name
        self.email = email
        self.password = password

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None
        
        user = User(
            id_=user[0], name=user[1], email=user[2], password=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, password):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, password) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, password),
        )
        db.commit()