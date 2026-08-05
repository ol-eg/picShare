from diagrams import Diagram, Cluster
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

            with Cluster("Backend Libraries"):
                orm = Python("SQLAlchemy / Alembic\n(async ORM + migrations)")
                auth_lib = Python("bcrypt / passlib\n(password hashing)")
                jwt_lib = Python("python-jose / JWT\n(token generation)")
                img_lib = Python("Pillow\n(thumbnail generation)")

        with Cluster("picshare-db-1"):
            db = PostgreSQL("PostgreSQL 17")
            asyncpg = Python("asyncpg\n(async driver)")

    dev >> app
    app >> frontend
    app >> api_docs
    app >> orm
    app >> auth_lib
    app >> jwt_lib
    app >> img_lib
    orm >> asyncpg
    asyncpg >> db