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


class HistoryCommand(Command):
    """Show history information"""
    @classmethod
    def name(cls) -> str:
        return "history"
    
    @classmethod
    def dscp(cls) -> str:
        return "Show history information"
    
    def execute(self, args: List[str]) -> str:
        return "Show history information"


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
    
# ==================== Command Sequence Implementation ====================
import shlex
class SequenceCommand(Command):
    """Execute multiple commands in sequence with proper argument parsing"""
    @classmethod
    def name(cls) -> str:
        return "sequence"
    
    @classmethod
    def dscp(cls) -> str:
        return (
            "Execute commands sequentially, stop on first failure\n"
            "Usage:\n"
            "  sequence \"cmd1 args\" \"cmd2 args\"...\n"
            "Example:\n"
            "  sequence \"echo hello\" \"version\""
        )
    
    def execute(self, args: List[str]) -> str:
        registry = CommandRegistry()
        results = []
        
        try:
            # Split command sequence with proper quote handling
            commands = self._parse_arguments(args)
        except ValueError as e:
            return f"Invalid command sequence: {str(e)}"
        
        for cmd_str in commands:
            try:
                # Split into command and arguments
                parts = shlex.split(cmd_str)
                if not parts:
                    continue
                
                cmd_name = parts[0]
                cmd_args = parts[1:]
                
                cmd = registry.get_command(cmd_name)
                output = cmd.execute(cmd_args)
                results.append(output.strip())
            except Exception as e:
                results.append(f"Error in '{cmd_str}': {str(e)}")
                break
        
        return '\n'.join(filter(None, results))
    
    def _parse_arguments(self, args: List[str]) -> List[str]:
        """Parse command sequence with proper quote handling"""
        try:
            # Join and re-split with full quote support
            full_cmd = ' '.join(args)
            return shlex.split(full_cmd, posix=True)
        except ValueError as e:
            raise ValueError(f"Invalid command syntax: {str(e)}")


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
            help_text += f"\n{cmd_cls.name():<20} - {cmd_cls.dscp().splitlines()[0]}"
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

    def contextMenuEvent(self, event):
        """Custom context menu with essential actions"""
        menu = QMenu(self)
        
        # Add Copy action with selection check
        copy_action = QAction("Copy", self)
        copy_action.setEnabled(self.textCursor().hasSelection())
        copy_action.triggered.connect(self.copy)
        menu.addAction(copy_action)

        # Add Copy action with selection check
        paste_action = QAction("&Paste", self)
        paste_action.triggered.connect(self._handle_ctrl_v)
        paste_action.setShortcut("Ctrl+V")
        menu.addAction(paste_action)

        # Add existing Clear action
        clear_action = QAction("&Clear", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self._handle_ctrl_l)
        menu.addAction(clear_action)
        
        menu.exec_(event.globalPos())

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
                self._handle_ctrl_v()
                event.accept()  # Disable Ctrl+V
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
        if key in (Qt.Key_Return, Qt.Key_Enter):
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

    def _handle_ctrl_c(self):
        """Handle Ctrl+C to abort current input"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        cursor.insertText("^C")
        self._advance_to_new_prompt()

    def _handle_ctrl_v(self):
        self._enforce_cursor_boundary()
        self.paste()

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
        history_input = self._get_current_line()
        self._append_output(f"\n{'   '.join(candidates)}\n")
        self._insert_prompt()
        current_input = self._get_current_line()
        self._append_output(current_input)
        self._append_output(history_input)

    def _get_completion_prefix(self) -> str:
        """Extract current word for completion matching"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        return cursor.selectedText().strip()

    # ==================== Command Execution Flow ====================
    def _process_command_execution(self):
        """Handle command submission and output display"""
        # Ensure cursor at end of line before execution
        self._enforce_cursor_boundary()
        
        cmd = self._get_current_line().strip()
        
        if cmd:
            self._store_command_history(cmd)
            self.execute_command.emit(cmd)
            self._advance_to_new_prompt()
        else:
            # Handle empty command with new prompt
            self._advance_to_new_prompt()

    def _move_cursor_to_line_end(self):
        """Ensure cursor at end of current command line"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.EndOfLine)
        self.setTextCursor(cursor)

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
        

def main():
    import sys
    app = QApplication(sys.argv)

    # Register sample commands
    registry = CommandRegistry()
    registry.register(EchoCommand.name(), EchoCommand)
    registry.register(VersionCommand.name(), VersionCommand)
    registry.register(SequenceCommand.name(), SequenceCommand)
    registry.register(HistoryCommand.name(), HistoryCommand)

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

1. tab补齐的时候出现问题， 例如用户输入： help h， 这个时候tab补齐会显示help和history两条命令，新起一行的时候只有h, 而不是help h
iCell> help h
help   history
iCell> h

要求：
1. 代码clean code, 代码注释使用英文
"""