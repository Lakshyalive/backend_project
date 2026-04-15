from fastapi import FastAPI
from database import Base, engine
from routers import auth_routes, task_routes

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Task Management API", description="REST API with JWT auth and role-based access control", version="1.0.0")
app.include_router(auth_routes.router)
app.include_router(task_routes.router)

@app.get("/")
def root():
    return {
        "message": "Task Manager API is running!",
        "docs":    "Visit /docs for interactive API documentation (Swagger UI)"
    }
