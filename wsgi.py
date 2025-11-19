from app import create_app

application = create_app()

# For Gunicorn
app = application

if __name__ == "__main__":
    application.run()