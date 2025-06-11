import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_and_install():
    """Check for required packages and install if missing"""
    print("🔍 Checking system requirements...")
    
    if not check_python_version():
        return False
    
    required_packages = {
        'cv2': 'opencv-python==4.8.1.78',
        'mediapipe': 'mediapipe==0.10.7', 
        'PIL': 'pillow==10.0.1',
        'numpy': 'numpy==1.24.3'
    }
    
    missing_packages = []
    
    print("\n📦 Checking required packages...")
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✅ {module} is already installed")
        except ImportError:
            print(f"❌ {module} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        try:
            # Upgrade pip first
            print("⬆️ Upgrading pip...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            
            # Install missing packages
            print("📥 Installing packages...")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install'
            ] + missing_packages)
            
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            print("\n🔧 Try manual installation:")
            for package in missing_packages:
                print(f"pip install {package}")
            return False
    else:
        print("\n✅ All required packages are already installed!")
    
    return True

def check_camera():
    """Check if camera is available"""
    print("\n📹 Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera is available!")
            cap.release()
            return True
        else:
            print("⚠️ Camera not detected or in use by another application")
            return False
    except Exception as e:
        print(f"⚠️ Camera check failed: {e}")
        return False

def main():
    """Main installer function"""
    print("🏓 Hand Pong Game - Setup Installer")
    print("=" * 50)
    
    # Check and install packages
    if not check_and_install():
        print("\n❌ Setup failed!")
        input("Press Enter to exit...")
        return
    
    # Check camera
    camera_ok = check_camera()
    
    print("\n" + "=" * 50)
    print("🎮 SETUP COMPLETE!")
    print("=" * 50)
    
    if camera_ok:
        print("✅ Everything is ready to play!")
        print("\n🚀 To start the game, run:")
        print("python hand_pong_improved.py")
    else:
        print("⚠️ Setup complete, but camera issues detected.")
        print("Make sure your camera is connected and not in use.")
        print("\n🚀 You can still try running:")
        print("python hand_pong_improved.py")
    
    print("\n📋 Game Controls:")
    print("• Left hand controls left paddle")
    print("• Right hand controls right paddle") 
    print("• Move hands up/down to control paddles")
    print("• AI takes over when hands not detected")
    
    print("\n🎯 Tips for best experience:")
    print("• Ensure good lighting")
    print("• Use plain background")
    print("• Keep hands clearly visible")
    print("• Stay 2-3 feet from camera")
    
    input("\nPress Enter to exit installer...")

if __name__ == "__main__":
    main()
