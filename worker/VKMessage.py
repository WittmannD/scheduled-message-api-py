import os

from aiovk import TokenSession, API
from vk_api.utils import get_random_id

from web.api.models.BaseModel import db
from web.api.models.ScheduledMessageModel import ScheduledMessageModel

VK_API_VERSION = os.environ.get('VK_API_VERSION', 5.131)


class VKMessage:
    def __init__(self, model: ScheduledMessageModel):
        self.model = model

    def _on_success(self):
        self.model.status = 'sent'
        db.session.add(self.model)

    def _on_error(self):
        self.model.status = 'failed'
        db.session.add(self.model)

    async def send(self):
        try:
            session = TokenSession(access_token=self.model.token)
            vk_api = API(session)

            kwargs = dict()
            kwargs.setdefault('peer_id', self.model.peer_id)
            kwargs.setdefault('message', self.model.content)
            kwargs.setdefault('payload', self.model.payload)
            kwargs.setdefault('random_id', get_random_id())
            kwargs.setdefault('v', VK_API_VERSION)

            await vk_api('messages.send', **kwargs)
            await session.close()

        except Exception as err:
            self._on_error()

        else:
            self._on_success()
