"""
Pytest configuration for Dash app tests.
Adds chromedriver directory to PATH if chromedriver.exe exists in the repo.
"""
import os

# Add parent directory to PATH so chromedriver.exe can be found
# (chromedriver may be in repo root)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_chromedriver_path = os.path.join(_root, "chromedriver.exe")
if os.path.exists(_chromedriver_path):
    os.environ["PATH"] = _root + os.pathsep + os.environ.get("PATH", "")
