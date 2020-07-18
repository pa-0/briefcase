from unittest.mock import MagicMock

import pytest
from requests import exceptions as requests_exceptions

from briefcase.exceptions import NetworkFailure
from briefcase.integrations.linuxdeploy import LinuxDeploy


@pytest.fixture
def mock_command(tmp_path):
    command = MagicMock()
    command.host_arch = 'wonky'
    command.tools_path = tmp_path / 'tools'
    command.tools_path.mkdir()

    return command


def test_upgrade_exists(mock_command, tmp_path):
    "If linuxdeploy already exists, upgrading deletes first"
    appimage_path = tmp_path / 'tools' / 'linuxdeploy-wonky.AppImage'

    # Mock the existence of an install
    appimage_path.touch()

    # Mock a successful download
    mock_command.download_url.return_value = 'new-downloaded-file'

    # Create a linuxdeploy wrapper, then upgrade it
    linuxdeploy = LinuxDeploy(mock_command)
    linuxdeploy.upgrade()

    # The mock file will be deleted
    assert not appimage_path.exists()

    # A download is invoked
    mock_command.download_url.assert_called_with(
        url='https://github.com/linuxdeploy/linuxdeploy/'
            'releases/download/continuous/linuxdeploy-wonky.AppImage',
        download_path=tmp_path / 'tools'
    )
    # The downloaded file will be made executable
    mock_command.os.chmod.assert_called_with('new-downloaded-file', 0o755)


def test_upgrade_does_not_exist(mock_command, tmp_path):
    "If linuxdeploy doesn't exist, it is downloaded"
    # Mock a successful download
    mock_command.download_url.return_value = 'new-downloaded-file'

    # Create a linuxdeploy wrapper, then upgrade it
    linuxdeploy = LinuxDeploy(mock_command)
    linuxdeploy.upgrade()

    # A download is invoked
    mock_command.download_url.assert_called_with(
        url='https://github.com/linuxdeploy/linuxdeploy/'
            'releases/download/continuous/linuxdeploy-wonky.AppImage',
        download_path=tmp_path / 'tools'
    )
    # The downloaded file will be made executable
    mock_command.os.chmod.assert_called_with('new-downloaded-file', 0o755)


def test_upgrade_linuxdeploy_download_failure(mock_command, tmp_path):
    "If linuxdeploy doesn't exist, but a download failure occurs, an error is raised"
    appimage_path = tmp_path / 'tools' / 'linuxdeploy-wonky.AppImage'

    # Mock the existence of an install
    appimage_path.touch()

    mock_command.download_url.side_effect = requests_exceptions.ConnectionError

    # Create a linuxdeploy wrapper, then upgrade it.
    # The upgrade will fail
    linuxdeploy = LinuxDeploy(mock_command)
    with pytest.raises(NetworkFailure):
        linuxdeploy.upgrade()

    # The mock file will be deleted
    assert not appimage_path.exists()

    # A download was invoked
    mock_command.download_url.assert_called_with(
        url='https://github.com/linuxdeploy/linuxdeploy/'
            'releases/download/continuous/linuxdeploy-wonky.AppImage',
        download_path=tmp_path / 'tools'
    )
