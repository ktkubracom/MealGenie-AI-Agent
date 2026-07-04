from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as recipe_router

app = FastAPI(
    title="MealGenie v2 Backend",
    description="The AI Swarm orchestrator for MealGenie.",
    version="2.0.0"
)

# Configure CORS so the Next.js frontend can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipe_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the MealGenie AI Backend API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
