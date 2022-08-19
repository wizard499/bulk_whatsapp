from flask import Flask, render_template
from controllers.send_msg import send


app = Flask(__name__)
app.register_blueprint(send)



if __name__ == '__main__':
    app.run(debug=True)
