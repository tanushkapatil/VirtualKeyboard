import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
import time

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Hand detector with higher detection confidence
detector = HandDetector(detectionCon=0.9, maxHands=1)
keyboard = Controller()

# Color scheme
COLORS = {
    "key": (50, 50, 50),
    "hover": (100, 100, 255),
    "press": (0, 200, 255),
    "text": (255, 255, 255),
    "border": (200, 200, 200),
    "display": (40, 40, 40),
    "instruction": (200, 200, 200)
}

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["Space", "Back", "Enter", "Close"]
]

class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text
        self.active = False

# Create buttons
buttonList = []
start_x, start_y = 50, 150
key_width, key_height = 85, 85
h_spacing, v_spacing = 10, 10

for row_idx, row in enumerate(keys):
    for col_idx, key in enumerate(row):
        if key == "Space":
            buttonList.append(Button([start_x, start_y + 3*(key_height+v_spacing)], key, [350, key_height]))
        elif key == "Back":
            buttonList.append(Button([start_x + 370, start_y + 3*(key_height+v_spacing)], key, [150, key_height]))
        elif key == "Enter":
            buttonList.append(Button([start_x + 540, start_y + 3*(key_height+v_spacing)], key, [150, key_height]))
        elif key == "Close":
            buttonList.append(Button([start_x + 710, start_y + 3*(key_height+v_spacing)], key, [150, key_height]))
        else:
            x = start_x + col_idx * (key_width + h_spacing)
            y = start_y + row_idx * (key_height + v_spacing)
            buttonList.append(Button([x, y], key))

# State management
class KeyboardState:
    def __init__(self):
        self.final_text = ""
        self.last_action_time = 0
        self.action_delay = 0.3  # seconds
        self.active_button = None
        self.gesture = "none"
        
    def reset_active_buttons(self):
        for btn in buttonList:
            btn.active = False

state = KeyboardState()

def draw_all(img, buttons):
    for btn in buttons:
        x, y = btn.pos
        w, h = btn.size
        
        # Determine button color based on state
        if btn.active:
            color = COLORS["press"]
        elif btn == state.active_button:
            color = COLORS["hover"]
        else:
            color = COLORS["key"]
        
        cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), COLORS["border"], 2)
        
        text_size = cv2.getTextSize(btn.text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        
        cv2.putText(img, btn.text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS["text"], 2)
    return img

def detect_gestures(lmList, fingers):
    # Check for pinch (click)
    if len(lmList) > 16:
        thumb_tip = lmList[4]
        index_tip = lmList[8]
        distance = np.hypot(thumb_tip[0]-index_tip[0], thumb_tip[1]-index_tip[1])
        if distance < 40:
            return "click"
    
    # Check for peace sign (space)
    if fingers and fingers[1] and fingers[2] and not fingers[0] and not fingers[3] and not fingers[4]:
        return "peace"
    
    # Check for thumbs up (enter)
    if fingers and fingers[0] and not any(fingers[1:]):
        return "thumbs_up"
    
    # Check for fist (backspace)
    if fingers and not any(fingers):
        return "fist"
    
    return "none"

def handle_key_press(button):
    current_time = time.time()
    if (current_time - state.last_action_time) < state.action_delay:
        return
    
    state.last_action_time = current_time
    button.active = True
    
    if button.text == "Space" and state.gesture == "peace":
        state.final_text += " "
        keyboard.press(' ')
    elif button.text == "Back" and state.gesture == "fist":
        state.final_text = state.final_text[:-1]
        keyboard.press('\b')
    elif button.text == "Enter" and state.gesture == "thumbs_up":
        state.final_text += "\n"
        keyboard.press('\n')
    elif button.text == "Close" and state.gesture == "click":
        cap.release()
        cv2.destroyAllWindows()
        exit()
    elif state.gesture == "click" and button.text not in ["Space", "Back", "Enter", "Close"]:
        state.final_text += button.text
        keyboard.press(button.text)

# Main window
cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Virtual Keyboard", 1280, 800)

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    state.reset_active_buttons()
    
    # Find hands
    hands, img = detector.findHands(img, flipType=False)
    img = draw_all(img, buttonList)
    
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        state.gesture = detect_gestures(lmList, fingers)
        
        # Find which key is being pointed at
        if len(lmList) > 8:
            for btn in buttonList:
                x, y = btn.pos
                w, h = btn.size
                
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    state.active_button = btn
                    handle_key_press(btn)
                    break
    
    # Display text
    cv2.rectangle(img, (50, 30), (1230, 100), COLORS["display"], cv2.FILLED)
    cv2.putText(img, state.final_text[-40:], (60, 80), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS["text"], 2)
    
    # Display gesture and instructions
    cv2.putText(img, f"Current Gesture: {state.gesture}", (50, 650), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS["instruction"], 2)
    
    instructions = [
        "HOW TO USE:",
        "- Point at keys with your index finger",
        "- PINCH (thumb+index) to type regular keys",
        "- PEACE SIGN (✌️) on SPACE for space",
        "- FIST (✊) on BACK for backspace",
        "- THUMBS UP (👍) on ENTER for new line",
        "- PINCH on CLOSE to exit"
    ]
    
    for i, instruction in enumerate(instructions):
        y_pos = 680 + i * 30
        cv2.putText(img, instruction, (50, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS["instruction"], 1)
    
    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
