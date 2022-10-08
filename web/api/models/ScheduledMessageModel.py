from datetime import datetime

from web.api.models.BaseModel import BaseModel, db


class ScheduledMessageModel(BaseModel):
    __tablename__ = 'scheduled_message_model'

    user_id: str
    peer_id: str
    content: str
    payload: str
    time_for_dispatch: datetime
    token: str
    status: str

    user_id = db.Column(db.String)
    peer_id = db.Column(db.String)
    content = db.Column(db.String)
    payload = db.Column(db.String)
    time_for_dispatch = db.Column(db.DateTime(timezone=True))
    token = db.Column(db.String)
    status = db.Column(db.String, default='await')
