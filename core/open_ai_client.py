from PyQt5.QtCore import QObject, pyqtSignal, QMutex, QMutexLocker
import openai
from openai import OpenAI, AsyncOpenAI, APIError, RateLimitError
import uuid
import json
from typing import Dict, List, Optional
from qasync import asyncSlot

# 公共常量
MARKER = "icell-final-answer"
BUFFER_SAFE_MARGIN = 20  # 缓冲区安全余量

class BaseLLMClient(QObject):
    """Base class containing common functionality"""
    response_received = pyqtSignal(dict)  # {request_id, content, is_end, commands[], phase}
    send_error = pyqtSignal(str)
    connection_changed = pyqtSignal(str)

    def __init__(self, api_key: str, base_url: str):
        super().__init__()
        self.config = {
            "max_retries": 3,
            "response_timeout": 15,
            "stream_chunk_size": 1024
        }
        self._setup_clients(api_key, base_url)
        self.active_requests = {}
        self.mutex = QMutex()

    def _setup_clients(self, api_key: str, base_url: str):
        """Initialize client instances in subclasses"""
        raise NotImplementedError

    def _handle_content_chunk(self, request_id: str, buffer: str, is_final: bool) -> tuple:
        """Process content chunk and detect marker (returns new buffer, phase)"""
        phase = "thinking"
        marker_pos = buffer.find(MARKER)
        
        # 完整标记检测
        if marker_pos != -1:
            # 发射思考内容
            thinking_part = buffer[:marker_pos].strip()
            if thinking_part:
                self._emit_response(request_id, thinking_part, False, phase)
            
            # 处理最终答案部分
            final_content = buffer[marker_pos + len(MARKER):]
            return final_content, "final"
        
        # 处理可能的跨块分割
        if not is_final:
            # 保留可能的分割部分
            overlap = min(len(buffer), len(MARKER) - 1)
            for i in range(1, overlap + 1):
                if MARKER.startswith(buffer[-i:]):
                    hold_back = i
                    thinking_part = buffer[:-hold_back]
                    if thinking_part:
                        self._emit_response(request_id, thinking_part, False, phase)
                    return buffer[-hold_back:], phase
        
        # 最终块处理
        if is_final and buffer:
            self._emit_response(request_id, buffer, True, "final")
            return "", "final"
        
        return buffer, phase

    def _parse_final_answer(self, content: str) -> Optional[Dict]:
        """Parse and validate final answer JSON"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            self.send_error.emit("Invalid JSON format in final answer")
            return None

    def _emit_response(self, request_id: str, content: str, is_end: bool, phase: str):
        """Emit standardized response"""
        commands = []
        if phase == "final" and is_end:
            if parsed := self._parse_final_answer(content):
                commands = parsed.get("commands", [])
        
        self.response_received.emit({
            "request_id": request_id,
            "content": content,
            "is_end": is_end,
            "commands": commands,
            "phase": phase
        })

    def _check_cancellation(self, request_id: str) -> bool:
        """Thread-safe cancellation check"""
        with QMutexLocker(self.mutex):
            return self.active_requests.get(request_id, {}).get("cancel", False)

    def _emit_cancellation(self, request_id: str):
        """Notify about cancelled request"""
        self.response_received.emit({
            "request_id": request_id,
            "content": "Request cancelled",
            "is_end": True,
            "commands": [],
            "phase": "cancelled"
        })

class LLMClient(BaseLLMClient):
    """Synchronous client implementation"""
    
    def _setup_clients(self, api_key: str, base_url: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def send_request(self, message: Dict, deep_mode: bool = False) -> str:
        """Execute synchronous request"""
        request_id = message.get("request_id", str(uuid.uuid4()))
        
        with QMutexLocker(self.mutex):
            self.active_requests[request_id] = {"cancel": False}

        try:
            response = self.client.chat.completions.create(
                model="custom-model",
                messages=self._build_messages(message),
                stream=deep_mode,
                max_tokens=self.config["stream_chunk_size"],
                temperature=0.7
            )

            if deep_mode:
                self._process_streaming(response, request_id)
            else:
                self._process_normal_response(response, request_id)

        except (APIError, RateLimitError) as e:
            self._handle_api_error(e, request_id)
        except Exception as e:
            self.send_error.emit(f"Unexpected error: {str(e)}")
        finally:
            with QMutexLocker(self.mutex):
                del self.active_requests[request_id]

        return request_id

    def _process_streaming(self, response, request_id: str):
        """Process streaming response"""
        buffer = ""
        phase = "thinking"
        
        for chunk in response:
            if self._check_cancellation(request_id):
                self._emit_cancellation(request_id)
                return

            content = chunk.choices[0].delta.content or ""
            buffer += content
            
            while len(buffer) > BUFFER_SAFE_MARGIN:
                buffer, phase = self._handle_content_chunk(request_id, buffer, False)

        # Process remaining buffer
        if buffer:
            self._handle_content_chunk(request_id, buffer, True)

    def _process_normal_response(self, response, request_id: str):
        """Process non-streaming response"""
        content = response.choices[0].message.content
        buffer, _ = self._handle_content_chunk(request_id, content, True)

    def _handle_api_error(self, error: Exception, request_id: str):
        """Handle API errors"""
        error_msg = f"API Error: {str(error)}"
        self.send_error.emit(error_msg)
        self._emit_response(request_id, error_msg, True, "error")

    def _build_messages(self, message: Dict) -> List[Dict]:
        """Build message format"""
        return [{
            "role": "user",
            "content": message.get("content", "")
        }]

    def stop_request(self, request_id: str):
        """Cancel ongoing request"""
        with QMutexLocker(self.mutex):
            if request_id in self.active_requests:
                self.active_requests[request_id]["cancel"] = True

class AsyncLLMClient(BaseLLMClient):
    """Asynchronous client implementation"""
    
    def _setup_clients(self, api_key: str, base_url: str):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.pending_tasks = {}

    @asyncSlot(dict, bool)
    async def send_request(self, message: Dict, deep_mode: bool = False) -> str:
        """Execute asynchronous request"""
        request_id = message.get("request_id", str(uuid.uuid4()))
        
        with QMutexLocker(self.mutex):
            self.pending_tasks[request_id] = asyncio.create_task(
                self._execute_request(message, deep_mode, request_id)
            )

        return request_id

    async def _execute_request(self, message: Dict, deep_mode: bool, request_id: str):
        """Actual request execution"""
        try:
            response = await self.client.chat.completions.create(
                model="custom-model",
                messages=self._build_messages(message),
                stream=deep_mode,
                max_tokens=self.config["stream_chunk_size"],
                temperature=0.7
            )

            if deep_mode:
                await self._process_async_streaming(response, request_id)
            else:
                self._process_normal_response(response, request_id)

        except (APIError, RateLimitError) as e:
            self._handle_api_error(e, request_id)
        except asyncio.CancelledError:
            self._emit_cancellation(request_id)
        except Exception as e:
            self.send_error.emit(f"Unexpected error: {str(e)}")
        finally:
            with QMutexLocker(self.mutex):
                del self.pending_tasks[request_id]

    async def _process_async_streaming(self, response, request_id: str):
        """Process async streaming response"""
        buffer = ""
        phase = "thinking"
        
        async for chunk in response:
            if self._check_cancellation(request_id):
                raise asyncio.CancelledError()

            content = chunk.choices[0].delta.content or ""
            buffer += content
            
            while len(buffer) > BUFFER_SAFE_MARGIN:
                buffer, phase = self._handle_content_chunk(request_id, buffer, False)

        # Process remaining buffer
        if buffer:
            self._handle_content_chunk(request_id, buffer, True)

    def _process_normal_response(self, response, request_id: str):
        """Process async non-streaming response"""
        content = response.choices[0].message.content
        buffer, _ = self._handle_content_chunk(request_id, content, True)

    def stop_request(self, request_id: str):
        """Cancel async request"""
        with QMutexLocker(self.mutex):
            if task := self.pending_tasks.get(request_id):
                task.cancel()

    def _build_messages(self, message: Dict) -> List[Dict]:
        """Build message format"""
        return [{
            "role": "user",
            "content": message.get("content", "")
        }]