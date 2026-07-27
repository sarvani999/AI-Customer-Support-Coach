import sys
import os

# Add project root path
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)


from flask import Flask
from routes import register_routes



app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)


register_routes(app)



if __name__ == "__main__":

    app.run(debug=True)