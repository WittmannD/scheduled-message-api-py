import math
import os
from datetime import timedelta, datetime

import sqlalchemy
from sqlalchemy import and_, orm
from sqlalchemy.ext.automap import automap_base

from web.api.models.ScheduledMessageModel import ScheduledMessageModel


class DB:
    base = automap_base()
    engine = sqlalchemy.create_engine(os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://'))
    base.prepare(autoload_with=engine, reflect=True)
    session = orm.Session(bind=engine)

    ScheduledMessageQuery = session.query(ScheduledMessageModel)

    @classmethod
    def fetch_messages(cls, period: int):
        now = datetime.utcnow()
        from_time, to_time = (
            now - timedelta(seconds=math.floor(period / 2)),
            now + timedelta(seconds=math.ceil(period / 2))
        )

        query = cls.ScheduledMessageQuery.filter(
            and_(
                ScheduledMessageModel.time_for_dispatch >= from_time,
                ScheduledMessageModel.time_for_dispatch <= to_time,
                ScheduledMessageModel.status == 'await'
            )
        )
        messages = query.order_by(ScheduledMessageModel.created_at.asc()).all()

        for message in messages:
            message.status = 'processed'
            cls.session.add(message)

        cls.commit()
        return messages

    @classmethod
    def commit(cls):
        cls.session.commit()
