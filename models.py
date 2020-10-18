from flask_sqlalchemy import SQLAlchemy as SA


class SQLAlchemy(SA):
    def apply_pool_defaults(self, app, options):
        SA.apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(63), nullable=False, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    room_id = db.Column(db.String(63), nullable=True)


class Roles(db.Model):
    __tablename__ = 'roles'
    game_id = db.Column(db.String(63), nullable=False, primary_key=True)
    number = db.Column(db.Integer, nullable=False, primary_key=True)  # remain=0  hidden=-1,-2  invalid=-3,-4
    user_id = db.Column(db.String(63), nullable=False)  # user_id or "remain" or "hidden" or "invalid"
    role = db.Column(db.String(63), nullable=True)
    vote = db.Column(db.String(63), nullable=True)
    ability = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Integer, nullable=False, default=1)
