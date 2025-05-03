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
KEY_COLOR = (60, 60, 60)    # Dark gray keys
HOVER_COLOR = (200, 150, 0)  # Blueish hover (BGR format)
PRESS_COLOR = (0, 150, 255)  # Orange press
TEXT_COLOR = (255, 255, 255) # White text
DISPLAY_COLOR = (40, 40, 40) # Dark gray for text display

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["Space", "Back", "Enter"]  # Special keys
]

finalText = ""

class Button:
    def __init__(self, pos, text, size=[90, 90]):  # Increased key size
        self.pos = pos
        self.size = size
        self.text = text

# Create buttons with proper spacing
buttonList = []
key_width, key_height = 90, 90
horizontal_spacing = 15
vertical_spacing = 15
start_x = 50
start_y = 150  # Lowered to make space for text display

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "Space":
            buttonList.append(Button([start_x + 2*(key_width+horizontal_spacing), 
                                   start_y + 3*(key_height+vertical_spacing)], 
                                  key, [400, key_height]))
        elif key == "Back":
            buttonList.append(Button([start_x + 7*(key_width+horizontal_spacing), 
                                   start_y + 3*(key_height+vertical_spacing)], 
                                  key, [180, key_height]))
        elif key == "Enter":
            buttonList.append(Button([start_x + 9*(key_width+horizontal_spacing), 
                                    start_y + 3*(key_height+vertical_spacing)], 
                                   key, [180, key_height]))
        else:
            buttonList.append(Button([start_x + j*(key_width+horizontal_spacing), 
                                   start_y + i*(key_height+vertical_spacing)], 
                                  key))

def drawAll(img, buttonList):
    # Create a semi-transparent background for keys only
    overlay = img.copy()
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (40, 40, 40), cv2.FILLED)
    
    # Blend the overlay with original image
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    
    # Draw buttons
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        # Special styling for space bar
        if button.text == "Space":
            cv2.rectangle(img, (x, y), (x + w, y + h), KEY_COLOR, cv2.FILLED)
            cv2.putText(img, button.text, (x + 140, y + 60),
                       cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), KEY_COLOR, cv2.FILLED)
            cv2.putText(img, button.text, (x + 25, y + 60),
                       cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
    return img

while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)
    
    # Resize window to be more compact vertically
    img = cv2.resize(img, (1280, 720))
    
    img = drawAll(img, buttonList)

    if hands:
        hand1 = hands[0]
        lmList = hand1["lmList"]
        
        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if len(lmList) > 12 and x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                # Hover effect (blueish)
                cv2.rectangle(img, (x, y), (x + w, y + h), HOVER_COLOR, cv2.FILLED)
                cv2.putText(img, button.text, (x + 25, y + 60),
                           cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
                
                # Check for click (thumb and index finger)
                length, _, _ = detector.findDistance(lmList[8][:2], lmList[4][:2], img)
                
                if length < 40:
                    # Press effect
                    cv2.rectangle(img, (x, y), (x + w, y + h), PRESS_COLOR, cv2.FILLED)
                    cv2.putText(img, button.text, (x + 25, y + 60),
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

    # Text display area at top
    cv2.rectangle(img, (50, 30), (1230, 100), DISPLAY_COLOR, cv2.FILLED)
    cv2.putText(img, finalText[-30:], (60, 80),
               cv2.FONT_HERSHEY_PLAIN, 3, TEXT_COLOR, 3)
    
    # Instruction text at bottom
    cv2.putText(img, "Pinch (thumb+index) to type | Close window to exit", (50, 690),
               cv2.FONT_HERSHEY_PLAIN, 2, (200, 200, 200), 2)

    cv2.imshow("Virtual Keyboard", img)
    
    if cv2.getWindowProperty("Virtual Keyboard", cv2.WND_PROP_VISIBLE) < 1:
        break
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()