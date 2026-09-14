# ============================================================
# AGRITWIN AI - CROP CALENDAR ENGINE
# ============================================================

CROP_CALENDARS = {
    "WHEAT": {
        "sowing": "October - December",
        "vegetative": "December - January",
        "flowering": "February - March",
        "harvest": "March - April"
    },
    "RICE": {
        "sowing": "June - July",
        "vegetative": "July - August",
        "flowering": "August - September",
        "harvest": "September - November"
    },
    "MAIZE": {
        "sowing": "June - July",
        "vegetative": "July - August",
        "flowering": "August - September",
        "harvest": "September - October"
    },
    "CHICKPEA": {
        "sowing": "October - November",
        "vegetative": "November - January",
        "flowering": "January - February",
        "harvest": "February - March"
    },
    "PIGEONPEA": {
        "sowing": "June - July",
        "vegetative": "July - September",
        "flowering": "September - October",
        "harvest": "November - December"
    },
    "GROUNDNUT": {
        "sowing": "June - July",
        "vegetative": "July - August",
        "flowering": "August - September",
        "harvest": "September - October"
    },
    "COTTON": {
        "sowing": "April - June",
        "vegetative": "June - August",
        "flowering": "August - October",
        "harvest": "October - December"
    },
    "BARLEY": {
        "sowing": "October - November",
        "vegetative": "November - January",
        "flowering": "February",
        "harvest": "March - April"
    },
    "SOYABEAN": {
        "sowing": "June - July",
        "vegetative": "July - August",
        "flowering": "August - September",
        "harvest": "September - October"
    }
}


def get_crop_calendar(crop: str) -> dict:

    crop = crop.upper().strip()

    calendar = CROP_CALENDARS.get(
        crop
    )

    if calendar is None:

        calendar = {
            "sowing": "Not available",
            "vegetative": "Not available",
            "flowering": "Not available",
            "harvest": "Not available"
        }

    return {
        "crop": crop,
        "calendar": calendar
    }