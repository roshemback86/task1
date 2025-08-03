from fastapi import FastAPI
from app.core.flow_manager import FlowManager
from app.api.endpoints import register_routes

app = FastAPI(title="Flow Manager API", version="1.0.0")
flow_manager = FlowManager()
register_routes(app, flow_manager)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)