from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Registrar blueprints
    from app.routes import web

    
    app.register_blueprint(web)
    
    
    return app