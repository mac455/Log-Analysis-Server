from flask import Flask
from models import db  # Import db from models.py

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///logs.db"
    
    db.init_app(app)  # Initialize SQLAlchemy properly

    # Import blueprint inside function to avoid circular import
    from routes import logs  
    app.register_blueprint(logs)

    with app.app_context():
        db.create_all()  # Ensure database tables are created

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
