import unittest
import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.version_manager import VersionManager

from PyQt6.QtCore import QCoreApplication

class TestManagers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # QCoreApplication needed for QObject signals
        if not QCoreApplication.instance():
            cls.app = QCoreApplication(sys.argv)

    def test_version_manager_init(self):
        # Create a dummy config for testing
        config_path = "tests/test_version.json"
        with open(config_path, 'w') as f:
            f.write('{"versionName": "1.0.0"}')
            
        manager = VersionManager(config_path=config_path)
        self.assertIsNotNone(manager.current_version_info)
        self.assertEqual(manager.current_version_info['versionName'], "1.0.0")
        
        # Clean up
        if os.path.exists(config_path):
            os.remove(config_path)

if __name__ == '__main__':
    unittest.main()
