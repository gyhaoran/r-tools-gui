# llm_server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from enum import Enum
import uuid
import time
import json
import asyncio
import logging
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ResponseType(str, Enum):
    """Enum for response message types"""
    TEXT_CHUNK = "text_chunk"
    THINKING_STEP = "thinking_step"
    ERROR = "error"

class ChatRequest(BaseModel):
    """Pydantic model for chat request validation"""
    message: str
    deep_mode: bool = False

async def mock_llm_generation(message: str, deep_mode: bool):
    """Simulate LLM response generation with different modes
    
    Args:
        message (str): User input message
        deep_mode (bool): Whether to use deep thinking mode
    
    Yields:
        dict: Response chunks with metadata
    """
    try:
        if deep_mode:
            # Simulate deep thinking process
            thinking_steps = [
                ("理解问题", "正在分析用户的核心需求..."),
                ("知识检索", "从知识库中检索相关案例..."),
                ("逻辑推理", "构建推理链条..."),
                ("生成结果", "整合最终结论")
            ]
            
            for step in thinking_steps:
                yield {
                    "type": ResponseType.THINKING_STEP,
                    "content": f"{step[0]}: {step[1]}",
                    "is_end": False
                }
                await asyncio.sleep(1.5)  # Simulate processing time
                
            yield {
                "type": ResponseType.TEXT_CHUNK,
                "content": "Final conclusion based on deep analysis:\nRecommended action: Implement solution X",
                "is_end": True
            }
        else:
            # Simulate standard response
            for i in range(1, 4):
                yield {
                    "type": ResponseType.TEXT_CHUNK,
                    "content": f"Response part {i}/3: Sample content chunk",
                    "is_end": i == 3
                }
                await asyncio.sleep(0.8)
                
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        yield {
            "type": ResponseType.ERROR,
            "content": "Error in processing request",
            "is_end": True
        }

@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for chat interactions
    
    Handles:
    - Connection initialization
    - Message validation
    - Response generation
    - Error handling
    """
    await websocket.accept()
    client_id = uuid.uuid4().hex
    logger.info(f"Client connected: {client_id}")
    
    try:
        while True:
            # Receive and validate message
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
                ChatRequest(**data)  # Validate with Pydantic
            except Exception as e:
                error_msg = {"type": ResponseType.ERROR, "content": "Invalid request format"}
                await websocket.send_json(error_msg)
                continue

            # Process valid request
            request_id = data.get("request_id", str(uuid.uuid4()))
            logger.info(f"Processing request {request_id}")
            
            async for chunk in mock_llm_generation(
                message=data["message"],
                deep_mode=data["deep_mode"]
            ):
                response = {
                    **chunk,
                    "request_id": request_id,
                    "timestamp": int(time.time())
                }
                await websocket.send_json(response)
                
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        error_msg = {
            "type": ResponseType.ERROR,
            "content": "Internal server error",
            "is_end": True
        }
        await websocket.send_json(error_msg)
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
