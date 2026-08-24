"""
Maps each site location to a Department (for dashboard filtering) and a
Manager (for email notification routing). Note: manager is per-location,
not strictly per-department — a location can carry a department label but
still be routed to a different manager (e.g. Chemical Yard is labelled
Admin but is managed by Kamran, not Kaleem).

To edit the org chart, just update LOCATION_INFO and MANAGER_EMAILS below.
"""

# location name -> {"department": ..., "manager": ...}
LOCATION_INFO = {
    # --- Admin (Kaleem) ---
    "Admin Building": {"department": "Admin", "manager": "Kaleem"},
    "Admin Building Top Area": {"department": "Admin", "manager": "Kaleem"},
    "CTS Checkpost": {"department": "Admin", "manager": "Kaleem"},
    "CTS Main Gate": {"department": "Admin", "manager": "Kaleem"},
    "Canteen": {"department": "Admin", "manager": "Kaleem"},
    "Main Gate": {"department": "Admin", "manager": "Kaleem"},
    "Off-the-Job Location": {"department": "Admin", "manager": "Kaleem"},
    "Outdoor Boundary": {"department": "Admin", "manager": "Kaleem"},
    "Parking Area": {"department": "Admin", "manager": "Kaleem"},
    "Record Room": {"department": "Admin", "manager": "Kaleem"},
    "Security Control Room": {"department": "Admin", "manager": "Kaleem"},
    "Training Room": {"department": "Admin", "manager": "Kaleem"},
    "Chemical Yard": {"department": "Admin", "manager": "Kamran"},  # exception

    # --- Electrical (Faisal) ---
    "CTS Generator Room": {"department": "Electrical", "manager": "Faisal"},
    "CTS Transformer Room": {"department": "Electrical", "manager": "Faisal"},
    "E&I Yard": {"department": "Electrical", "manager": "Faisal"},
    "Generator Room": {"department": "Electrical", "manager": "Faisal"},
    "Jetty Switch Room": {"department": "Electrical", "manager": "Faisal"},
    "Local Switch Room": {"department": "Electrical", "manager": "Faisal"},
    "Solar Park": {"department": "Electrical", "manager": "Faisal"},
    "Substation 1": {"department": "Electrical", "manager": "Faisal"},
    "Substation 2": {"department": "Electrical", "manager": "Faisal"},
    "Substation 2 Extension": {"department": "Electrical", "manager": "Faisal"},
    "Substation 3": {"department": "Electrical", "manager": "Faisal"},
    "Substation 4": {"department": "Electrical", "manager": "Faisal"},
    "Substation 5": {"department": "Electrical", "manager": "Faisal"},
    "Substation 5 Extension": {"department": "Electrical", "manager": "Faisal"},
    "Substation 6": {"department": "Electrical", "manager": "Faisal"},

    # --- Ops / HSE (Kamran) ---
    "Fire Pump House Room": {"department": "Ops", "manager": "Kamran"},
    "Fire Station": {"department": "HSE", "manager": "Kamran"},
    "First Aid Room": {"department": "HSE", "manager": "Kamran"},
    "Hazardous Yard": {"department": "Ops", "manager": "Kamran"},
    "Hose Room": {"department": "Ops", "manager": "Kamran"},

    # --- Mechanical (Sajid) ---
    "CTS Workshop": {"department": "Mechanical", "manager": "Sajid"},
    "Cable Yard": {"department": "Mechanical", "manager": "Sajid"},
    "Maintenance BLD": {"department": "Mechanical", "manager": "Sajid"},
    "Pipe Yard": {"department": "Mechanical", "manager": "Sajid"},
    "Salvage Yard": {"department": "Mechanical", "manager": "Sajid"},
    "Scrap Yard": {"department": "Mechanical", "manager": "Sajid"},
    "Workshop": {"department": "Mechanical", "manager": "Sajid"},

    # --- Operations (Qasim) ---
    "Acetic Acid Pump House": {"department": "Operations", "manager": "Qasim"},
    "Acetic Acid Tank Farm Area T-1201": {"department": "Operations", "manager": "Qasim"},
    "Acetic Acid Tank Farm Area T-1202": {"department": "Operations", "manager": "Qasim"},
    "Acetic Acid Truck Loading Area": {"department": "Operations", "manager": "Qasim"},
    "Back Pressure Skid": {"department": "Operations", "manager": "Qasim"},
    "Central Control Room": {"department": "Operations", "manager": "Qasim"},
    "Diesel Tank Farm": {"department": "Operations", "manager": "Qasim"},
    "EDC Pump House": {"department": "Operations", "manager": "Qasim"},
    "EDC Tank Farm T-1301": {"department": "Operations", "manager": "Qasim"},
    "EDC Tank Farm T-1302": {"department": "Operations", "manager": "Qasim"},
    "EDC Truck Loading Area": {"department": "Operations", "manager": "Qasim"},
    "Ethylene Combustor Area": {"department": "Operations", "manager": "Qasim"},
    "Ethylene Culvert": {"department": "Operations", "manager": "Qasim"},
    "Ethylene Process Area": {"department": "Operations", "manager": "Qasim"},
    "Ethylene Tank Farm T-1501": {"department": "Operations", "manager": "Qasim"},
    "Ethylene Tank Farm T-1502": {"department": "Operations", "manager": "Qasim"},
    "Ethylene Utility Area": {"department": "Operations", "manager": "Qasim"},
    "FFBL Tank Farm Area": {"department": "Operations", "manager": "Qasim"},
    "General Weighbridge": {"department": "Operations", "manager": "Qasim"},
    "Jetty 1": {"department": "Operations", "manager": "Qasim"},
    "Jetty": {"department": "Operations", "manager": "Qasim"},
    "Jetty Breasting Dolphin 1": {"department": "Operations", "manager": "Qasim"},
    "Jetty Breasting Dolphin 2": {"department": "Operations", "manager": "Qasim"},
    "Jetty ESD Skid A": {"department": "Operations", "manager": "Qasim"},
    "Jetty ESD Skid B": {"department": "Operations", "manager": "Qasim"},
    "Jetty Equipment Room": {"department": "Operations", "manager": "Qasim"},
    "Jetty Head": {"department": "Operations", "manager": "Qasim"},
    "Jetty Instrumentation Skid": {"department": "Operations", "manager": "Qasim"},
    "Jetty Intersection": {"department": "Operations", "manager": "Qasim"},
    "Jetty Mooring Dolphin 1": {"department": "Operations", "manager": "Qasim"},
    "Jetty Mooring Dolphin 2": {"department": "Operations", "manager": "Qasim"},
    "Jetty Mooring Dolphin 3": {"department": "Operations", "manager": "Qasim"},
    "Jetty Mooring Dolphin 4": {"department": "Operations", "manager": "Qasim"},
    "Jetty Trestle": {"department": "Operations", "manager": "Qasim"},
    "Jetty Walkway North Side": {"department": "Operations", "manager": "Qasim"},
    "Jetty Walkway South Side": {"department": "Operations", "manager": "Qasim"},
    "Jetty Walkways": {"department": "Operations", "manager": "Qasim"},
    "Under Jetty": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201A": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201B": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201C": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201D": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201E": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201F": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201G": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201H": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V201J": {"department": "Operations", "manager": "Qasim"},
    "LPG Bullet Storage V202A": {"department": "Operations", "manager": "Qasim"},
    "LPG Pump House": {"department": "Operations", "manager": "Qasim"},
    "LPG Truck Loading Area Bay 1": {"department": "Operations", "manager": "Qasim"},
    "LPG Truck Loading Area Bay 2": {"department": "Operations", "manager": "Qasim"},
    "LPG Truck Loading Area Bay 3": {"department": "Operations", "manager": "Qasim"},
    "LPG Truck Loading Area Bay 4": {"department": "Operations", "manager": "Qasim"},
    "LPG Weighbridge": {"department": "Operations", "manager": "Qasim"},
    "Local Equipment Room": {"department": "Operations", "manager": "Qasim"},
    "MEG Common User Manifold": {"department": "Operations", "manager": "Qasim"},
    "MEG Pump House": {"department": "Operations", "manager": "Qasim"},
    "MEG Tank Farm": {"department": "Operations", "manager": "Qasim"},
    "MEG Truck Loading Area Bay 1": {"department": "Operations", "manager": "Qasim"},
    "Main Control Room": {"department": "Operations", "manager": "Qasim"},
    "Metering Skid": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 1": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 2": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 3": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 4": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 5": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 6": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 7": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 8": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 9": {"department": "Operations", "manager": "Qasim"},
    "Mooring Dolphin 10": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Nitrogen Area": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Pump Hot Water": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Pump House": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Tank Farm 1101": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Tank Farm 1102": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Tank Farm 1103": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Tank Farm 3101": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Truck Loading Area Bay 1": {"department": "Operations", "manager": "Qasim"},
    "Paraxylene Truck Loading Area Bay 2": {"department": "Operations", "manager": "Qasim"},
    "Utility Pump Area": {"department": "Operations", "manager": "Qasim"},
    "Utility Tank Area": {"department": "Operations", "manager": "Qasim"},
    "VCM LCR": {"department": "Operations", "manager": "Qasim"},
    "VCM Pump House": {"department": "Operations", "manager": "Qasim"},
    "VCM Tank Farm": {"department": "Operations", "manager": "Qasim"},
    "VCM Tank Farm V-101A": {"department": "Operations", "manager": "Qasim"},
    "VCM Tank Farm V-101B": {"department": "Operations", "manager": "Qasim"},
    "VCM Store": {"department": "Operations", "manager": "Qasim"},
    "Waste Water Handling Area": {"department": "Operations", "manager": "Qasim"},
    "Water Bath Heater": {"department": "Operations", "manager": "Qasim"},

    # --- Warehouse (Kaleem) ---
    "Admin Store": {"department": "Warehouse", "manager": "Kaleem"},
    "Warehouse": {"department": "Warehouse", "manager": "Kaleem"},
    "Warehouse A": {"department": "Warehouse", "manager": "Kaleem"},
    "Warehouse B (China Yard)": {"department": "Warehouse", "manager": "Kaleem"},
}

# manager name -> email address. TESTING: everyone routes to the same inbox
# for now (bolosafety@gmail.com — the Resend account's own address, since the
# sending domain isn't verified yet, so Resend only allows delivery there).
# Replace each value with the real manager email once the domain is verified.
MANAGER_EMAILS = {
    "Kaleem": "bolosafety@gmail.com",
    "Faisal": "bolosafety@gmail.com",
    "Kamran": "bolosafety@gmail.com",
    "Sajid": "bolosafety@gmail.com",
    "Qasim": "bolosafety@gmail.com",
}

ALL_DEPARTMENTS = ["Admin", "Electrical", "HSE", "Mechanical", "Ops", "Operations", "Warehouse"]


def get_location_info(location: str):
    """Returns {"department": ..., "manager": ..., "manager_email": ...} for a
    given location name, or None if the location isn't in the mapping
    (e.g. 'Not specified')."""
    info = LOCATION_INFO.get(location)
    if not info:
        return None
    manager_email = MANAGER_EMAILS.get(info["manager"])
    return {
        "department": info["department"],
        "manager": info["manager"],
        "manager_email": manager_email,
    }
