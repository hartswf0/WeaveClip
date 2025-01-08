import pytest
import os
import sys

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up the test environment before each test."""
    # Ensure Qt plugin path is set
    if 'QT_QPA_PLATFORM_PLUGIN_PATH' not in os.environ:
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/Users/gaia/anaconda3/plugins'
    
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    yield  # Run the test
    
    # Cleanup after test if needed
    pass
