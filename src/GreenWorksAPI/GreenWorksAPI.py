# GreenWorks-Core/Main.py
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from datetime import datetime
import requests
import json
from Records import Login_object, Mower_operating_status, User_info_object, Mower_properties
from Enums import MowerState

@dataclass
class Mower:
    id: int
    name: str
    sn: str
    is_online: bool
    properties: Mower_properties
    operating_status: Mower_operating_status

class GreenWorksAPI:
    """Greenworks - API Wrapper for Greenworks robotic lawn mower."""
    base_url = "https://xapi.globetools.systems/v2"

    def __init__(self, email: str, password: str, timezone: str):
        """Initialize the GreenWorks class with user credentials."""
        self.login_info = self.login_user(email, password)
        self.user_info = self.get_user_info(self.login_info.user_id)
        self.UserTimezone = ZoneInfo(timezone)

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
            
            if response.status_code == 401:
                raise UnauthorizedException('Wrong login')
            response.raise_for_status()  # Stopper ved 4xx/5xx
            data = response.json()

            # Eventuelt check for nødvendige felter
            if "user_id" not in data or "access_token" not in data:
                raise ValueError("Login-svar mangler nødvendige felter: 'user_id' og/eller 'access_token'")

            return Login_object(**data)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Login fejlede: netværksfejl ved {url}: {e} : {response.json()}") from e

        except ValueError as e:
            raise RuntimeError(f"Login fejlede: ugyldigt JSON-svar fra {url}: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Login fejlede: fejl ved oprettelse af login_object: {e}\nData: {data}") from e

    def get_user_info(self, user_id: int) -> User_info_object:
        url = f"{self.base_url}/user/{user_id}"
        headers = {
            "Access-Token": self.login_info.access_token
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Kaster exception på 4xx/5xx

            data = response.json()
            
            # Simpelt check for nødvendige felter (kan udvides)
            if "id" not in data:
                raise ValueError("Brugerdata mangler 'id' felt")

            return User_info_object(**data)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

        except ValueError as e:
            raise RuntimeError(f"Ugyldigt JSON-svar: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Fejl ved oprettelse af user_info_object: {e}") from e
        
    def get_mower_operating_status(self, product_id: int, mower_id: int) -> Mower_operating_status:
        """
        Placeholder for a method to update mower information.
        This method should implement the logic to update mower details.
        """
        url = f"https://xapi.globetools.systems/v2/product/{product_id}/v_device/{mower_id}?datapoints=32"
        headers = {
            "Access-Token": self.login_info.access_token
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Stopper ved 4xx/5xx


            # Feltet "32" er en streng med JSON-indhold
            raw_32 = response.json().get("32", "{}")
            parsed_32 = json.loads(raw_32)
            data = parsed_32.get("request", {})

            return Mower_operating_status(
                battery_status=data.get("battery_status", -1),
                mower_main_state=MowerState(data.get("mower_main_state", -1)),
                next_start=datetime.fromtimestamp(data.get("next_start", ""), tz=self.UserTimezone),
                request_time=datetime.fromisoformat(data.get("request_time", "").replace("Z", "+00:00")).astimezone(self.UserTimezone)
            )

        except ValueError as e:
            raise RuntimeError(f"Ugyldigt JSON-svar fra {url}: {e}") from e
        except TypeError as e:
            raise RuntimeError(f"Fejl ved oprettelse af mower_info_object: {e}") from e
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

    def get_devices(self, user_id: int) -> list[Mower]:
        Mowers = []  # Tøm listen før opdatering
        url = f"{self.base_url}/user/{user_id}/subscribe/devices?version=0"
        headers = {
            "Access-Token": self.login_info.access_token
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Stopper hvis status != 2xx

            data = response.json()

            # Tjek at 'list' findes i JSON og er en liste
            devices = data.get("list")
            if not isinstance(devices, list):
                raise ValueError("JSON-svar indeholder ikke en gyldig 'list' af enheder")
            
            # Returner en liste af Mower objekter
            for device in devices:
                mower_properties = self.get_device_properties(device.get("product_id"), device.get("id"))
                if mower_properties is None:
                    raise ValueError(f"Kunne ikke hente egenskaber for enhed med ID {device.get('id')}")
                mower_operating_status = self.get_mower_operating_status(device.get("product_id"), device.get("id"))
                if mower_operating_status is None:
                    raise ValueError(f"Kunne ikke hente tilstand for enhed med ID {device.get('id')}")
                # Opret Mower objekt med de hentede data
                mower = Mower(
                    id=device.get("id"),
                    name=device.get("name"),
                    sn=device.get("sn"),
                    is_online=device.get("is_online"),
                    properties=mower_properties,
                    operating_status=mower_operating_status
                )
                # Tilføj Mower objektet til listen
                Mowers.append(mower)

            return Mowers  # Returner listen af Mower objekter

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

        except ValueError as e:
            raise RuntimeError(f"Ugyldigt JSON-svar fra {url}: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Fejl ved oprettelse af mower_info_object: {e}") from e
        
    def get_device_properties(self, product_id: int, device_id: int) -> Mower_properties:
        """
        Placeholder for a method to get device properties.
        This method should implement the logic to retrieve device properties.
        """
        url = f"{self.base_url}/product/{product_id}/device/{device_id}/property"
        headers = {
            "Access-Token": self.login_info.access_token
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Stopper ved 4xx/5xx
            
            data = response.json()
            return Mower_properties(**data)  # Returner de hentede enhedsegenskaber

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

    def refresh_access_token(self, access_token: str, refresh_token: str):
        """
        Placeholder for a method to refresh the access token.
        This method should implement the logic to refresh the token if needed.
        """
        # Implement token refresh logic here
        
        
        pass

class UnauthorizedException(Exception):
    pass

class LastConfig:
    def __init__(self, data):
        self.name = data.get("name", "")
        self.timestamp = data.get("timestamp")
        self.mower = Mower(data.get("id"),data.get("name"), data.get("sn"), data.get("is_online"), data.get("properties"), data.get("operating_status"))