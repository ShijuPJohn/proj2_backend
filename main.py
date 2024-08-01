from app import app
from controllers.auth_controllers import user_controller
from controllers.book_controllers import book_controller
from controllers.request_issue_controllers import request_controller

app.register_blueprint(user_controller)
app.register_blueprint(book_controller)
app.register_blueprint(request_controller)

if __name__ == '__main__':
    app.run(debug=True)