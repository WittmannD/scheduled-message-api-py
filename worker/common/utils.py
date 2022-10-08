import math
from datetime import timedelta, datetime

from sqlalchemy import and_

from web.api.models.BaseModel import db
from web.api.models import ScheduledMessageModel


def fetch_messages(period: int):
    now = datetime.utcnow()
    from_time, to_time = (
        now - timedelta(seconds=math.floor(period / 2)),
        now + timedelta(seconds=math.ceil(period / 2))
    )

    messages = ScheduledMessageModel.find_by(
        stmt=and_(
            ScheduledMessageModel.time_for_dispatch >= from_time,
            ScheduledMessageModel.time_for_dispatch <= to_time,
            ScheduledMessageModel.status == 'await'
        )
    )

    for message in messages:
        print(message)

        message.status = 'processed'
        db.session.add(message)

    db.session.commit()
    return messages
