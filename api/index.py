from flask import Flask
from services.auth.routes import auth
from services.instagram.profile import profile
from services.instagram.media import media
from services.instagram.post import post

from uuid import uuid4

def create_app():
    app = Flask(__name__)
    app.secret_key = str(uuid4())
    
    # Load configuration (API keys, secrets)
    app.config.from_object('config.MetaConfig')

    # Register blueprints
    app.register_blueprint(profile, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(media, url_prefix='/media')
    app.register_blueprint(post, url_prefix='/post')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)