from enum import Enum

VALID_NETWORK_TYPES = [
    "clearnet",
    "i2p",
    "onion",
    "invalid"
]

class ENTITY_KEYS:
    M_EMAIL_ADDRESSES = "m_email_addresses"
    M_PHONE_NUMBERS = "m_phone_numbers"


VALID_CONTENT_TYPES = [
    "general",
    "forums",
    "tracking",
    "news",
    "stolen",
    "drugs",
    "hacking",
    "marketplaces",
    "cryptocurrency",
    "leaks",
    "adult",
    "carding",
    "scams",
    "ransomware",
    "databases",
    "money_laundering",
    "counterfeit",
    "malware",
    "botnets",
    "exploits",
    "spam",
    "chemicals",
    "weapons",
    "human_trafficking",
    "csam",
    "doxing",
    "extortion",
    "espionage",
    "propaganda",
    "terrorism",
    "government_leaks",
    "c2_panels",
    "ddos",
    "apt"
]
