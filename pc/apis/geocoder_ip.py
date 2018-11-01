import geocoder

"""
https://github.com/DenisCarriere/geocoder#pypi-install
"""
def get_robot_location():
    g = geocoder.ip('me')
    return g.latlng
