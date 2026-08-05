from diagrams import Diagram, Cluster
from diagrams.onprem.client import User
from diagrams.onprem.network import Internet
from diagrams.programming.framework import FastAPI
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.container import Docker
from diagrams.generic.os import LinuxGeneral

with Diagram(
    "picShare Architecture",
    show=False,
    outformat="png",
    filename="docs/architecture_diagram",
):
    user = User("Browser / Swagger")
    internet = Internet("Home Router (port 80)")

    with Cluster("Docker Compose"):
        fastapi = Docker("picshare-app-1\nFastAPI / Uvicorn")
        postgres = Docker("picshare-db-1\nPostgreSQL 17")
        storage = LinuxGeneral("Static Files\n/uploads /thumbnails")

    user >> internet >> fastapi
    fastapi >> postgres
    fastapi >> storage