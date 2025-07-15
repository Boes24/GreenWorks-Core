import os
from GreenWorks import GreenWorks


greenworks = GreenWorks(os.getenv("EMAIL"), os.getenv("PASSWORD")) # type: ignore

def test_login_and_user_info():
    assert greenworks.user_info.email == os.getenv("EMAIL")
    assert greenworks.login_info.access_token is not None
    assert greenworks.login_info.user_id is not None

test_login_and_user_info()

def test_get_devices():
    devices = greenworks.get_devices()
    assert len(devices) > 0, "No devices found."
    for device in devices:
        assert device.id is not None, "Device ID is None."
        assert device.name is not None, "Device name is None."
        print(f"Device ID: {device.id}, Name: {device.name}")
test_get_devices()
print("All tests passed.")
# This script tests the login functionality and retrieves user information and devices.
# It assumes that the environment variables EMAIL and PASSWORD are set with valid credentials.
# The tests check that the login is successful and that devices are retrieved correctly.
# If any test fails, an assertion error will be raised.