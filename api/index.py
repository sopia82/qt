import sys
import os

# Set root directory in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Handler for Vercel
if __name__ == "__main__":
    app.run()
