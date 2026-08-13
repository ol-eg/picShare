from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.programming.framework import FastAPI
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.language import Python, Javascript

with Diagram(
    "picShare — Technology Stack",
    show=False,
    outformat="png",
    filename="docs/stack_diagram",
    direction="TB",
):
    dev = User("Developer / Tests\n(pytest, httpx)")

    with Cluster("Docker Compose"):
        with Cluster("picshare-app-1"):
            with Cluster("Frontend"):
                frontend = Javascript("Tailwind CSS + HTMX\n(Jinja2 templates)")
                api_docs = Javascript("Swagger UI / ReDoc\n(static bundle)")

            app = FastAPI("FastAPI / Uvicorn\n(ASGI router)")

            with Cluster("Service Layer\n(business logic)"):
                services = Python("services.py\n(image upload, state)")
                img_utils = Python("image_utils.py\n(thumbnail generation)")
                auth_lib = Python("auth.py\nbcrypt + JWT")

            with Cluster("Data Access Layer"):
                repos = Python("repositories.py\n(DB access)")
                orm = Python("SQLAlchemy / Alembic\n(async ORM + migrations)")

        with Cluster("picshare-db-1"):
            db = PostgreSQL("PostgreSQL 17")
            asyncpg = Python("asyncpg\n(async driver)")

    dev >> app
    app >> frontend
    app >> api_docs
    app >> Edge(label="routes call") >> services
    services >> Edge(label="save_upload") >> img_utils
    services >> Edge(label="hashing/JWT") >> auth_lib
    services >> repos
    repos >> orm
    orm >> Edge(label="queries") >> asyncpg
    asyncpg >> db