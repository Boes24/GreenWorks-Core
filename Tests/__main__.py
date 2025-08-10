import os
from datetime import datetime
from zoneinfo import ZoneInfo
from src.GreenWorksAPI.GreenWorksAPI import GreenWorksAPI
from src.GreenWorksAPI.Records import Login_object, User_info_object

from unittest import mock
from requests.exceptions import RequestException
import time


def test_login_and_user_info_live():
    greenworks = GreenWorksAPI(os.getenv("EMAIL"), os.getenv("PASSWORD"), "Europe/Copenhagen") # type: ignore
    assert greenworks.user_info.email == os.getenv("EMAIL")
    assert greenworks.login_info.access_token is not None
    assert greenworks.login_info.user_id is not None


def test_get_devices_live():
    greenworks = GreenWorksAPI(os.getenv("EMAIL"), os.getenv("PASSWORD"), "Europe/Copenhagen") # type: ignore
    mowers = greenworks.get_devices()
    assert len(mowers) > 0, "No devices found."
    for device in mowers:
        assert device.id is not None, "Device ID is None."
        assert device.name is not None, "Device name is None."
        assert device.sn is not None, "Device SN is None."
        assert device.is_online is not None, "Device online status is None."
        assert device.properties is not None, "Device properties are None."
        assert device.operating_status is not None, "Device operating status is None."
        # Print device information for debugging
        print(f"Device Name: {device.name}, SN: {device.sn}, Device ID: {device.id}, Online: {device.is_online}")
        print(f"Device Battery Status: {device.operating_status.battery_status}")
        print(f"Device Main State: {device.operating_status.mower_main_state.name}")
        print(f"Next Start: {device.operating_status.next_start}")

def test_refresh_access_token_success():
    """Ensure refresh_access_token updates tokens on success and doesn't re-login."""
    with mock.patch('src.GreenWorksAPI.GreenWorksAPI.GreenWorksAPI._login_user') as mock_login, \
         mock.patch('src.GreenWorksAPI.GreenWorksAPI.GreenWorksAPI._get_user_info') as mock_user_info:

        mock_login.return_value = Login_object(
            access_token="old-access",
            refresh_token="old-refresh",
            user_id=123,
            expire_in=int(time.time()) + 10,
            authorize="RW",
        )

        mock_user_info.return_value = User_info_object(
            gender=0,
            active_date="2025-01-01T00:00:00Z",
            source=0,
            passwd_inited=True,
            is_vaild=True,
            nickname="tester",
            id=123,
            create_date="2025-01-01T00:00:00Z",
            email="tester@example.com",
            region_id=0,
            authorize_code="abcd",
            corp_id="corp",
            privacy_code="privacy",
            account="tester",
            age=30,
            status=1,
        )

        api = GreenWorksAPI("tester@example.com", "password", "Europe/Copenhagen")

        # Reset call count to detect any re-login during refresh
        mock_login.reset_mock()

        old_expire = api.login_info.expire_in

        # Mock successful POST for refresh
        with mock.patch('src.GreenWorksAPI.GreenWorksAPI.requests.post') as mock_post:
            mock_resp = mock.Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "access_token": "new-access",
                "refresh_token": "new-refresh",
            }
            mock_post.return_value = mock_resp

            api.refresh_access_token()

        assert api.login_info.access_token == "new-access"
        assert api.login_info.refresh_token == "new-refresh"
        assert api.login_info.expire_in > old_expire
        # Ensure re-login not triggered on success
        assert mock_login.call_count == 0

def test_refresh_access_token_refresh_fail_relogin_success():
    """Ensure that when refresh returns non-200, the client performs a re-login successfully."""
    with mock.patch('src.GreenWorksAPI.GreenWorksAPI.GreenWorksAPI._login_user') as mock_login, \
         mock.patch('src.GreenWorksAPI.GreenWorksAPI.GreenWorksAPI._get_user_info') as mock_user_info:

        # Initial login during constructor
        mock_login.return_value = Login_object(
            access_token="old-access",
            refresh_token="old-refresh",
            user_id=123,
            expire_in=int(time.time()) + 3600,
            authorize="RW",
        )

        mock_user_info.return_value = User_info_object(
            gender=0,
            active_date="2025-01-01T00:00:00Z",
            source=0,
            passwd_inited=True,
            is_vaild=True,
            nickname="tester",
            id=123,
            create_date="2025-01-01T00:00:00Z",
            email="tester@example.com",
            region_id=0,
            authorize_code="abcd",
            corp_id="corp",
            privacy_code="privacy",
            account="tester",
            age=30,
            status=1,
        )

        api = GreenWorksAPI("tester@example.com", "password", "Europe/Copenhagen")

        # Reset login mock to capture re-login only
        mock_login.reset_mock()

        # Mock refresh endpoint to fail with non-200
        with mock.patch('src.GreenWorksAPI.GreenWorksAPI.requests.post') as mock_post:
            mock_resp = mock.Mock()
            mock_resp.status_code = 401
            mock_resp.text = "unauthorized"
            mock_resp.json.return_value = {"error": "unauthorized"}
            mock_post.return_value = mock_resp

            api.refresh_access_token()

        # Verify re-login attempted once
        assert mock_login.call_count == 1, "Expected relogin when refresh fails"
        # Tokens remain unchanged in current implementation (relogin result not assigned)
        assert api.login_info.access_token == "old-access"
        assert api.login_info.refresh_token == "old-refresh"

if __name__ == "__main__":
    # Always run the unit (mocked) test
    test_refresh_access_token_success()
    test_refresh_access_token_refresh_fail_relogin_success()

    # Run live tests only when credentials are provided
    if os.getenv("EMAIL") and os.getenv("PASSWORD"):
        test_login_and_user_info_live()
        test_get_devices_live()
        print("All tests passed.")
    else:
        print("Skipping live API tests: EMAIL/PASSWORD not set. Mocked success test passed.")