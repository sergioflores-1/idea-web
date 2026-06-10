# ── IDEA Blog — Modelos SQLAlchemy ───────────────────────────────────────────
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name    = db.Column(db.String(100), nullable=False)
    last_name     = db.Column(db.String(100), default="")
    alias         = db.Column(db.String(50),  default="")
    init          = db.Column(db.String(4),   default="")
    is_admin      = db.Column(db.Boolean,     default=False)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display(self):
        return f"@{self.alias}" if self.alias else self.name

    def to_session(self):
        return {
            "id":       self.id,
            "name":     self.name,
            "email":    self.email,
            "init":     self.init,
            "alias":    self.alias,
            "display":  self.display,
            "is_admin": self.is_admin,
        }


class Article(db.Model):
    __tablename__   = "articles"
    id              = db.Column(db.Integer, primary_key=True)
    category        = db.Column(db.String(50),  nullable=False)
    featured        = db.Column(db.Boolean,     default=False)
    title           = db.Column(db.String(500), nullable=False)
    excerpt         = db.Column(db.Text,        nullable=False)
    content         = db.Column(db.Text,        nullable=False, default="")
    author          = db.Column(db.String(200), nullable=False)
    init            = db.Column(db.String(4),   default="")
    read_time       = db.Column(db.Integer,     default=5)
    views           = db.Column(db.Integer,     default=0)
    likes           = db.Column(db.Integer,     default=0)
    comments_count  = db.Column(db.Integer,     default=0)
    _tags           = db.Column("tags", db.Text, default="")
    created_at      = db.Column(db.DateTime,    default=datetime.utcnow)
    is_pdf          = db.Column(db.Boolean,     default=False)
    pdf_data        = db.Column(db.LargeBinary, nullable=True)

    @property
    def tags(self):
        return [t.strip() for t in self._tags.split(",") if t.strip()] if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = ",".join(value) if isinstance(value, list) else (value or "")

    # Alias para compatibilidad con templates que usan art.comments
    @property
    def comments(self):
        return self.comments_count


class Forum(db.Model):
    __tablename__ = "forums"
    id            = db.Column(db.Integer, primary_key=True)
    category      = db.Column(db.String(50),  nullable=False)
    solved        = db.Column(db.Boolean,     default=False)
    title         = db.Column(db.String(500), nullable=False)
    body          = db.Column(db.Text,        default="")
    author        = db.Column(db.String(200), nullable=False)
    init          = db.Column(db.String(4),   default="")
    votes         = db.Column(db.Integer,     default=0)
    views         = db.Column(db.Integer,     default=0)
    _tags         = db.Column("tags", db.Text, default="")
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    replies       = db.relationship("Comment", backref="forum", lazy=True,
                                    cascade="all, delete-orphan",
                                    order_by="Comment.created_at")

    @property
    def tags(self):
        return [t.strip() for t in self._tags.split(",") if t.strip()] if self._tags else []

    # Alias para templates que usan f.answers
    @property
    def answers(self):
        return len(self.replies)


class Event(db.Model):
    __tablename__ = "events"
    id          = db.Column(db.Integer,     primary_key=True)
    date_label  = db.Column(db.String(20),  nullable=False)   # "22 Ene"
    title       = db.Column(db.String(500), nullable=False)
    type        = db.Column(db.String(50),  default="Online")
    time        = db.Column(db.String(50),  default="")
    location    = db.Column(db.String(200), default="")
    description = db.Column(db.Text,        default="")
    registered  = db.Column(db.Integer,     default=0)
    capacity    = db.Column(db.Integer,     default=0)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)


class Panel(db.Model):
    __tablename__ = "panels"
    id          = db.Column(db.String(50),  primary_key=True)  # slug: "ia", "dev"
    emoji       = db.Column(db.String(10),  default="📌")
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text,        default="")
    members     = db.Column(db.Integer,     default=0)
    posts       = db.Column(db.Integer,     default=0)
    color       = db.Column(db.String(20),  default="#3b82f6")
    activity    = db.Column(db.String(100), default="")
    _tags       = db.Column("tags", db.Text, default="")
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)

    @property
    def tags(self):
        return [t.strip() for t in self._tags.split(",") if t.strip()] if self._tags else []


class Comment(db.Model):
    __tablename__ = "comments"
    id            = db.Column(db.Integer, primary_key=True)
    forum_id      = db.Column(db.Integer, db.ForeignKey("forums.id"), nullable=False)
    author        = db.Column(db.String(200), nullable=False)
    init          = db.Column(db.String(4),   default="")
    text          = db.Column(db.Text,        nullable=False)
    votes         = db.Column(db.Integer,     default=0)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    @property
    def timestamp(self):
        return self.created_at.strftime("%d %b %Y, %H:%M")

    def to_dict(self):
        return {
            "id":        self.id,
            "forum_id":  self.forum_id,
            "author":    self.author,
            "init":      self.init,
            "text":      self.text,
            "votes":     self.votes,
            "timestamp": self.timestamp,
        }
