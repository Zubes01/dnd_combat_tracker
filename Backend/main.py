from fastapi import FastAPI

app = FastAPI()

state = {
    "board_x_max": 10,
    "board_y_max": 10,
    "entities": [],
    "counter": 0
    }

# Example endpoints to demonstrate state usage
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    return {"message": f"This is a test endpoint, the counter is at {state['counter']}"}

@app.post("/increment")
async def increment():
    state["counter"] += 1
    return {"message": f"Counter incremented to {state['counter']}"}

# now for actual game logic
@app.post("/add_entity")
async def add_entity(entity: dict):
    # Example entity: {"id": "4ac5safd", "x": 1, "y": 2}
    if not all(k in entity for k in ("id", "x", "y")):
       return {"error": "Entity must have id, x, and y"}
    if not (0 <= entity["x"] < state["board_x_max"]) or not (0 <= entity["y"] < state["board_y_max"]):
         return {"error": "Entity position out of bounds"}
    if any(e["id"] == entity["id"] for e in state["entities"]):
       return {"error": "Entity with this ID already exists"}
    if any(e["x"] == entity["x"] and e["y"] == entity["y"] for e in state["entities"]):
       return {"error": "Another entity is already at this position"}
        
    state["entities"].append(entity)
    return {"message": "Entity added", "entities": state["entities"]}

@app.post("/move_entity")
async def move_entity(entity: dict):
    # Example entity: {"id": "4ac5safd", "x": 1, "y": 2}
    if not all(k in entity for k in ("id", "x", "y")):
        return {"error": "Entity must have id, x, and y"}
    if not (0 <= entity["x"] < state["board_x_max"]) or not (0 <= entity["y"] < state["board_y_max"]):
        return {"error": "Entity position out of bounds"}
    existing_entity = next((e for e in state["entities"] if e["id"] == entity["id"]), None)
    if not existing_entity:
        return {"error": "Entity not found"}
    existing_entity["x"] = entity["x"]
    existing_entity["y"] = entity["y"]
    return {"message": "Entity moved", "entities": state["entities"]}