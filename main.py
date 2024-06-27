from app import app
from controllers.auth_controllers import user_controller
from controllers.book_controllers import book_controller

app.register_blueprint(user_controller)
app.register_blueprint(book_controller)

if __name__ == '__main__':
    app.run(debug=True)