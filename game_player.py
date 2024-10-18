from pynput.keyboard import Key, Controller
import time

keyboard = Controller()

# Give yourself time to switch to the game
time.sleep(2.5)


def sleep(duration):
    print(f"Waiting for {duration} seconds...")
    time.sleep(duration)

def close_console():
    print("Closing console with Escape key...")
    keyboard.press(Key.esc)
    time.sleep(0.1)  # Hold for a short duration
    keyboard.release(Key.esc)
    print("Console closed.")

def move_forward(duration):
    print(f"Moving forward for {duration} seconds...")
    keyboard.press('w')
    time.sleep(duration)
    keyboard.release('w')
    print("Stopped moving forward.")

def jump():
    print("Jumping!")
    keyboard.press(Key.space)
    time.sleep(0.1)
    keyboard.release(Key.space)
    print("Finished jumping.")

def spin(duration):
    print("Spinning...")
    keyboard.press(Key.left)  # Assuming spinning left
    time.sleep(duration)
    keyboard.release(Key.left)
    print("Stopped spinning.")

def move_left(duration):
    print("Moving left...")
    keyboard.press('a')
    time.sleep(duration)
    keyboard.release('a')
    print("Stopped moving left.")

def turn_left(duration):
    print(f"Turning left for {duration} seconds...")
    keyboard.press(Key.left)
    time.sleep(duration)
    keyboard.release(Key.left)

def turn_right(duration):
    print("Turning right")
    keyboard.press(Key.right)
    time.sleep(duration)
    keyboard.release(Key.right)

try:
    close_console()
    time.sleep(1) # Delay before the actions start

    # Execute actions in sequence (In Seconds)
    move_forward(1.8)   # Move forward
    jump()              # Jump
    time.sleep(18)      # Wait for first door
    move_forward(1.8)   # Move forward
    time.sleep(15)      # Wait 2nd door
    move_forward(0.5)   # Move toward desk
    turn_right(0.3)     # Turn right slightly
    move_forward(1.5)   # Forward into coridoor
    turn_left(0.31)     # Slight left
    move_forward(2.9)   # Move forward down coridoor
    turn_left(0.48)     # Turn left
    move_forward(0.9)   # Move down corridoor
    move_forward(0.39)  # Move forward
    turn_right(0.5)     # Turn right to go down ramp
    move_forward(0.8)   # Move Forward down ramp
    jump()              # Jump
    move_forward(3)     # Move forward
    turn_right(0.5)     # Turn towards changing room coridoor
    move_forward(1.5)   # Move toward changing room


except KeyboardInterrupt:
    print("Script interrupted by user.")