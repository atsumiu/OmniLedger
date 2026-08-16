import os
import re
from urllib.parse import quote

import requests
from dotenv import load_dotenv



load_dotenv()

API_KEY = os.getenv("PROPRADAR_API_KEY")

BASE_URL = "https://api.propradar.com.au/v1"



def _headers():
    """
    Creates the headers required for PropRadar API requests.
    """

    if not API_KEY:
        raise ValueError(
            "PROPRADAR_API_KEY is missing from your .env file."
        )

    return {
        "X-API-Key": API_KEY,
        "Accept": "application/json"
    }


def _get(endpoint, params=None):
    """
    Sends a GET request to the PropRadar API.
    """

    response = requests.get(
        f"{BASE_URL}{endpoint}",
        headers=_headers(),
        params=params,
        timeout=15
    )

    response.raise_for_status()

    return response.json()



def test_connection():
    """
    Tests whether the PropRadar API connection works.
    """

    return _get("/health")


def get_usage(days=30):
    """
    Returns PropRadar API usage information.
    """

    return _get(
        "/usage",
        {
            "days": days
        }
    )



def search_property(address, postcode):
    """
    Searches for a property using its address and postcode.

    PropRadar requires a postcode for property address searches.
    """

    if not address:
        raise ValueError(
            "A property address is required."
        )

    if not postcode:
        raise ValueError(
            "A postcode is required for PropRadar property search."
        )

    return _get(
        "/properties/search",
        {
            "address": address,
            "postcode": postcode
        }
    )


def get_property(property_id):
    """
    Returns full information about a PropRadar property.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    return _get(
        f"/properties/{property_id}"
    )


def get_property_history(property_id):
    """
    Returns the event history of a property.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    return _get(
        f"/properties/{property_id}/history"
    )


def get_sold_summary(property_id):
    """
    Returns the most recent sold information for a property.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    return _get(
        f"/properties/{property_id}/sold_summary"
    )


def get_psp_with_confidence(property_id):
    """
    Returns the potential sell price and confidence range.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    return _get(
        f"/properties/{property_id}/psp_with_confidence"
    )


def get_similar_properties(property_id):
    """
    Returns similar active properties.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    return _get(
        f"/properties/{property_id}/similar"
    )


def get_nearby_properties(
    property_id,
    radius_m=1000,
    property_type=None,
    beds=None,
    limit=20
):
    """
    Returns active properties near another property.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    params = {
        "radius_m": radius_m,
        "limit": limit
    }

    if property_type:
        params["property_type"] = property_type

    if beds is not None:
        params["beds"] = beds

    return _get(
        f"/properties/{property_id}/nearby",
        params
    )



def get_suburb_stats(
    state,
    suburb,
    postcode=None
):
    """
    Returns statistics for a suburb.

    Postcode is OPTIONAL.

    If no postcode is supplied, PropRadar chooses the
    best-quality suburb record.
    """

    if not state:
        raise ValueError(
            "State is required."
        )

    if not suburb:
        raise ValueError(
            "Suburb is required."
        )

    params = {}

    if postcode:
        params["postcode"] = postcode

    encoded_suburb = quote(
        str(suburb).strip(),
        safe=""
    )

    return _get(
        f"/suburbs/{state.upper()}/{encoded_suburb}",
        params
    )


def get_recent_sales(
    state,
    suburb,
    months=12,
    property_type=None,
    min_beds=None,
    max_beds=None,
    min_price=None,
    max_price=None,
    limit=20
):
    """
    Returns recently sold properties in a suburb.
    """

    if not state:
        raise ValueError(
            "State is required."
        )

    if not suburb:
        raise ValueError(
            "Suburb is required."
        )

    params = {
        "months": months,
        "limit": limit
    }

    if property_type:
        params["property_type"] = property_type

    if min_beds is not None:
        params["min_beds"] = min_beds

    if max_beds is not None:
        params["max_beds"] = max_beds

    if min_price is not None:
        params["min_price"] = min_price

    if max_price is not None:
        params["max_price"] = max_price

    encoded_suburb = quote(
        str(suburb).strip(),
        safe=""
    )

    return _get(
        f"/suburbs/{state.upper()}/{encoded_suburb}/sold",
        params
    )


def get_suburb_listings(
    state,
    suburb,
    property_type=None,
    min_beds=None,
    max_beds=None,
    min_price=None,
    max_price=None,
    limit=20
):
    """
    Returns current properties listed for sale in a suburb.
    """

    if not state:
        raise ValueError(
            "State is required."
        )

    if not suburb:
        raise ValueError(
            "Suburb is required."
        )

    params = {
        "limit": limit
    }

    if property_type:
        params["property_type"] = property_type

    if min_beds is not None:
        params["min_beds"] = min_beds

    if max_beds is not None:
        params["max_beds"] = max_beds

    if min_price is not None:
        params["min_price"] = min_price

    if max_price is not None:
        params["max_price"] = max_price

    encoded_suburb = quote(
        str(suburb).strip(),
        safe=""
    )

    return _get(
        f"/suburbs/{state.upper()}/{encoded_suburb}/listings",
        params
    )


