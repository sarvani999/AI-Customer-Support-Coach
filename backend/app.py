import os
import sys


# Add project root path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                __file__
            )
        )
    )
)


from flask import Flask

from routes import register_routes

from knowledge_routes import (
    register_knowledge_routes
)


app = Flask(
    __name__,
    template_folder=(
        "../frontend/templates"
    ),
    static_folder=(
        "../frontend/static"
    )
)


# Normal application routes
register_routes(
    app
)


# Knowledge Base routes
register_knowledge_routes(
    app
)


print(
    "\nREGISTERED FLASK ROUTES:"
)

print(
    app.url_map
)


if __name__ == "__main__":

    app.run(
        debug=True
    )