from flask import current_app
from flask_restful import Resource, abort, marshal_with
from ..fields.user import (
    getUserField, getUsersField, getFollowersField, getFollowingsField
)
from ..common.parsers import page_parser, post_aUser_parser
from ..common.auth import auth, can
from .. import User, Post, Comment, Follow, db


class aUser(Resource):
    method_decorators = {"post": [can("editinfo"), auth.login_required]}

    @marshal_with(getUserField)
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404, message="User not found.")
        return user

    @marshal_with(getUserField)
    def post(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404, message="User not found.")
        form = post_aUser_parser.parse_args()
        user.name = form["name"]
        user.age = form["age"]
        user.location = form["location"]
        user.about_me = form["about_me"]
        db.session.add(user)
        db.session.commit()
        return user


class Users(Resource):

    @marshal_with(getUsersField)
    def get(self):
        page = page_parser.parse_args()["page"]
        pagination = User.query.order_by(User.member_since.desc()).paginate(
            page,
            per_page=current_app.config.get("FLASK_USER_PER_PAGE", 20),
            error_out=False,
        )
        return pagination


class Followers(Resource):

    @marshal_with(getFollowersField)
    def get(self, username):
        page = page_parser.parse_args()["page"]
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404, message="User not found.")
        pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(
            page,
            per_page=current_app.config.get("FLASK_USER_PER_PAGE", 20),
            error_out=False,
        )
        users = [item.follower for item in pagination.items]
        pagination.items = users
        return pagination


class Followings(Resource):

    @marshal_with(getFollowingsField)
    def get(self, username):
        page = page_parser.parse_args()["page"]
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404, message="User not found.")
        pagination = user.followings.order_by(Follow.timestamp.desc()).paginate(
            page,
            per_page=current_app.config.get("FLASK_USER_PER_PAGE", 20),
            error_out=False,
        )
        users = [item.followed for item in pagination.items]
        pagination.items = users
        return pagination
