from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI() 

# Хранилище активных комнат: { room_id: [список_вебсокетов] }
rooms = {}

@app.get("/")
async def root():
    return {"status": "Checkers Server is running"}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    
    if room_id not in rooms:
        rooms[room_id] = []
    
    # Если в комнате уже есть 2 игрока, отключаем третьего лишнего
    if len(rooms[room_id]) >= 2:
        await websocket.send_text(json.dumps({"status": "error", "message": "Room is full"}))
        await websocket.close()
        return

    rooms[room_id].append(websocket)
    
    try:
        while True:
            # Ждем сообщение от одного из игроков (строку с ходом)
            data = await websocket.receive_text()
            
            # Пересылаем это сообщение второму игроку в этой же комнате
            for client in rooms[room_id]:
                if client != websocket:
                    await client.send_text(data)
                    
    except WebSocketDisconnect:
        # Если игрок отключился, удаляем его из комнаты
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:
            del rooms[room_id]