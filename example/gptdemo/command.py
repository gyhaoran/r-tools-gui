from PyQt5.QtCore import Qt, QObject, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtWidgets import (QTextEdit, QApplication, QCompleter,
                             QScrollBar, QMenu, QAction)
from PyQt5.QtGui import (QTextCursor, QTextCharFormat, QColor,
                         QKeyEvent, QFont, QSyntaxHighlighter,
                         QTextFormat, QPalette)
from abc import ABC, abstractmethod
from typing import List, Dict, Type

# ==================== Command Framework Core ====================
class Command(ABC):
    """Abstract base class with enhanced command metadata"""
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Unique command identifier"""
        pass
    
    @classmethod
    @abstractmethod
    def dscp(cls) -> str:
        """Command description with usage instructions"""
        pass
        
    @abstractmethod
    def execute(self, args: List[str]) -> str:
        """Execute command with given arguments"""
        pass

class HelpCommand(Command):
    """Built-in help system implementation"""
    @classmethod
    def name(cls) -> str:
        return "help"
    
    @classmethod
    def dscp(cls) -> str:
        return (
            "Display command information\n"
            "Usage:\n"
            "  help [command]\n"
            "Options:\n"
            "  command  Show details for specific command"
        )
    
    def execute(self, args: List[str]) -> str:
        registry = CommandRegistry()
        if not args:
            return self._all_commands_help(registry)
        return self._single_command_help(registry, args[0])
    
    def _all_commands_help(self, registry) -> str:
        """Generate help listing for all commands"""
        help_text = "Available commands:\n"
        for cmd_name in registry._commands:
            cmd_cls = registry._commands[cmd_name]
            help_text += f"\n{cmd_cls.name():<10} - {cmd_cls.dscp().splitlines()[0]}"
        return help_text
    
    def _single_command_help(self, registry, cmd_name: str) -> str:
        """Generate detailed help for specific command"""
        try:
            cmd_cls = registry._commands[cmd_name]
            return f"{cmd_cls.name()} command\n{cmd_cls.dscp()}"
        except KeyError:
            return f"Command not found: {cmd_name}"

# ==================== Command Registry Update ====================
class CommandRegistry(QObject):
    """Singleton registry with command metadata support"""
    _instance = None
    command_registered = pyqtSignal(str)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self._commands: Dict[str, Type[Command]] = {}
            self.register(HelpCommand.name(), HelpCommand)
            self._initialized = True

    def register(self, name: str, command: Type[Command]):
        """Register command with metadata validation"""
        if name != command.name():
            raise ValueError(f"Command name mismatch: {name} vs {command.name()}")
        self._commands[name] = command
        self.command_registered.emit(name)

    def get_command(self, name: str) -> Command:
        """Factory method with enhanced error handling"""
        try:
            return self._commands[name]()
        except KeyError:
            raise ValueError(f"Unknown command: {name}")

# ==================== Terminal Widget Implementation ====================
class iCellTerminal(QTextEdit):
    """Custom terminal widget with advanced command features"""
    execute_command = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_settings()
        self._init_ui_components()
        self._init_command_system()
        self._insert_prompt()

    def _init_settings(self):
        """Initialize terminal configuration"""
        self.setUndoRedoEnabled(False)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self._prompt = "iCell> "
        self._history_max = 100
        self._current_line_pos = 0

    def _init_ui_components(self):
        """Set up UI elements and styling"""
        self.setStyleSheet("""
        QTextEdit {
            background-color: #002b36;
            color: #839496;
            font-family: 'Consolas';
            font-size: 12pt;
            selection-background-color: #073642;
        }
        """)
        self._init_completer()
        self._init_scrollbar()

    def _init_completer(self):
        """Configure command auto-completion system"""
        self.completer = QCompleter([])
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

    def _init_scrollbar(self):
        """Customize scrollbar appearance"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setStyleSheet("""
        QScrollBar:vertical {
            background: #073642;
            width: 14px;
            margin: 14px 0 14px 0;
        }
        QScrollBar::handle:vertical {
            background: #586e75;
            min-height: 30px;
        }
        """)

    def _init_command_system(self):
        """Initialize command-related data structures"""
        self._command_history = []
        self._history_index = -1
        self._current_buffer = ""
        self._prompt_positions = [0]

    # ==================== Enhanced Mouse Handling ====================
    def mousePressEvent(self, event):
        """Allow text selection but keep cursor in current line"""
        # Save current cursor position
        original_cursor = self.textCursor()
        original_pos = original_cursor.position()
        
        # Process the mouse event normally
        super().mousePressEvent(event)
        
        # Get new cursor position after click
        new_cursor = self.textCursor()
        new_pos = new_cursor.position()
        
        # Enforce cursor boundary
        if new_pos < self._current_line_pos:
            new_cursor.setPosition(self._current_line_pos)
        self.setTextCursor(new_cursor)
        
        # Preserve original selection
        if original_pos != new_pos:
            new_cursor.setPosition(original_pos, QTextCursor.KeepAnchor)
        
        self._enforce_cursor_boundary()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click selection within current line"""
        # Perform normal double-click selection
        super().mouseDoubleClickEvent(event)
        
        # Adjust selection boundaries
        cursor = self.textCursor()
        start = max(cursor.selectionStart(), self._current_line_pos)
        end = cursor.selectionEnd()
        
        # Create new selection within valid range
        cursor.setPosition(start)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        
        self._enforce_cursor_boundary()

    def mouseMoveEvent(self, event):
        """Handle text selection with boundary checks"""
        # Process mouse movement normally
        super().mouseMoveEvent(event)
        
        # Constrain selection to current line
        cursor = self.textCursor()
        if cursor.hasSelection():
            start = max(cursor.selectionStart(), self._current_line_pos)
            end = cursor.selectionEnd()
            
            # Update selection if out of bounds
            if start < self._current_line_pos:
                cursor.setPosition(self._current_line_pos)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)
        
        # self._enforce_cursor_boundary()

    # ==================== Core Cursor Control ====================
    def _enforce_cursor_boundary(self):
        """Ensure cursor stays within editable area"""
        cursor = self.textCursor()
        current_pos = cursor.position()
        
        # Calculate line boundaries
        cursor.movePosition(QTextCursor.EndOfLine)
        line_end = cursor.position()
        
        # Apply position constraints
        if current_pos < self._current_line_pos:
            cursor.setPosition(self._current_line_pos)
        elif current_pos > line_end:
            cursor.setPosition(line_end)
        
        self.setTextCursor(cursor)

    # ==================== Event Processing ====================
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input with command features"""
        key = event.key()
        modifiers = event.modifiers()

        # Handle Control modifiers
        if modifiers == Qt.ControlModifier:
            if key == Qt.Key_U:
                self._clear_current_line()
                event.accept()
                return
            elif key == Qt.Key_L:
                self._handle_ctrl_l()
                event.accept()
                return
            elif key == Qt.Key_C:
                self._handle_ctrl_c()
                event.accept()
                return
            elif key == Qt.Key_V:
                event.ignore()  # Disable Ctrl+V
                return

        # Handle Backspace protection
        if key == Qt.Key_Backspace:
            cursor = self.textCursor()
            if cursor.position() <= self._current_line_pos:
                event.ignore()
                return
            else:
                super().keyPressEvent(event)
                self._enforce_edit_boundary()
                return

        # Handle Enter key
        if key == Qt.Key_Return:
            self._process_command_execution()
            return

        # History navigation
        if key == Qt.Key_Up:
            self._navigate_history(1)
            return
        if key == Qt.Key_Down:
            self._navigate_history(-1)
            return

        # Auto-completion
        if key == Qt.Key_Tab:
            self._trigger_auto_completion()
            return

        # Filter input in protected areas
        if self._should_filter_input(event):
            event.ignore()
            return

        super().keyPressEvent(event)
        self._enforce_edit_boundary()

    def contextMenuEvent(self, event):
        """Custom context menu with limited actions"""
        menu = QMenu(self)
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self._handle_ctrl_l)
        menu.addAction(clear_action)
        menu.exec_(event.globalPos())

    def _handle_ctrl_c(self):
        """Handle Ctrl+C to abort current input"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.insertText("^C")
        self._advance_to_new_prompt()

    def _handle_ctrl_l(self):
        """Handle Ctrl+L to clear screen"""
        self.clear()
        self._insert_prompt()
        self._record_prompt_position()

    # ==================== Command History Management ====================
    def _navigate_history(self, step: int):
        """Cycle through command history with up/down keys"""
        if not self._command_history:
            return

        if self._history_index == -1:
            self._current_buffer = self._get_current_line()

        new_index = self._history_index + step
        if -1 <= new_index < len(self._command_history):
            self._history_index = new_index
            cmd = self._command_history[self._history_index] if self._history_index != -1 else self._current_buffer
            self._replace_current_line(cmd)

    def _replace_current_line(self, new_text: str):
        """Update current command line content"""
        cursor = self.textCursor()
        cursor.setPosition(self._current_line_pos)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(new_text)
        self.setTextCursor(cursor)

    # ==================== Auto-Completion System ====================
    def _get_completion_candidates(self, prefix: str) -> List[str]:
        """Get sorted list of matching commands"""
        all_commands = CommandRegistry()._commands.keys()
        return sorted([cmd for cmd in all_commands if cmd.startswith(prefix)])    

    def _trigger_auto_completion(self):
        """Display command suggestions in terminal directly"""
        prefix = self._get_completion_prefix()       
        candidates = self._get_completion_candidates(prefix)
        
        if not candidates:
            return  # No matches
        
        cursor = self.textCursor()
        if len(candidates) == 1:  # Auto-complete
            cursor.insertText(candidates[0][len(prefix):])
            return

        if len(candidates) > 1:
            self._display_candidates(prefix, candidates)      

    def _display_candidates(self, prefix: str, candidates: List[str]):
        self._append_output(f"\n{'   '.join(candidates)}\n")
        self._insert_prompt()
        current_input = self._get_current_line()        
        self._append_output(current_input)
        self._append_output(prefix)

    def _get_completion_prefix(self) -> str:
        """Extract current word for completion matching"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText().strip()

    # ==================== Command Execution Flow ====================
    def _process_command_execution(self):
        """Handle command submission and output display"""
        cmd = self._get_current_line().strip()
        
        if cmd:
            self._store_command_history(cmd)
            self.execute_command.emit(cmd)
            self._advance_to_new_prompt()
        else:
            # Handle empty command with new prompt
            self._advance_to_new_prompt()

    def _store_command_history(self, cmd: str):
        """Update command history storage"""
        self._command_history = [cmd] + self._command_history[:self._history_max-1]
        self._history_index = -1

    def _advance_to_new_prompt(self):
        """Add new prompt after command execution"""
        self._append_output("\n")
        self._insert_prompt()
        self._record_prompt_position()

    # ==================== Input Protection System ====================
    def _should_filter_input(self, event: QKeyEvent) -> bool:
        """Determine if input should be blocked"""
        return (not self._is_in_editable_zone()
                and event.key() not in (Qt.Key_Control, Qt.Key_Shift))

    def _is_in_editable_zone(self) -> bool:
        """Check if cursor is within current command line"""
        return self.textCursor().position() >= self._current_line_pos

    def _enforce_edit_boundary(self):
        """Ensure cursor stays in allowed editing area"""
        cursor = self.textCursor()
        if cursor.position() < self._current_line_pos:
            cursor.setPosition(self._current_line_pos)
            self.setTextCursor(cursor)

    # ==================== Output Management ====================
    def _insert_prompt(self):
        """Insert new prompt with protected formatting"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(self._prompt)
        self._record_prompt_position()

    def _record_prompt_position(self):
        """Track position of current command line start"""
        self._current_line_pos = self.textCursor().position()

    def _append_output(self, text: str):
        """Safely append text to terminal output"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.ensureCursorVisible()

    # ==================== Utility Methods ====================
    def _get_current_line(self) -> str:
        """Extract current command line content"""
        full_text = self.toPlainText()
        return full_text[self._current_line_pos:].strip()

    def _clear_current_line(self):
        """Clear current command line content"""
        cursor = self.textCursor()
        cursor.setPosition(self._current_line_pos)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        self.setTextCursor(cursor)
        

# ==================== Sample Command Implementations ====================
class EchoCommand(Command):
    """Demonstration command for echo functionality"""
    @classmethod
    def name(cls) -> str:
        return "echo"
    
    @classmethod
    def dscp(cls) -> str:
        return (
            "Display input arguments\n"
            "Usage:\n"
            "  echo [text...]\n"
            "Options:\n"
            "  text  One or more arguments to display"
        )
    
    def execute(self, args: List[str]) -> str:
        return " ".join(args) if args else ""

class VersionCommand(Command):
    """System version information"""
    @classmethod
    def name(cls) -> str:
        return "version"
    
    @classmethod
    def dscp(cls) -> str:
        return "Display terminal version information"
    
    def execute(self, args: List[str]) -> str:
        return "iCell Terminal v2.1.1 (2025)"
    

def main():
    import sys
    app = QApplication(sys.argv)

    # Register sample commands
    registry = CommandRegistry()
    registry.register(EchoCommand.name(), EchoCommand)
    registry.register(VersionCommand.name(), VersionCommand)

    terminal = iCellTerminal()
    terminal.resize(800, 400)

    def handle_command(cmd: str):
        parts = cmd.split()
        if not parts:
            return

        try:
            command = registry.get_command(parts[0])
            output = command.execute(parts[1:])
            terminal._append_output(f"\n{output}")
        except ValueError as e:
            terminal._append_output(f"\nError: {str(e)}")

    terminal.execute_command.connect(handle_command)
    terminal.show()
    sys.exit(app.exec_())    


if __name__ == "__main__":
    main()
    

"""
pyqt5 gui应用


基于我现在的代码，帮我支持以下需求：
1. 使用最简单的方式，鼠标单击，双击事件（选中文本），保证光标在当前行就行（保持不变，用户控制光标，只能通过键盘左右键去控制移动），通过简单设计，保持软件的稳定性

    


要求：
1. 代码clean code, 代码注释使用英文
2. 给出完整版的代码，回答使用中文
"""