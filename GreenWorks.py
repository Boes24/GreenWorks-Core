# GreenWorks-Core/Main.py
import requests
from Objects import login_object, user_info_object, mower_info_object

class GreenWorks:
    """Greenworks - API Wrapper for Greenworks robotic lawn mower."""
    base_url = "https://xapi.globetools.systems/v2"
    def __init__(self, email: str, password: str):
        """Initialize the GreenWorks class with user credentials."""
        self.login_info = self.login_user(email, password)
        self.user_info = self.get_user_info(self.login_info.user_id, self.login_info.access_token)
        
        ## Get devices associated with the user
        self.devices = self.get_devices(self.user_info.id, self.login_info.access_token)
    
    def login_user(self, email: str, password: str):
        url = f"{self.base_url}/user_auth"
        body = {
            "corp_id": "100fa2b00b622800",
            "email": email,
            "password": password,
        }

        try:
            print(f"Logging in with email: {email}")  # Debugging output
            print(f"Request URL: {url}")  # Debugging output
            print(f"Request body: {body}")  # Debugging output
            # Send POST request to the API
            response = requests.post(url, json=body, timeout=10)
            
            response.raise_for_status()  # Stopper ved 4xx/5xx
            data = response.json()

            # Eventuelt check for nødvendige felter
            if "user_id" not in data or "access_token" not in data:
                raise ValueError("Login-svar mangler nødvendige felter: 'user_id' og/eller 'access_token'")

            return login_object(**data)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Login fejlede: netværksfejl ved {url}: {e} : {response.json()}") from e

        except ValueError as e:
            raise RuntimeError(f"Login fejlede: ugyldigt JSON-svar fra {url}: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Login fejlede: fejl ved oprettelse af login_object: {e}\nData: {data}") from e

    def get_user_info(self, user_id: int, access_token: str):
        url = f"{self.base_url}/user/{user_id}"
        headers = {
            "Access-Token": access_token
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Kaster exception på 4xx/5xx

            data = response.json()
            
            # Simpelt check for nødvendige felter (kan udvides)
            if "id" not in data:
                raise ValueError("Brugerdata mangler 'id' felt")

            return user_info_object(**data)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

        except ValueError as e:
            raise RuntimeError(f"Ugyldigt JSON-svar: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Fejl ved oprettelse af user_info_object: {e}") from e

    def get_devices(self, user_id: int, access_token: str):

        url = f"{self.base_url}/user/{user_id}/subscribe/devices?version=0"
        headers = {
            "Access-Token": access_token
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Stopper hvis status != 2xx

            data = response.json()

            # Tjek at 'list' findes i JSON og er en liste
            devices = data.get("list")
            if not isinstance(devices, list):
                raise ValueError("JSON-svar indeholder ikke en gyldig 'list' af enheder")

            return [mower_info_object(**device) for device in devices]

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

        except ValueError as e:
            raise RuntimeError(f"Ugyldigt JSON-svar fra {url}: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Fejl ved oprettelse af mower_info_object: {e}") from e

    def refresh_access_token(self, access_token: str, refresh_token: str):
        """
        Placeholder for a method to refresh the access token.
        This method should implement the logic to refresh the token if needed.
        """
        # Implement token refresh logic here
        
        
        pass

