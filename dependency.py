import subprocess
import sys

def install_packages():
    """Install required packages"""
    packages = [
        'opencv-python==4.8.1.78',
        'mediapipe==0.10.7',
        'pillow==10.0.1',
        'numpy==1.24.3'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
            return False
    
    print("\n✓ All packages installed successfully!")
    print("You can now run: python hand_pong.py")
    return True

if __name__ == "__main__":
    install_packages()
