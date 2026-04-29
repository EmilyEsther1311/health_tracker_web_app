from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.orm as so
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint
from flask_login import UserMixin
from app import db, login

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, index= True, unique=True)
    email: Mapped[str] = mapped_column(db.String, index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(db.String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    activities: Mapped[list['Activity']] = relationship(back_populates="user", cascade="all, delete-orphan")
    body_measurements: Mapped[list['BodyMeasurement']] = relationship(back_populates="user", cascade="all, delete-orphan")
    leader_groups: Mapped[list['SupportGroup']] = relationship(back_populates="leader", cascade="all, delete-orphan")
    groups: Mapped[list['UserGroup']] = relationship(back_populates="member", cascade="all, delete-orphan")


class SupportGroup(db.Model):
    __tablename__ = 'support_group'
    __table_args__ = (UniqueConstraint('name', 'leader_id'),)

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String, index=True, nullable=False)
    leader_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))

    members: Mapped[list['UserGroup']] = relationship(back_populates="support_group", cascade="all, delete-orphan")

    leader: Mapped['User'] = relationship(back_populates="leader_groups", foreign_keys=[leader_id],)


class UserGroup(db.Model):
    __tablename__ = 'user_group'

    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'), primary_key=True)
    s_group_id: Mapped[int] = mapped_column(db.ForeignKey('support_group.id'), primary_key=True)

    member: Mapped['User'] = relationship(back_populates="groups", foreign_keys=[user_id],)
    support_group: Mapped['SupportGroup'] = relationship(back_populates="members", foreign_keys=[s_group_id],)

class ExerciseType(db.Model):
    __tablename__ = 'exercise_type'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    description: Mapped[str] = mapped_column(db.String, index=True, unique=True)
    duration: Mapped[int] = mapped_column(db.Integer, index=True)
    intensity: Mapped[int] = mapped_column(db.Integer, index=True)
    attachment_filename: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)

    activities: Mapped[list['Activity']] = relationship(back_populates="exercise_type")


class Activity(db.Model):
    __tablename__ = 'activity'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(db.DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(db.DateTime, index=True)
    notes: Mapped[str] = mapped_column(db.String, index=True, nullable=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))
    exercise_type_id: Mapped[int] = mapped_column(db.ForeignKey('exercise_type.id'))

    user: Mapped[User] = relationship(back_populates="activities", foreign_keys=[user_id],)
    exercise_type: Mapped['ExerciseType'] = relationship(back_populates="activities", foreign_keys=[exercise_type_id],)

class BodyMeasurement(db.Model):
    __tablename__ = 'body_measurement'
    __table_args__ = (UniqueConstraint('user_id', 'timestamp'),)

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('user.id'))
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, index=True)
    weight: Mapped[float] = mapped_column(db.Float, index=True)
    pulse: Mapped[int] = mapped_column(db.Integer, index=True)

    user: Mapped['User'] = relationship(back_populates="body_measurements", foreign_keys=[user_id], )


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

