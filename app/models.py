from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import db
from app import login


# remember user login function
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sa.String(64), index=True,
                                                  unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sa.String(120), index=True,
                                               unique=True)
    password_hash: orm.Mapped[Optional[str]
                              ] = orm.mapped_column(sa.String(256))

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(
        back_populates='author')
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(140))
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, passwd):
        """Set a password for the user"""
        self.password_hash = generate_password_hash(passwd)

    def check_password(self, passwd):
        """Check user password to confirm user identity before login in"""
        return check_password_hash(self.password_hash, passwd)

    def avatar(self, size):
        """Return the user avatar"""
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(digest, size)


class Post(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sa.String(140))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(index=True,
                                                        default=lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey(User.id), index=True)

    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
