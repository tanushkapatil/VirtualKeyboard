import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import cvzone
from pynput.keyboard import Controller

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Width
cap.set(4, 720)   # Height

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)
keyboard = Controller()

# Color scheme
KEY_COLOR = (0, 0, 0)          # Black keys
HOVER_COLOR = (200, 150, 0)    # Blue hover
PRESS_COLOR = (0, 150, 255)    # Orange press
TEXT_COLOR = (255, 255, 255)   # White text
BORDER_COLOR = (255, 255, 255) # White border
DISPLAY_COLOR = (40, 40, 40)   # Dark display area

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["Space", "Back", "Enter", "Close"]  # Special keys
]

finalText = ""

class Button:
    def __init__(self, pos, text, size=[80, 80]):  # Slightly smaller standard keys
        self.pos = pos
        self.size = size
        self.text = text

# Create buttons with proper spacing
buttonList = []
key_width, key_height = 80, 80
horizontal_spacing = 10
vertical_spacing = 10
start_x = 50
start_y = 150  # Starting position

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "Space":
            buttonList.append(Button([start_x, start_y + 3*(key_height+vertical_spacing)], 
                                  key, [300, key_height]))
        elif key == "Back":
            buttonList.append(Button([start_x + 320, start_y + 3*(key_height+vertical_spacing)], 
                                  key, [150, key_height]))
        elif key == "Enter":
            buttonList.append(Button([start_x + 480, start_y + 3*(key_height+vertical_spacing)], 
                                   key, [150, key_height]))
        elif key == "Close":
            buttonList.append(Button([start_x + 640, start_y + 3*(key_height+vertical_spacing)], 
                                   key, [150, key_height]))
        else:
            buttonList.append(Button([start_x + j*(key_width+horizontal_spacing), 
                                   start_y + i*(key_height+vertical_spacing)], 
                                  key))

def drawAll(img, buttonList):
    # Draw all keys with black background and white border
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        # Draw key with black background and white border
        cv2.rectangle(img, (x, y), (x + w, y + h), KEY_COLOR, cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), BORDER_COLOR, 2)
        
        # Center text based on key size
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, 2, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        
        cv2.putText(img, button.text, (text_x, text_y),
                   cv2.FONT_HERSHEY_PLAIN, 2, TEXT_COLOR, 2)
    return img

# Create a resizable window
cv2.namedWindow("Virtual Keyboard", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Virtual Keyboard", 1000, 700)  # Standard window size

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    
    img = drawAll(img, buttonList)

    if hands:
        hand1 = hands[0]
        lmList = hand1["lmList"]
        
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if len(lmList) > 12 and x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                # Hover effect (blue with black border)
                cv2.rectangle(img, (x, y), (x + w, y + h), HOVER_COLOR, cv2.FILLED)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2)  # Black border on hover
                
                # Center text
                text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, 2, 2)[0]
                text_x = x + (w - text_size[0]) // 2
                text_y = y + (h + text_size[1]) // 2
                
                cv2.putText(img, button.text, (text_x, text_y),
                           cv2.FONT_HERSHEY_PLAIN, 2, TEXT_COLOR, 2)
                
                # Check for click (thumb and index finger)
                length, _, _ = detector.findDistance(lmList[8][:2], lmList[4][:2], img)
                
                if length < 40:
                    # Press effect (orange with black border)
                    cv2.rectangle(img, (x, y), (x + w, y + h), PRESS_COLOR, cv2.FILLED)
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2)
                    cv2.putText(img, button.text, (text_x, text_y),
                               cv2.FONT_HERSHEY_PLAIN, 2, TEXT_COLOR, 2)
                    
                    # Handle key presses
                    if button.text == "Back":
                        if len(finalText) > 0:
                            finalText = finalText[:-1]
                            keyboard.press('\b')
                    elif button.text == "Space":
                        finalText += " "
                        keyboard.press(' ')
                    elif button.text == "Enter":
                        finalText += "\n"
                        keyboard.press('\n')
                    elif button.text == "Close":
                        cap.release()
                        cv2.destroyAllWindows()
                        exit()
                    else:
                        finalText += button.text
                        keyboard.press(button.text)
                    
                    sleep(0.15)

    # Text display area at top
    cv2.rectangle(img, (50, 30), (950, 100), DISPLAY_COLOR, cv2.FILLED)
    cv2.putText(img, finalText[-30:], (60, 80),
               cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
    
    # Instruction text at bottom
    cv2.putText(img, "Pinch (thumb+index) to type | Close window to exit", (50, 680),
               cv2.FONT_HERSHEY_PLAIN, 2, (200, 200, 200), 2)

    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.getWindowProperty("Virtual Keyboard", cv2.WND_PROP_VISIBLE) < 1:
        break
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
