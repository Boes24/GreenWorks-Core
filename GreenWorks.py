# GreenWorks-Core/Main.py

from Methodes import Methodes

class GreenWorks:
    """Greenworks - API Wrapper for Greenworks robotic lawn mower."""
    URL: Methodes
    def __init__(self, email: str, password: str):
        """Initialize the GreenWorks class with user credentials."""
        self.URL = Methodes()
        self.login_info = self.URL.login_user(email, password)
        self.user_info = self.URL.get_user_info(self.login_info.user_id, self.login_info.access_token)
        
        ## Get devices associated with the user
        self.devices = self.URL.get_devices(self.user_info.id, self.login_info.access_token)

    def get_devices(self):
        """Return a list of mower_info_object for each device."""
        return self.URL.get_devices(self.user_info.id, self.login_info.access_token)
    
    