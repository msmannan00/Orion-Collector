from pydantic import BaseModel
from typing import List, Optional

class entity_model(BaseModel):
    m_email_addresses: List[str] = []
    m_phone_numbers: List[str] = []
    m_states: List[str] = []
    m_location_info: List[str] = []
    m_social_media_profiles: List[str] = []
    m_social_channel: List[str] = []
    m_name: str = ""
    m_industry: Optional[str] = None
    m_company_name: Optional[str] = None
    m_country_name: Optional[str] = None
    m_ip: Optional[List[str]] = None
    m_team: Optional[str] = None
    m_attacker: List[str] = []

    m_au_abn: List[str] = []
    m_au_acn: List[str] = []
    m_au_medicare: List[str] = []
    m_au_tfn: List[str] = []
    m_credit_cards: List[str] = []
    m_crypto_addresses: List[str] = []
    m_crypto_btc_addresses: List[str] = []
    m_iban_codes: List[str] = []
    m_in_aadhaar_numbers: List[str] = []
    m_in_pan_numbers: List[str] = []
    m_in_passport_numbers: List[str] = []
    m_in_vehicle_registrations: List[str] = []
    m_in_voter_ids: List[str] = []
    m_medical_licenses: List[str] = []
    m_nrp_numbers: List[str] = []
    m_persons: List[str] = []
    m_sg_nric_fin_numbers: List[str] = []
    m_uk_nhs_numbers: List[str] = []
    m_uk_nino_numbers: List[str] = []
    m_urls: List[str] = []
    m_us_bank_numbers: List[str] = []
    m_us_driver_licenses: List[str] = []
    m_us_itin_numbers: List[str] = []
    m_us_passport_numbers: List[str] = []
    m_us_ssn_numbers: List[str] = []

