from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QTimer 
from PyQt5.QtWebSockets import QWebSocket 
from PyQt5.QtNetwork import QAbstractSocket 
import json 
import time 
import uuid 
 
 
class LLMClient(QObject):
    """
    WebSocket client for communicating with LLM Server 
    Handles message streaming and command execution 
    """
    response_received = pyqtSignal(dict)  # {request_id, content, is_end, commands[]}
    connection_changed = pyqtSignal(str)  # Connection status updates 
    send_error = pyqtSignal(str)  # Error messages
 
    def __init__(self, server_url: str):
        """
        Initialize client with server URL 
        Args:
            server_url: WebSocket server address (e.g., "ws://localhost:8765")
        """
        super().__init__()
        self.ws  = QWebSocket()
        self.server_url  = QUrl(server_url)
        self.pending_requests  = {}  # Track ongoing requests 
        self.active_commands  = {}  # Store command lists for completed requests 
 
        # Configuration parameters 
        self.config  = {
            "reconnect_interval": 5,  # Seconds between reconnect attempts 
            "response_timeout": 5,  # Seconds to wait for server response 
            "heartbeat_interval": 30  # Seconds between heartbeat checks 
        }
 
        # Initialize timers 
        self.reconnect_timer  = QTimer(self)
        self.heartbeat_timer  = QTimer(self)
        
        # Setup signal connections 
        self._connect_signals()
        self._setup_timers()
 
    def connect_server(self) -> None:
        """Establish connection to WebSocket server"""
        if self.ws.state()  == QAbstractSocket.UnconnectedState:
            self.ws.open(self.server_url) 
 
    def send_request(self, message: str, deep_mode: bool = False) -> str:
        """
        Send new request to LLM server 
        Args:
            message: User input text 
            deep_mode: Enable advanced analysis mode 
        Returns:
            request_id: Unique identifier for tracking responses 
        """
        print(f"Sending request: {message}, deep_mode={deep_mode}")
        request_id = message.get("request_id",  str(uuid.uuid4()))
        payload = {
            "protocol": 2,
            "request_id": request_id,
            "type": 0,
            "message": message.get("content",  ""),
            "deep_mode": deep_mode
        }
        self._send_json(payload)
        self.pending_requests[request_id]  = time.time() 
        
        # Setup response timeout 
        QTimer.singleShot(self.config["response_timeout"]  * 1000,
                         lambda: self._handle_response_timeout(request_id))
 
    def stop_request(self, request_id: str) -> None:
        """Send request termination command"""
        payload = {
            "protocol": 2,
            "request_id": request_id, 
            "type": 1
        }
        self._send_json(payload)
 
    # Internal Handlers 
    def _on_message_received(self, message: str) -> None:
        """Process incoming server messages"""
        try:
            print(f"Received llm server message: {message}")
            data = json.loads(message) 
            self._update_heartbeat()
            
            if data["type"] == 0:  # Standard response 
                self._process_llm_response(data)
            elif data["type"] == 2:  # Heartbeat 
                self._process_heartbeat(data)
 
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Invalid message format: {str(e)}, {message}")
 
    def _process_llm_response(self, data: dict) -> None:
        """Handle LLM response packets"""
        request_id = data["request_id"]
        is_final = data.get("is_end",  False)
        
        # Emit immediate update 
        self.response_received.emit({ 
            "request_id": request_id,
            "content": data["content"],
            "is_end": is_final,
            "commands": data.get("commands",  []) if is_final else []
        })
 
        # Cleanup completed requests 
        if is_final and request_id in self.pending_requests: 
            del self.pending_requests[request_id] 
 
    def _handle_response_timeout(self, request_id: str) -> None:
        """Handle unanswered requests"""
        if request_id in self.pending_requests: 
            self.response_received.emit({ 
                "request_id": request_id,
                "content": "Response timeout"
            })
            del self.pending_requests[request_id] 
 
    # Network Management 
    def _connect_signals(self) -> None:
        """Connect WebSocket signals"""
        self.ws.connected.connect(self._on_connected) 
        self.ws.disconnected.connect(self._on_disconnected) 
        self.ws.textMessageReceived.connect(self._on_message_received) 
 
    def _setup_timers(self) -> None:
        """Configure automatic timers"""
        self.reconnect_timer.timeout.connect(self.reconnect) 
        self.heartbeat_timer.timeout.connect(self.check_heartbeat) 
 
    def _on_connected(self) -> None:
        """Handle successful connection"""
        self.connection_changed.emit('connected') 
        self.heartbeat_timer.start(self.config["heartbeat_interval"]  * 1000)
        self.reconnect_timer.stop() 
 
    def _on_disconnected(self) -> None:
        """Handle connection loss"""
        self.connection_changed.emit('disconnected') 
        self.heartbeat_timer.stop() 
        self.reconnect_timer.start(self.config["reconnect_interval"]  * 1000)
 
    def reconnect(self) -> None:
        """Attempt server reconnection"""
        if not self.ws.isValid(): 
            self.ws.abort() 
            self.connect_server() 
 
    # Heartbeat Management 
    def _update_heartbeat(self) -> None:
        """Refresh last active timestamp"""
        self.last_activity  = time.time() 
 
    def check_heartbeat(self) -> None:
        """Monitor connection health"""
        if time.time()  - self.last_activity  > self.config["heartbeat_interval"]: 
            self._send_heartbeat()
 
    def _send_heartbeat(self) -> None:
        """Send heartbeat ping"""
        if self.ws.state()  == QAbstractSocket.ConnectedState:
            self._send_json({
                "protocol": 2,
                "type": 2,
                "payload": "ping"
            })
 
    def _process_heartbeat(self, data: dict) -> None:
        """Handle heartbeat response"""
        if data.get("payload")  == "pong":
            self._update_heartbeat()
 
    def _send_json(self, data: dict) -> None:
        """Safely send JSON data"""
        if self.ws.isValid():
            print(f"Connection state before send: {self.ws.state()}") 
            self.ws.sendTextMessage(json.dumps(data)) 
        else:
            print("Error: Cannot send message - llm server not connected")
            self.send_error.emit("Error: Cannot send message - llm server not connected")
            