def get_suburb_coverage(
    state=None,
    has=None,
    limit=200,
    offset=0
):
    """
    Returns suburbs covered by PropRadar.

    Useful for checking whether a suburb exists before
    requesting detailed information.
    """

    params = {
        "limit": limit,
        "offset": offset
    }

    if state:
        params["state"] = state.upper()

    if has:
        if isinstance(has, list):
            params["has"] = ",".join(has)
        else:
            params["has"] = has

    return _get(
        "/suburbs",
        params
    )


def get_suburb_rankings(
    state,
    metric=None,
    property_type=None,
    min_median_price=None,
    max_median_price=None,
    top=20
):
    """
    Returns ranked suburbs.

    This endpoint requires the appropriate PropRadar plan.
    """

    if not state:
        raise ValueError(
            "State is required."
        )

    params = {
        "state": state.upper(),
        "top": top
    }

    if metric:
        params["metric"] = metric

    if property_type:
        params["property_type"] = property_type

    if min_median_price is not None:
        params["min_median_price"] = min_median_price

    if max_median_price is not None:
        params["max_median_price"] = max_median_price

    return _get(
        "/suburbs/rankings",
        params
    )


def get_suburb_price_history(
    state,
    suburb,
    years=10
):
    """
    Returns historical median property prices for a suburb.
    """

    if not state:
        raise ValueError(
            "State is required."
        )

    if not suburb:
        raise ValueError(
            "Suburb is required."
        )

    encoded_suburb = quote(
        str(suburb).strip(),
        safe=""
    )

    return _get(
        f"/suburbs/{state.upper()}/{encoded_suburb}/price_history",
        {
            "years": years
        }
    )


def get_market_cycle(
    state,
    suburb
):
    """
    Returns market-cycle information for a suburb.
    """

    if not state:
        raise ValueError(
            "State is required."
        )

    if not suburb:
        raise ValueError(
            "Suburb is required."
        )

    encoded_suburb = quote(
        str(suburb).strip(),
        safe=""
    )

    return _get(
        f"/suburbs/{state.upper()}/{encoded_suburb}/market_cycle"
    )



def get_comparables_by_property(
    property_id,
    radius_m=1000,
    months=12,
    property_type=None,
    beds=None,
    limit=20
):
    """
    Finds recently sold comparable properties around
    an existing PropRadar property.
    """

    if not property_id:
        raise ValueError(
            "A PropRadar property ID is required."
        )

    params = {
        "property_id": property_id,
        "radius_m": radius_m,
        "months": months,
        "limit": limit
    }

    if property_type:
        params["property_type"] = property_type

    if beds is not None:
        params["beds"] = beds

    return _get(
        "/comparables",
        params
    )


def get_comparables_by_location(
    lat,
    lng,
    radius_m=1000,
    months=12,
    property_type=None,
    beds=None,
    limit=20
):
    """
    Finds recently sold comparable properties around
    a latitude/longitude location.

    This is intended for PropRadar plans that support
    latitude/longitude comparables.
    """

    if lat is None or lng is None:
        raise ValueError(
            "Latitude and longitude are required."
        )

    params = {
        "lat": lat,
        "lng": lng,
        "radius_m": radius_m,
        "months": months,
        "limit": limit
    }

    if property_type:
        params["property_type"] = property_type

    if beds is not None:
        params["beds"] = beds

    return _get(
        "/comparables",
        params
    )




def extract_postcode(address):
    """
    Attempts to find a four-digit Australian postcode
    inside an address.

    Returns:
        postcode string
        or None if no postcode exists.
    """

    if not address:
        return None

    match = re.search(
        r"\b(\d{4})\b",
        str(address)
    )

    if match:
        return match.group(1)

    return None


def search_omniledger_property(property_data):
    """
    Attempts to match an OmniLedger property with
    a PropRadar property.

    IMPORTANT:
    OmniLedger properties do not always contain postcodes.

    If there is no postcode, this function simply skips
    the PropRadar property lookup instead of crashing.
    """

    if not property_data:
        print(
            "PROPRADAR SKIPPED: "
            "No property data."
        )

        return None

    address = property_data.get(
        "propertyAddress"
    )

    if not address:
        print(
            "PROPRADAR SKIPPED: "
            "No property address."
        )

        return None

    postcode = extract_postcode(
        address
    )

    if not postcode:
        print(
            f"PROPRADAR SKIPPED: "
            f"No postcode found for '{address}'."
        )

        return None

    try:
        return search_property(
            address,
            postcode
        )

    except requests.exceptions.RequestException as error:
        print(
            f"PROPRADAR ERROR: "
            f"Could not search '{address}': {error}"
        )

        return None