import json 
import uuid 
from PyQt5.QtCore import QObject, pyqtSignal, QUrl 
from PyQt5.QtWebSockets import QWebSocket 
from PyQt5.QtNetwork import QAbstractSocket 
 
# ==================== Core WebSocket Client ====================
class LLMClient(QObject):
    response_received = pyqtSignal(dict)
    status_changed = pyqtSignal(str)  # Connection status signal: connecting/connected/disconnected 
 
    def __init__(self, server_url):
        super().__init__()
        self.ws  = QWebSocket()
        self.server_url  = QUrl(server_url)
        self.current_request_id  = None 
        self._init_connections()
 
    def _init_connections(self):
        """Initialize signal-slot connections"""
        # Connection status signals 
        self.ws.connected.connect(lambda:  self.status_changed.emit("connected")) 
        self.ws.disconnected.connect(lambda:  self.status_changed.emit("disconnected")) 
        self.ws.error.connect(self._handle_error) 
        
        # Message reception signal 
        self.ws.textMessageReceived.connect(self._handle_message) 
 
    def connect_server(self):
        """Initiate connection (thread-safe)"""
        if self.ws.state()  == QAbstractSocket.UnconnectedState:
            self.status_changed.emit("connecting") 
            self.ws.open(self.server_url) 
 
    def send_request(self, data, deep_mode=False):
        """Send request (called directly from main thread)"""
        self.current_request_id  = data.get("request_id",  str(uuid.uuid4())) 
        
        request = {
            "request_id": self.current_request_id, 
            "message": data.get("content", ""),
            "deep_mode": deep_mode 
        }
        
        if self.ws.isValid(): 
            self.ws.sendTextMessage(json.dumps(request)) 
        else:
            self.response_received.emit({ 
                "request_id": self.current_request_id, 
                "content": "Connection not ready",
                "is_end": True 
            })
 
    def _handle_message(self, message):
        """Message parsing and forwarding"""
        try:
            data = json.loads(message) 
            self.response_received.emit(data) 
            
            if data.get("is_end",  False):
                self.current_request_id  = None 
        except json.JSONDecodeError:
            self.response_received.emit({ 
                "request_id": self.current_request_id, 
                "content": "Invalid message format",
                "is_end": True 
            })
 
    def _handle_error(self, error):
        """Error handling"""
        error_map = {
            QAbstractSocket.HostNotFoundError: "Server not found",
            QAbstractSocket.ConnectionRefusedError: "Connection refused",
            QAbstractSocket.NetworkError: "Network error"
        }
        msg = error_map.get(error,  f"Unknown error ({error})")
        self.response_received.emit({ 
            "request_id": self.current_request_id, 
            "content": msg,
            "is_end": True 
        })
 
    def close(self):
        """Safely close connection"""
        if self.ws.isValid(): 
            self.ws.close() 
 
    def __del__(self):
        """Destructor"""
        self.close()
