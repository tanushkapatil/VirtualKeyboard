# 🖐️ Virtual Keyboard using Hand Tracking

A contactless virtual keyboard that uses real-time hand tracking to detect key presses using finger gestures. Built with OpenCV, CVZone, and Mediapipe, this project provides an innovative and accessible human-computer interaction experience.

---

## 🔧 Features

- Hand gesture-based typing with thumb and index finger pinch
- Custom on-screen keyboard layout with hover and press effects
- Real-time display of typed text
- Supports special keys: `Space`, `Back`, `Enter`, and `Close`
- Interactive UI with visual feedback (hover, press animations)
- No physical contact required – fully air-based interaction

---

## 🛠️ Tech Stack

- **Python**
- **OpenCV**
- **CVZone**
- **Mediapipe**
- **Pynput** (for simulating keyboard input)

---

## 🖥️ How It Works

1. **Hand Detection:** The webcam detects the hand using Mediapipe through CVZone.
2. **Finger Tracking:** Tracks the index and thumb fingers to determine if a key is hovered or clicked.
3. **Key Interaction:**
   - **Hover:** Highlights key in blue when finger is over it.
   - **Click:** If thumb and index come close (distance < threshold), the key is considered clicked.
4. **Typing:** Uses `pynput` to simulate real keystrokes and display on screen.

---

### 🔗 Dependencies

```bash
pip install opencv-python
pip install cvzone
pip install pynput
