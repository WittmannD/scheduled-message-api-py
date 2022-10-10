import os
from http import HTTPStatus

from flask import make_response, current_app
from flask_restful import Resource
from vk_api import VkApi

from webargs.flaskparser import use_args
from webargs import fields

from web.api.common.decorators import token_required

VK_API_VERSION = os.environ.get('VK_API_VERSION', '5.131')


class ChatApi(Resource):
    @token_required
    @use_args(
        {
            'peer_id': fields.String(required=True)
        },
        location='query'
    )
    def get(self, current_user, args):
        session = VkApi(token=current_user.get('token'))
        vk_api = session.get_api()
        current_app.logger.info(current_user, args)

        kwargs = dict()
        kwargs.setdefault('peer_ids', args.get('peer_id'))
        kwargs.setdefault('v', VK_API_VERSION)

        response = vk_api.messages.getConversationsById(**kwargs)

        make_response(response, HTTPStatus.OK)
