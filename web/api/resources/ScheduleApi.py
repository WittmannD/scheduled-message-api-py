from flask import jsonify, make_response
from flask_restful import Resource
from http import HTTPStatus
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from webargs.flaskparser import use_args
from webargs import fields, validate

from web.api.common.decorators import token_required
from web.api.models.BaseModel import db
from web.api.models.ScheduledMessageModel import ScheduledMessageModel


class ScheduleApi(Resource):
    @token_required
    @use_args(
        {
            'peer_id': fields.String(required=True),
            'order_by': fields.List(fields.String(), missing=['created_at desc']),
            'page': fields.Integer(missing=1),
            'per_page': fields.Integer(missing=99)
        },
        location='query'
    )
    def get(self, current_user, args):
        messages = ScheduledMessageModel.find_paginate_and_order_by(
            page=args.get('page'),
            per_page=args.get('per_page'),
            order_by=args.get('order_by'),
            user_id=current_user.get('user_id'),
        )

        return make_response(jsonify([message.to_dict() for message in messages]), HTTPStatus.OK)

    @token_required
    @use_args(
        {
            'peer_id': fields.String(required=True),
            'content': fields.String(required=True, validate=validate.Length(min=1, max=10000)),
            'payload': fields.String(missing=''),
            'time_for_dispatch': fields.DateTime(required=True)
        },
        location='json'
    )
    def post(self, current_user, args):
        message = ScheduledMessageModel(
            user_id=current_user.get('user_id'),
            peer_id=args['peer_id'],
            content=args['content'],
            payload=args['payload'],
            token=current_user.get('token'),
            time_for_dispatch=args['time_for_dispatch'],
        )

        message.save_to_db()

        return make_response(jsonify(message.to_dict()), HTTPStatus.CREATED)

    @token_required
    @use_args(
        {'ids': fields.List(fields.Integer(), required=True)},
        location='json'
    )
    def delete(self, current_user, args):
        db.session.query(ScheduledMessageModel).filter(
            and_(
                ScheduledMessageModel.uid.in_(args.get('ids')),
                ScheduledMessageModel.user_id == current_user.get('user_id')
            )
        ).delete()

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

        else:
            return make_response(None, HTTPStatus.NO_CONTENT)
