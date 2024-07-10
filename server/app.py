#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204
    
class Login(Resource):

    #def get(self):
        #pass

# This will log in a user who already exists in the database 
# and store their id in the session to keep them logged in
    def post(self):
        user = User.query.filter(
            User.username == request.get_json()['username']
        ).first()

        session['user_id'] = user.id
        return user.to_dict()

api.add_resource(Login, '/login')

# Now using the session hash, we allow the user to stay logged in even when the page reloads
# without this part the user will be logged out when the page refreshes
# because the login route only saves the id to session while the frontend saves it to state and when the page refreshes there is a change in state
class CheckSession(Resource):

    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict()
        else:
            return {}, 401

api.add_resource(CheckSession, '/check_session')

# Logout is very simple because all it does is set the session to None
class Logout(Resource):

    def delete(self): # just add this line!
        session['user_id'] = None
        return {'message': '204: No Content'}, 204

api.add_resource(Logout, '/logout')

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
