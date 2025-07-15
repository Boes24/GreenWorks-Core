from dataclasses import dataclass
@dataclass
class login_object:
    access_token: str
    refresh_token: str
    user_id: int
    expire_in: int
    authorize: str

@dataclass
class user_info_object:
    gender: int
    active_date: str
    source: int
    passwd_inited: bool
    is_vaild: bool
    nickname: str
    id: int
    create_date: str
    email: str
    region_id: int
    authorize_code: str
    corp_id: str
    privacy_code: str
    account: str
    age: int
    status: int
    
@dataclass
class mower_info_object:
    subscribe_date: str
    is_active: bool
    role: int
    last_login: str
    active_code: str
    active_date: str
    groups: str
    mcu_version: int
    firmware_version: int
    source: int
    mac: str
    product_id: str
    access_key: int
    authority: str
    name: str
    authorize_code: str
    id: int
    is_online: bool
    sn: str