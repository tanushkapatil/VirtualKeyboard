import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import cvzone
from pynput.keyboard import Controller

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)
keyboard = Controller()

# Color scheme
BG_COLOR = (40, 40, 40)  # Dark gray background
KEY_COLOR = (70, 70, 70)  # Medium gray keys
HOVER_COLOR = (100, 100, 100)  # Light gray hover
PRESS_COLOR = (0, 150, 255)  # Orange press
TEXT_COLOR = (255, 255, 255)  # White text
DISPLAY_COLOR = (50, 50, 50)  # Darker gray for text display

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["Space", "Back", "Enter"]  # Special keys
]

finalText = ""

class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Create buttons
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "Space":
            buttonList.append(Button([100 * 2 + 50, 100 * 3 + 50], key, [400, 85]))
        elif key == "Back":
            buttonList.append(Button([100 * 7 + 50, 100 * 3 + 50], key, [170, 85]))
        elif key == "Enter":
            buttonList.append(Button([100 * 9 + 50, 100 * 3 + 50], key, [170, 85]))
        else:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

def drawAll(img, buttonList):
    # Draw background
    img[:] = BG_COLOR
    
    # Draw buttons
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        # Special styling for space bar
        if button.text == "Space":
            cv2.rectangle(img, (x, y), (x + w, y + h), KEY_COLOR, cv2.FILLED)
            cv2.putText(img, button.text, (x + 120, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
        else:
            cvzone.cornerRect(img, (x, y, w, h), 15, rt=0, colorC=KEY_COLOR, colorR=KEY_COLOR)
            cv2.putText(img, button.text, (x + 20, y + 60),
                        cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
    return img

while True:
    success, img = cap.read()
    if not success:
        continue
        
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)  # Already flipped
    
    img = drawAll(img, buttonList)

    if hands:
        hand1 = hands[0]
        lmList = hand1["lmList"]
        
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if len(lmList) > 12 and x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                # Hover effect
                cv2.rectangle(img, (x, y), (x + w, y + h), HOVER_COLOR, cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 60),
                            cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
                
                # Check for click
                length, _, _ = detector.findDistance(lmList[8][:2], lmList[12][:2], img)
                
                if length < 40:
                    # Press effect
                    cv2.rectangle(img, (x, y), (x + w, y + h), PRESS_COLOR, cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 60),
                                cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
                    
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
                    else:
                        finalText += button.text
                        keyboard.press(button.text)
                    
                    sleep(0.15)

    # Text display area
    cv2.rectangle(img, (50, 20), (1230, 100), DISPLAY_COLOR, cv2.FILLED)
    cv2.putText(img, finalText[-30:], (60, 80),  # Show last 30 characters
                cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
    
    # Instruction text
    cv2.putText(img, "Pinch to type | 'Q' to quit", (50, 700),
                cv2.FONT_HERSHEY_PLAIN, 2, (150, 150, 150), 2)

    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()