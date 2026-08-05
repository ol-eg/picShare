from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.onprem.inmemory import Redis

with Diagram(
    "App Structure — Module Coupling",
    show=False,
    outformat="png",
    filename="docs/module_diagram",
):
    with Cluster("picshare-app-1"):
        main = FastAPI("main.py\n(routes)")

        templates = Redis("templates/\n(Jinja2 HTML)")
        redoc = Redis("static/redoc_assets/\n(ReDoc bundle)")
        schemas = Python("schemas.py\n(Pydantic I/O)")
        auth = Python("auth.py\n(hashing, JWT)")
        img_utils = Python("image_utils.py\n(save, thumbnail)")
        models = Python("models.py\n(ORM: User, Image)")
        db = Python("database.py\n(engine, session)")

        main >> Edge(label="Jinja2") >> templates
        main >> Edge(label="StaticFiles") >> redoc
        main >> Edge(label="Pydantic") >> schemas
        main >> Edge(label="Depends") >> auth
        main >> Edge(label="Pillow") >> img_utils

        auth >> Edge(label="User model") >> models
        auth >> Edge(label="session") >> db