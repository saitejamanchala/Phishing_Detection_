import re
import urllib.parse
import ipaddress

def extract_url_features(url: str) -> dict:
    """
    Extracts structural indicators from a URL string and maps them 
    to a dictionary matching the dataset's features.
    """
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    
    # 1. UsingIP
    try:
        ipaddress.ip_address(hostname)
        using_ip = 1
    except ValueError:
        using_ip = -1

    # 2. LongURL
    if len(url) < 54:
        long_url = -1
    elif 54 <= len(url) <= 75:
        long_url = 0
    else:
        long_url = 1

    # 3. ShortURL
    shorteners = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|is\.gd|cli\.gs"
    short_url = 1 if re.search(shorteners, url) else -1

    # 4. Symbol@
    symbol_at = 1 if "@" in url else -1

    # 5. Redirecting//
    redirecting_slash = 1 if path.rfind("//") > 0 else -1

    # 6. PrefixSuffix-
    prefix_suffix = 1 if "-" in hostname else -1

    # 7. SubDomains
    dots = hostname.count(".")
    if dots <= 2:
        subdomains = -1
    elif dots == 3:
        subdomains = 0
    else:
        subdomains = 1

    # 8. HTTPS
    https = -1 if parsed.scheme == "https" else 1

    # Default heuristic mappings for secondary web/HTML features
    # (Values fall back to standard non-phishing indicators when non-fetchable)
    features = {
        "HTTPS": https,
        "AnchorURL": -1,
        "WebsiteTraffic": 0,
        "SubDomains": subdomains,
        "RequestURL": -1,
        "LinksInScriptTags": -1,
        "DomainRegLen": -1,
        "AgeofDomain": -1,
        "PageRank": -1,
        "UsingIP": using_ip,
        "DNSRecording": -1,
        "LinksPointingToPage": 1,
        "Index": 1,
        "LongURL": long_url,
        "ShortURL": short_url,
        "Symbol@": symbol_at,
        "Redirecting//": redirecting_slash,
        "PrefixSuffix-": prefix_suffix,
        "Favicon": -1,
        "NonStdPort": -1 if parsed.port in [None, 80, 443] else 1,
        "HTTPSDomainURL": 1 if "https" in hostname else -1,
        "ServerFormHandler": -1,
        "InfoEmail": 1 if "mailto:" in url else -1,
        "AbnormalURL": -1,
        "WebsiteForwarding": 0,
        "StatusBarCust": -1
    }

    return features