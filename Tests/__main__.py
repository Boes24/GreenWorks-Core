import os
from datetime import datetime
from zoneinfo import ZoneInfo
from GreenWorksAPI.GreenWorksAPI import GreenWorks


greenworks = GreenWorks(os.getenv("EMAIL"), os.getenv("PASSWORD")) # type: ignore

def test_login_and_user_info():
    assert greenworks.user_info.email == os.getenv("EMAIL")
    assert greenworks.login_info.access_token is not None
    assert greenworks.login_info.user_id is not None

test_login_and_user_info()

def test_update_devices():
    greenworks.update_devices(greenworks.user_info.id)
    assert len(greenworks.Mowers) > 0, "No devices found."
    for device in greenworks.Mowers:
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
    

test_update_devices()
print("All tests passed.")
# This script tests the login functionality and retrieves user information and devices.
# It assumes that the environment variables EMAIL and PASSWORD are set with valid credentials.
# The tests check that the login is successful and that devices are retrieved correctly.
# If any test fails, an assertion error will be raised.