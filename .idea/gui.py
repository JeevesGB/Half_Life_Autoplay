import sys
import socket
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtCore import QTimer

# -----------------------------
# RCON Communication
# -----------------------------
class HLController:
    def __init__(self, host='127.0.0.1', port=27015, password='mypass'):
        self.host = host
        self.port = port
        self.password = password
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, command):
        msg = f"rcon {self.password} {command}"
        self.sock.sendto(msg.encode(), (self.host, self.port))

# -----------------------------
# Script Executor
# -----------------------------
class ScriptExecutor:
    def __init__(self, controller, status_callback):
        self.controller = controller
        self.status_callback = status_callback
        self.commands = []
        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        self.current_steps_remaining = 0
        self.current_command = None

    def load_script(self, script_text):
        self.commands = []
        lines = script_text.splitlines()
        for line in lines:
            line = line.split("//")[0].strip()  # Remove comments
            if not line:
                continue
            match = re.match(r"(\w+)(?::\s*([-+]?\d*\.?\d+))?", line)
            if match:
                cmd = match.group(1).lower()
                param = match.group(2)
                if param:
                    try:
                        param = float(param)
                    except ValueError:
                        param = None
                self.commands.append((cmd, param))
        self.current_index = 0

    def start(self):
        if not self.commands:
            return
        self.current_index = 0
        self.execute_current_command()

    def execute_current_command(self):
        if self.current_index >= len(self.commands):
            self.status_callback("Script Finished")
            return

        cmd, param = self.commands[self.current_index]
        self.current_command = cmd

        if cmd == "walk":
            self.current_steps_remaining = int(param) if param else 1
            self.timer.start(50)
        elif cmd == "walk_backwards":
            self.current_steps_remaining = int(param) if param else 1
            self.current_command = "+back"
            self.timer.start(50)
        elif cmd == "turn_right":
            self.controller.send("turn 90")
            self.next_command()
        elif cmd == "turn_left":
            self.controller.send("turn -90")
            self.next_command()
        elif cmd == "turn":
            deg = int(param) if param else 0
            self.controller.send(f"turn {deg}")
            self.next_command()
        elif cmd == "jump":
            self.controller.send("+jump")
            QTimer.singleShot(100, lambda: self.controller.send("-jump"))
            self.next_command()
        elif cmd == "crouch":
            self.controller.send("+duck")
            self.next_command()
        elif cmd == "stand":
            self.controller.send("-duck")
            self.next_command()
        elif cmd == "use":
            self.controller.send("+use")
            QTimer.singleShot(100, lambda: self.controller.send("-use"))
            self.next_command()
        elif cmd == "shoot":
            duration = float(param) if param else 0.5
            self.controller.send("+attack")
            QTimer.singleShot(int(duration*1000), lambda: self.controller.send("-attack"))
            self.next_command()
        else:
            self.next_command()

        self.status_callback(f"Executing: {cmd} {param if param else ''}")

    def next_step(self):
        if self.current_steps_remaining > 0:
            self.controller.send(self.current_command)
            self.current_steps_remaining -= 1
            self.status_callback(f"{self.current_command}, steps left: {self.current_steps_remaining}")
        else:
            if self.current_command.startswith("+"):
                stop_cmd = self.current_command.replace("+", "-")
                self.controller.send(stop_cmd)
            self.timer.stop()
            self.current_index += 1
            self.execute_current_command()

    def next_command(self):
        self.current_index += 1
        self.execute_current_command()

# -----------------------------
# Main GUI
# -----------------------------
class HLGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Half-Life Player Controller")
        self.controller = HLController()
        self.script_executor = ScriptExecutor(self.controller, self.update_status)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Manual movement buttons
        movement_layout = QHBoxLayout()
        self.forward_btn = QPushButton("Forward")
        self.backward_btn = QPushButton("Backward")
        self.left_btn = QPushButton("Left")
        self.right_btn = QPushButton("Right")
        self.jump_btn = QPushButton("Jump")
        self.use_btn = QPushButton("Use")

        for btn in [self.forward_btn, self.backward_btn, self.left_btn, self.right_btn, self.jump_btn, self.use_btn]:
            btn.setCheckable(True)
            movement_layout.addWidget(btn)

        layout.addLayout(movement_layout)

        # Connect button presses
        self.forward_btn.pressed.connect(lambda: self.controller.send("+forward"))
        self.forward_btn.released.connect(lambda: self.controller.send("-forward"))
        self.backward_btn.pressed.connect(lambda: self.controller.send("+back"))
        self.backward_btn.released.connect(lambda: self.controller.send("-back"))
        self.left_btn.pressed.connect(lambda: self.controller.send("+moveleft"))
        self.left_btn.released.connect(lambda: self.controller.send("-moveleft"))
        self.right_btn.pressed.connect(lambda: self.controller.send("+moveright"))
        self.right_btn.released.connect(lambda: self.controller.send("-moveright"))
        self.jump_btn.pressed.connect(lambda: self.controller.send("+jump"))
        self.jump_btn.released.connect(lambda: self.controller.send("-jump"))
        self.use_btn.pressed.connect(lambda: self.controller.send("+use"))
        self.use_btn.released.connect(lambda: self.controller.send("-use"))

        # Script editor
        layout.addWidget(QLabel("Script Editor"))
        self.script_text = QTextEdit()
        layout.addWidget(self.script_text)
        script_btn_layout = QHBoxLayout()
        self.run_script_btn = QPushButton("Run Script")
        self.run_script_btn.clicked.connect(self.run_script)
        self.save_btn = QPushButton("Save Script")
        self.save_btn.clicked.connect(self.save_script)
        self.load_btn = QPushButton("Load Script")
        self.load_btn.clicked.connect(self.load_script)
        script_btn_layout.addWidget(self.run_script_btn)
        script_btn_layout.addWidget(self.save_btn)
        script_btn_layout.addWidget(self.load_btn)
        layout.addLayout(script_btn_layout)

        # Status
        layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Idle")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    # -----------------------------
    # Scripted Movement
    # -----------------------------
    def run_script(self):
        self.script_executor.load_script(self.script_text.toPlainText())
        self.script_executor.start()

    # -----------------------------
    # Script Save / Load
    # -----------------------------
    def save_script(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Script",
            "my_script.hlw",  # default name
            "Half-Life Script (*.hlw);;All Files (*)"
        )
        if filename:
            if not filename.lower().endswith(".hlw"):
                filename += ".hlw"
            with open(filename, "w") as f:
                f.write(self.script_text.toPlainText())
            self.update_status(f"Script saved to {filename}")

    def load_script(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Script",
            "",  # start in current directory
            "Half-Life Script (*.hlw);;All Files (*)"
        )
        if filename:
            with open(filename, "r") as f:
                script = f.read()
            self.script_text.setPlainText(script)
            self.update_status(f"Loaded script: {filename}")

    # -----------------------------
    # Status
    # -----------------------------
    def update_status(self, text):
        self.status_label.setText(text)

# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HLGUI()
    gui.show()
    sys.exit(app.exec())
