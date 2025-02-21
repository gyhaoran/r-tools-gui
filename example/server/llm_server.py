import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from uuid import uuid4
from contextlib import asynccontextmanager
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger("LLMServer") 

class TaskManager:
    """Async task lifecycle management (thread-safe)"""
    def __init__(self):
        self.active_tasks:  Dict[str, Dict] = {}
        self.task_status:  Dict[str, Dict] = defaultdict(dict)
        self.lock  = asyncio.Lock()

    async def register_task(self, request_id: str, task: asyncio.Task) -> None:
        """Register new processing task"""
        async with self.lock: 
            self.active_tasks[request_id]  = {
                "task": task,
                "start_time": datetime.now(), 
                "status": "processing"
            }

    async def cancel_task(self, request_id: str) -> bool:
        """Cancel existing task and cleanup resources"""
        async with self.lock: 
            if request_id not in self.active_tasks: 
                return False

            task_info = self.active_tasks.pop(request_id) 
            task_info["task"].cancel()
            return True

class ConnectionManager:
    """Enhanced WebSocket connection management"""
    def __init__(self):
        self.active_connections:  Dict[str, WebSocket] = {}  # request_id -> WebSocket
        self.interrupt_events  = defaultdict(asyncio.Event)

    async def disconnect(self, request_id: str):
        """Cleanup connection resources"""
        if request_id in self.active_connections:
            await self.active_connections[request_id].close()
            del self.active_connections[request_id]

    def get_websocket_by_request(self, request_id: str) -> Optional[WebSocket]:
        """Get WebSocket by request_id"""
        return self.active_connections.get(request_id, None)  if request_id else None

    async def associate_request(self, request_id: str, websocket: WebSocket):
        """Bind request to connection"""
        self.active_connections[request_id]  = websocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    app.state.task_manager  = TaskManager()
    app.state.connection_manager  = ConnectionManager()
    yield
    # Cleanup all tasks on shutdown
    async with app.state.task_manager.lock: 
        for request_id in list(app.state.task_manager.active_tasks.keys()): 
            await app.state.task_manager.cancel_task(request_id) 

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/llm") 
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint with proper connection handling"""
    manager = app.state.connection_manager 
    task_manager = app.state.task_manager

    try:
        while True:
            message = await websocket.receive_text() 
            logger.info(f"Received  message from {message}")

            data = json.loads(message) 
            request_id = data.get("request_id",  str(uuid4()))
            await manager.register_connection(request_id, websocket)            
            # Bind request to connection
            await manager.associate_request(request_id,  websocket)            
            await process_message(websocket, message, task_manager, manager)

    except WebSocketDisconnect as e:
        logger.info(f"Connection  {request_id} closed: code {e.code}") 
    except Exception as e:
        logger.error(f"Connection  error in {str(e)}", exc_info=True)
    finally:
        await manager.disconnect(request_id) 
        logger.info(f"Connection cleanup completed")

async def process_message(websocket: WebSocket, message: str,
                         task_manager: TaskManager, manager: ConnectionManager):
    """Message routing handler"""
    try:
        data = json.loads(message) 
        req_type = data.get("type",  0)
        if req_type == 0:
            await handle_new_request(websocket, data, task_manager, manager)
        elif req_type == 1:
            await handle_stop_request(data, task_manager, manager)

    except json.JSONDecodeError:
        await send_error(websocket, "Invalid JSON format")

async def handle_new_request(websocket: WebSocket, data: Dict,
                            task_manager: TaskManager, manager: ConnectionManager):
    """Handle new LLM request with connection validation"""
    request_id = data.get("request_id",  "")
    if not request_id:
        await send_error(websocket, "Missing request_id in payload")
        return

    if request_id in task_manager.active_tasks: 
        await send_error(websocket, "Duplicate request ID")
        return

    task = asyncio.create_task( 
        process_llm_stream(websocket, request_id, data, task_manager, manager)
    )
    await task_manager.register_task(request_id,  task)

async def handle_stop_request(data: Dict,
                             task_manager: TaskManager,
                             manager: ConnectionManager):
    """Handle stop request with connection validation"""
    request_id = data.get("request_id",  "")
    if await task_manager.cancel_task(request_id): 
        manager.interrupt_events[request_id].set() 
        # Cleanup connection mapping
        if request_id in manager.request_conn_map: 
            del manager.request_conn_map[request_id] 

async def process_llm_stream(websocket: WebSocket, request_id: str, data: Dict,
                            task_manager: TaskManager, manager: ConnectionManager):
    """LLM processing with connection awareness"""
    try:
        for i in range(1, 4):
            if manager.interrupt_events[request_id].is_set(): 
                break

            # Get current valid connection
            current_websocket = manager.get_websocket_by_request(request_id) 
            if not current_websocket:
                logger.warning(f"Connection  lost for request {request_id}")
                break

            await send_response_chunk(
                current_websocket,
                request_id,
                content=f"LLM Sever Response Content chunk {i}",
                is_end=(i == 3)
            )
            await asyncio.sleep(0.5)

    except asyncio.CancelledError:
        logger.info(f"Request  {request_id} cancelled")
    finally:
        await cleanup_request(request_id, task_manager, manager)

async def send_response_chunk(websocket: WebSocket, request_id: str,
                             content: str, is_end: bool):
    """Safe response sending with connection check"""
    try:
        payload = {
            "request_id": request_id,
            "type": 0,
            "content": content,
            "is_end": is_end
        }
        if is_end:
            payload["commands"] = generate_commands()
        
        await websocket.send_text(json.dumps(payload)) 
    except RuntimeError as e:
        logger.error(f"Send  failed for {request_id}: {str(e)}")
 
def generate_commands() -> list:
    """Generate sample commands"""
    return [
        {"type": "SAVE_RESULT", "target": "history.db"}, 
        {"type": "CLEANUP", "resources": ["temp_cache"]}
    ]
 
async def send_error(websocket: WebSocket, message: str):
    """Send error message to client"""
    error_payload = {
        "error_code": 400,
        "message": message,
        "is_end": True 
    }
    await websocket.send_text(json.dumps(error_payload)) 
 
async def cleanup_request(request_id: str, task_manager: TaskManager,
                        manager: ConnectionManager):
    """Cleanup request resources"""
    async with task_manager.lock: 
        await task_manager.cancel_task(request_id) 
        manager.interrupt_events.pop(request_id,  None)
 
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app,  host="localhost", port=8765, ws_ping_interval=25, ws_ping_timeout=35)
    