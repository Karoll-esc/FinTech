"""
Simplified FastAPI app for testing GET /cards endpoint
TASK-033: Aplicación mínima para tests de API
"""
from fastapi import FastAPI
from src.routes.cards import router as cards_router

# Crear aplicación FastAPI mínima
app = FastAPI(title="Cards API Test")

# Registrar router de cards
app.include_router(cards_router)
