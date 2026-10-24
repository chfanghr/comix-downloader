import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.utils import config as config_module


class ConfigPathTests(unittest.TestCase):
    def test_default_download_path_is_the_current_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "config.json"
            working_directory = Path(directory) / "work"
            working_directory.mkdir()
            with patch.object(config_module, "default_config_path", return_value=config_path), \
                 patch.object(
                     config_module.ConfigManager,
                     "_migrate_legacy_configs",
                     return_value=config_module.ConfigManager.DEFAULT_CONFIG.copy(),
                 ), \
                 patch.object(config_module.Path, "cwd", return_value=working_directory):
                config = config_module.ConfigManager()
                self.assertEqual(
                    config.get_download_config().download_path,
                    str(working_directory),
                )
