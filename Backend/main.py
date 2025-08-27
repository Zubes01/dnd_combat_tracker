import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import logging
app = FastAPI()

state = {
    "board_x_max": 14,
    "board_y_max": 14,
    "entities": [],
    "counter": 0
    }

# Store current location in memory (later: use DB)
test_location = {"x": 2, "y": 3}

# Keep track of websocket connections
active_connections: list[WebSocket] = []


# Custom broadcast function
async def broadcast(message):
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logging.info(f"WebSocket disconnected: {e}")
            disconnected.append(connection)
    for connection in disconnected:
        if connection in active_connections:
            active_connections.remove(connection)

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

@app.post("/remove_entity")
async def remove_entity(entity: dict):
    # Example entity: {"id": "4ac5safd"}
    if "id" not in entity:
        return {"error": "Entity must have id"}
    existing_entity = next((e for e in state["entities"] if e["id"] == entity["id"]), None)
    if not existing_entity:
        return {"error": "Entity not found"}
    state["entities"].remove(existing_entity)
    return {"message": "Entity removed", "entities": state["entities"]}

@app.get("/entities")
async def get_entities():
    return {"entities": state["entities"]}

@app.websocket("/ws_test")
async def websocket_test_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    # Send initial state when client connects
    await websocket.send_json({"type": "init", "location": test_location})

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            print(f"Received message: {data}")

            if data["type"] == "move":
                # Update game state
                test_location["x"] = data["x"]
                test_location["y"] = data["y"]

                # Broadcast new state to everyone
                await broadcast({"type": "update", "location": test_location})

    except WebSocketDisconnect:
        active_connections.remove(websocket)
