from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class RequestBodyIn(BaseModel):
    kid: str = Field(None, alias='_id')
    description: str = None
    price: float
    tax: float = None
    additional_info: List[str] = []
    additional_space: str = None
    available_from: str = None
    bathroom: str = None
    bathroom_equip: str = None
    bathroom_number: str = None
    building_material: str = None
    building_type: str = None
    comute: str = None
    condition: str = None
    condition_electric_wires: str = None
    description: str
    download_date: str = None
    download_date_utc: float = None
    education: str = None
    finishing_stage: str = None
    flat_height: str = None
    flat_living_size: float = None
    flat_size: float
    floor: float = None
    floor_attic: float = None
    floor_basement: float = None
    for_office: str = None
    GC_addr_city: str = None
    GC_addr_country: str = None
    GC_addr_country_code: str = None
    GC_addr_house_number: str = None
    GC_addr_neighbourhood: str = None
    GC_addr_postcode: str = None
    GC_addr_road: str = None
    GC_addr_state: str = None
    GC_addr_suburb: str = None
    GC_boundingbox: str = None
    GC_latitude: float
    GC_longitude: float
    health_beauty: str = None
    heating_type: str = None
    kitchen: str = None
    location: str
    loudness: str = None
    main_url: str = None
    market: str = None
    model_name: str = None
    name: str
    number_of_floors: float = None
    offer_added: str = None
    offer_number: str = None
    offer_updated: str = None
    other: str = None
    parking: str = None
    price: float
    price_m2: float = None
    producer_name: str
    property_form: str = None
    ref_number: str = None
    rent_price: str = None
    rooms: float = None
    terrace: str = None
    terrece_size: str = None
    tracking_id: float
    umeblowane: str = None
    url: str = None
    widows_type: str = None
    windows: str = None
    world_direction: str = None
    year_of_building: float = None


class RequestBodyListIn(BaseModel):
    data: List[RequestBodyIn]


class RequestBodyOut(RequestBodyIn):
    prediction: float
    model_name: str = None


class RequestBodyListOut(BaseModel):
    data: List[RequestBodyOut]


class TrainMode(str, Enum):
    development = "DEVELOPMENT"
    docker = "DOCKER"
