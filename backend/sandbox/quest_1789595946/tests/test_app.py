"""Integration tests for Flask application routes."""

import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"NutriPulse" in response.data

def test_api_tips_all(client):
    response = client.get("/api/tips")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "tips" in data
    assert "weight_loss" in data["tips"]
    assert "hydration" in data["tips"]

def test_api_tips_category(client):
    response = client.get("/api/tips?category=superfoods")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["category"] == "superfoods"
    assert len(data["tips"]) > 0

def test_api_calculate_valid(client):
    payload = {
        "gender": "male",
        "age": 25,
        "weight": 75.0,
        "height": 180.0,
        "activity_level": "moderate",
        "goal": "weight_loss",
        "diet_type": "high_protein"
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "bmi" in data
    assert "bmr" in data
    assert "tdee" in data
    assert "target_calories" in data
    assert "macros" in data
    assert data["macros"]["diet_type"] == "high_protein"

def test_api_calculate_invalid_data(client):
    payload = {
        "gender": "male",
        "age": -5,
        "weight": 75.0,
        "height": 180.0
    }
    response = client.post("/api/calculate", json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_api_meal_plan_valid(client):
    payload = {
        "calories": 2200,
        "diet_type": "low_carb"
    }
    response = client.post("/api/meal-plan", json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "meal_plan" in data
    assert len(data["meal_plan"]["meals"]) == 4

def test_api_meal_plan_invalid(client):
    payload = {
        "calories": 100
    }
    response = client.post("/api/meal-plan", json=payload)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
