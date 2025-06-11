import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time

class HandPongGame:
    def __init__(self):
        # Initialize MediaPipe with better settings
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Detect both hands
            min_detection_confidence=0.3,  # Lower threshold for better detection
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Game state
        self.game_running = False
        self.left_hand_detected = False
        self.right_hand_detected = False
        self.score = {'player1': 0, 'player2': 0}
        
        # Game objects
        self.canvas_width = 600
        self.canvas_height = 400
        self.ball = {
            'x': self.canvas_width // 2,
            'y': self.canvas_height // 2,
            'dx': 4,
            'dy': 4,
            'radius': 8
        }
        self.paddle1 = {'x': 10, 'y': 180, 'width': 8, 'height': 80}
        self.paddle2 = {'x': 582, 'y': 180, 'width': 8, 'height': 80}
        self.paddle_speed = 6
        
        # Camera
        self.cap = None
        self.current_frame = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the Tkinter UI"""
        self.root = tk.Tk()
        self.root.title("🏓 Hand Pong Game (Python Desktop App)")
        self.root.configure(bg='#1e293b')
        self.root.geometry("850x750")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (425)
        y = (self.root.winfo_screenheight() // 2) - (375)
        self.root.geometry(f"850x750+{x}+{y}")
        
        # Main container
        main_container = tk.Frame(self.root, bg='#1e293b', padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = tk.Frame(main_container, bg='#1e293b')
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title = tk.Label(
            title_frame,
            text="🏓 HAND PONG GAME (Python Desktop)",
            font=('Arial', 20, 'bold'),
            fg='white',
            bg='#1e293b'
        )
        title.pack()
        
        # Status bar
        status_frame = tk.Frame(main_container, bg='#374151', padx=15, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Camera status
        self.camera_status = tk.Label(
            status_frame,
            text="📹 Camera: OFF",
            font=('Arial', 11, 'bold'),
            fg='#ef4444',
            bg='#374151'
        )
        self.camera_status.pack(side=tk.LEFT)
        
        # Left hand status
        self.left_hand_status = tk.Label(
            status_frame,
            text="👈 Left Hand: ❌",
            font=('Arial', 11, 'bold'),
            fg='#ef4444',
            bg='#374151'
        )
        self.left_hand_status.pack(side=tk.LEFT, padx=(15, 0))
        
        # Right hand status
        self.right_hand_status = tk.Label(
            status_frame,
            text="👉 Right Hand: ❌",
            font=('Arial', 11, 'bold'),
            fg='#ef4444',
            bg='#374151'
        )
        self.right_hand_status.pack(side=tk.LEFT, padx=(15, 0))
        
        # Score
        self.score_display = tk.Label(
            status_frame,
            text="Score: 0 - 0",
            font=('Arial', 12, 'bold'),
            fg='#22c55e',
            bg='#374151'
        )
        self.score_display.pack(side=tk.RIGHT)
        
        # Game canvas
        canvas_frame = tk.Frame(main_container, bg='#0f172a', padx=5, pady=5)
        canvas_frame.pack(pady=(0, 15))
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='#0f172a',
            highlightthickness=2,
            highlightbackground='#22c55e'
        )
        self.canvas.pack()
        
        # Instructions
        instructions_frame = tk.Frame(main_container, bg='#374151', padx=15, pady=10)
        instructions_frame.pack(fill=tk.X, pady=(0, 15))
        
        instructions = tk.Label(
            instructions_frame,
            text="🎮 CONTROLS: Left Hand = Left Paddle | Right Hand = Right Paddle | Move hands UP/DOWN to control paddles",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg='#374151'
        )
        instructions.pack()
        
        # Bottom section with camera and controls
        bottom_frame = tk.Frame(main_container, bg='#1e293b')
        bottom_frame.pack(fill=tk.X)
        
        # Camera preview (left side) - BIGGER
        camera_container = tk.Frame(bottom_frame, bg='#374151', padx=15, pady=15)
        camera_container.pack(side=tk.LEFT, fill=tk.Y)
        
        camera_title = tk.Label(
            camera_container,
            text="📹 LIVE CAMERA FEED",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#374151'
        )
        camera_title.pack(pady=(0, 10))
        
        self.camera_preview = tk.Label(
            camera_container,
            text="📷 Camera is OFF\n\n🎮 Click START GAME\nto turn on camera\n\n✋ Show both hands\nfor best control",
            width=30,
            height=12,
            bg='#1f2937',
            fg='#9ca3af',
            font=('Arial', 9),
            justify=tk.CENTER
        )
        self.camera_preview.pack()
        
        # Control buttons (right side)
        button_container = tk.Frame(bottom_frame, bg='#1e293b')
        button_container.pack(side=tk.RIGHT, fill=tk.Y, expand=True, padx=(20, 0))
        
        # START/STOP button
        self.start_stop_button = tk.Button(
            button_container,
            text="🎮 START GAME\n📹 Turn ON Camera\n✋ Enable Hand Control",
            font=('Arial', 14, 'bold'),
            bg='#22c55e',
            fg='white',
            padx=25,
            pady=25,
            command=self.toggle_game,
            relief=tk.RAISED,
            bd=4,
            cursor='hand2',
            activebackground='#16a34a'
        )
        self.start_stop_button.pack(expand=True, fill=tk.BOTH)
        
        # Control mode info
        mode_info = tk.Label(
            button_container,
            text="🎯 GAME MODES:\n• 1 Hand: You vs AI\n• 2 Hands: Hand vs Hand",
            font=('Arial', 9),
            fg='#94a3b8',
            bg='#1e293b',
            justify=tk.LEFT
        )
        mode_info.pack(pady=(10, 0))
        
        # Quit button
        quit_btn = tk.Button(
            button_container,
            text="❌ QUIT GAME",
            font=('Arial', 11, 'bold'),
            bg='#ef4444',
            fg='white',
            padx=20,
            pady=8,
            command=self.quit_game,
            relief=tk.RAISED,
            bd=2,
            cursor='hand2'
        )
        quit_btn.pack(pady=(10, 0))
        
        # Initialize display
        self.draw_game()
        
        # Show welcome message
        self.root.after(1000, self.show_welcome)
        
    def show_welcome(self):
        """Show welcome message"""
        messagebox.showinfo(
            "🎮 Welcome to Hand Pong!",
            "🏓 HAND PONG GAME\n\n"
            "🖥️ This is a Python Desktop Application\n"
            "(Not a web browser game)\n\n"
            "🎮 HOW TO PLAY:\n"
            "1️⃣ Click 'START GAME' button\n"
            "2️⃣ Allow camera access\n"
            "3️⃣ Show your hands to the camera\n"
            "4️⃣ Move hands UP/DOWN to control paddles\n\n"
            "🎯 CONTROL MODES:\n"
            "• 1 Hand: You control left paddle vs AI\n"
            "• 2 Hands: Left hand = left paddle, Right hand = right paddle\n\n"
            "Ready to play? 🚀"
        )
        
    def toggle_game(self):
        """Toggle game on/off"""
        if not self.game_running:
            self.start_game()
        else:
            self.stop_game()
            
    def start_game(self):
        """Start the game and camera"""
        print("🎮 Starting Hand Pong Game...")
        
        try:
            # Initialize camera
            print("📹 Initializing camera...")
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                messagebox.showerror(
                    "❌ Camera Error", 
                    "Cannot access camera!\n\n"
                    "Troubleshooting:\n"
                    "• Make sure camera is connected\n"
                    "• Close other apps using camera\n"
                    "• Check camera permissions\n"
                    "• Try restarting the application"
                )
                return
                
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Update game state
            self.game_running = True
            self.reset_game()
            
            # Update UI
            self.start_stop_button.config(
                text="🛑 STOP GAME\n📹 Turn OFF Camera\n⏹️ Stop Hand Control",
                bg='#ef4444',
                activebackground='#dc2626'
            )
            
            self.camera_status.config(
                text="📹 Camera: ON ✅",
                fg='#22c55e'
            )
            
            # Start game loop
            self.game_loop()
            
            print("✅ Game started successfully!")
            print("✋ Show your hands to the camera to control the paddles!")
            
        except Exception as e:
            print(f"❌ Error starting game: {e}")
            messagebox.showerror("Error", f"Failed to start game:\n{str(e)}")
            
    def stop_game(self):
        """Stop the game and camera"""
        print("🛑 Stopping game...")
        
        self.game_running = False
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # Update UI
        self.start_stop_button.config(
            text="🎮 START GAME\n📹 Turn ON Camera\n✋ Enable Hand Control",
            bg='#22c55e',
            activebackground='#16a34a'
        )
        
        self.camera_status.config(
            text="📹 Camera: OFF",
            fg='#ef4444'
        )
        
        self.left_hand_status.config(
            text="👈 Left Hand: ❌",
            fg='#ef4444'
        )
        
        self.right_hand_status.config(
            text="👉 Right Hand: ❌",
            fg='#ef4444'
        )
        
        # Clear camera preview
        self.camera_preview.config(
            text="📷 Camera is OFF\n\n🎮 Click START GAME\nto turn on camera\n\n✋ Show both hands\nfor best control",
            image=''
        )
        
        self.left_hand_detected = False
        self.right_hand_detected = False
        print("✅ Game stopped!")
        
    def reset_game(self):
        """Reset game state"""
        self.score = {'player1': 0, 'player2': 0}
        self.ball['x'] = self.canvas_width // 2
        self.ball['y'] = self.canvas_height // 2
        self.ball['dx'] = 4 * (1 if np.random.random() > 0.5 else -1)
        self.ball['dy'] = 4 * (1 if np.random.random() > 0.5 else -1)
        
    def game_loop(self):
        """Main game loop"""
        if not self.game_running:
            return
            
        try:
            # Process camera and hands
            self.process_camera()
            
            # Update game physics
            self.update_game()
            
            # Update display
            self.update_display()
            
        except Exception as e:
            print(f"⚠️ Game loop error: {e}")
            
        # Continue loop at 60 FPS
        self.root.after(16, self.game_loop)
        
    def process_camera(self):
        """Process camera and detect hands"""
        if not self.cap:
            return
            
        ret, frame = self.cap.read()
        if not ret:
            print("⚠️ Failed to read camera frame")
            return
            
        # Flip for mirror effect
        frame = cv2.flip(frame, 1)
        self.current_frame = frame.copy()
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process hands
        results = self.hands.process(rgb_frame)
        
        # Reset hand detection
        self.left_hand_detected = False
        self.right_hand_detected = False
        
        if results.multi_hand_landmarks and results.multi_handedness:
            print(f"🖐️ Detected {len(results.multi_hand_landmarks)} hand(s)")
            
            for i, (landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                # Determine if it's left or right hand
                hand_label = handedness.classification[0].label
                
                # Get hand position (using middle finger tip - landmark 12)
                middle_finger = landmarks.landmark[12]
                
                # Convert to pixel coordinates
                h, w, _ = frame.shape
                hand_x = middle_finger.x * w
                hand_y = middle_finger.y * h
                
                # Map to paddle position
                paddle_y = (hand_y / h) * self.canvas_height
                target_y = max(0, min(paddle_y - 40, self.canvas_height - 80))
                
                # Control paddles based on hand
                if hand_label == "Left":  # User's left hand (appears on right side of mirrored image)
                    self.right_hand_detected = True
                    # Smooth movement for right paddle
                    self.paddle2['y'] = int(self.paddle2['y'] * 0.7 + target_y * 0.3)
                    print(f"👉 Right hand detected at y={int(hand_y)}")
                    
                elif hand_label == "Right":  # User's right hand (appears on left side of mirrored image)
                    self.left_hand_detected = True
                    # Smooth movement for left paddle
                    self.paddle1['y'] = int(self.paddle1['y'] * 0.7 + target_y * 0.3)
                    print(f"👈 Left hand detected at y={int(hand_y)}")
                
                # Draw hand landmarks on frame
                self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        # Update camera preview
        self.update_camera_preview(frame)
        
    def update_camera_preview(self, frame):
        """Update camera preview with current frame"""
        try:
            # Resize frame for preview (bigger size)
            preview_frame = cv2.resize(frame, (240, 180))
            preview_frame = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img = Image.fromarray(preview_frame)
            photo = ImageTk.PhotoImage(img)
            
            # Update preview
            self.camera_preview.config(image=photo, text='')
            self.camera_preview.image = photo  # Keep reference
            
        except Exception as e:
            print(f"📹 Camera preview error: {e}")
            
    def update_game(self):
        """Update game physics"""
        # AI control for paddles when hands not detected
        if not self.left_hand_detected:
            # AI controls left paddle
            paddle_center = self.paddle1['y'] + self.paddle1['height'] // 2
            if paddle_center < self.ball['y'] - 20:
                self.paddle1['y'] = min(self.paddle1['y'] + 3, 
                                      self.canvas_height - self.paddle1['height'])
            elif paddle_center > self.ball['y'] + 20:
                self.paddle1['y'] = max(self.paddle1['y'] - 3, 0)
                
        if not self.right_hand_detected:
            # AI controls right paddle
            paddle_center = self.paddle2['y'] + self.paddle2['height'] // 2
            if paddle_center < self.ball['y'] - 20:
                self.paddle2['y'] = min(self.paddle2['y'] + 3, 
                                      self.canvas_height - self.paddle2['height'])
            elif paddle_center > self.ball['y'] + 20:
                self.paddle2['y'] = max(self.paddle2['y'] - 3, 0)
        
        # Ball movement
        self.ball['x'] += self.ball['dx']
        self.ball['y'] += self.ball['dy']
        
        # Ball collision with top/bottom walls
        if self.ball['y'] <= self.ball['radius'] or self.ball['y'] >= self.canvas_height - self.ball['radius']:
            self.ball['dy'] = -self.ball['dy']
            
        # Ball collision with paddles
        # Left paddle collision
        if (self.ball['x'] - self.ball['radius'] <= self.paddle1['x'] + self.paddle1['width'] and
            self.ball['y'] >= self.paddle1['y'] and
            self.ball['y'] <= self.paddle1['y'] + self.paddle1['height'] and
            self.ball['dx'] < 0):
            self.ball['dx'] = abs(self.ball['dx']) * 1.05  # Slight speed increase
            
        # Right paddle collision
        if (self.ball['x'] + self.ball['radius'] >= self.paddle2['x'] and
            self.ball['y'] >= self.paddle2['y'] and
            self.ball['y'] <= self.paddle2['y'] + self.paddle2['height'] and
            self.ball['dx'] > 0):
            self.ball['dx'] = -abs(self.ball['dx']) * 1.05  # Slight speed increase
            
        # Scoring
        if self.ball['x'] < 0:
            self.score['player2'] += 1
            self.reset_ball()
            print(f"🎯 Right player scores! Score: {self.score['player1']} - {self.score['player2']}")
        elif self.ball['x'] > self.canvas_width:
            self.score['player1'] += 1
            self.reset_ball()
            print(f"🎯 Left player scores! Score: {self.score['player1']} - {self.score['player2']}")
            
    def reset_ball(self):
        """Reset ball position"""
        self.ball['x'] = self.canvas_width // 2
        self.ball['y'] = self.canvas_height // 2
        self.ball['dx'] = 4 * (1 if np.random.random() > 0.5 else -1)
        self.ball['dy'] = 4 * (1 if np.random.random() > 0.5 else -1)
        
    def update_display(self):
        """Update all display elements"""
        # Update hand status
        if self.left_hand_detected:
            self.left_hand_status.config(
                text="👈 Left Hand: ✅",
                fg='#22c55e'
            )
        else:
            self.left_hand_status.config(
                text="👈 Left Hand: ❌",
                fg='#ef4444'
            )
            
        if self.right_hand_detected:
            self.right_hand_status.config(
                text="👉 Right Hand: ✅",
                fg='#22c55e'
            )
        else:
            self.right_hand_status.config(
                text="👉 Right Hand: ❌",
                fg='#ef4444'
            )
            
        # Update score
        self.score_display.config(
            text=f"Score: {self.score['player1']} - {self.score['player2']}"
        )
        
        # Draw game
        self.draw_game()
        
    def draw_game(self):
        """Draw the game"""
        self.canvas.delete("all")
        
        # Center line
        for i in range(0, self.canvas_height, 20):
            self.canvas.create_rectangle(
                self.canvas_width//2 - 1, i,
                self.canvas_width//2 + 1, i + 10,
                fill='#334155', outline=''
            )
            
        # Left paddle (changes color when hand detected)
        left_paddle_color = '#22c55e' if self.left_hand_detected else '#94a3b8'
        self.canvas.create_rectangle(
            self.paddle1['x'], self.paddle1['y'],
            self.paddle1['x'] + self.paddle1['width'],
            self.paddle1['y'] + self.paddle1['height'],
            fill=left_paddle_color, outline=''
        )
        
        # Right paddle (changes color when hand detected)
        right_paddle_color = '#22c55e' if self.right_hand_detected else '#94a3b8'
        self.canvas.create_rectangle(
            self.paddle2['x'], self.paddle2['y'],
            self.paddle2['x'] + self.paddle2['width'],
            self.paddle2['y'] + self.paddle2['height'],
            fill=right_paddle_color, outline=''
        )
        
        # Ball (changes color when any hand detected)
        ball_color = '#22c55e' if (self.left_hand_detected or self.right_hand_detected) else 'white'
        self.canvas.create_oval(
            self.ball['x'] - self.ball['radius'],
            self.ball['y'] - self.ball['radius'],
            self.ball['x'] + self.ball['radius'],
            self.ball['y'] + self.ball['radius'],
            fill=ball_color, outline=''
        )
        
    def quit_game(self):
        """Quit the application"""
        print("👋 Quitting Hand Pong Game...")
        if self.game_running:
            self.stop_game()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """Run the game"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)
        print("🏓 Hand Pong Game is ready!")
        print("🖥️ This is a Python Desktop Application")
        print("👀 Look for the game window with the START GAME button!")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        print("🚀 Launching Hand Pong Game...")
        print("🖥️ This runs as a Python Desktop Application (not in browser)")
        game = HandPongGame()
        game.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Make sure you have installed:")
        print("pip install opencv-python mediapipe pillow numpy")
        input("Press Enter to exit...")
