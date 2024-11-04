# services/exceptions.py

class VehicleNotFound(Exception):
    pass

class VehicleModelNotFound(Exception):
    pass

class ColorNotFound(Exception):
    pass

class VINAlreadyExists(Exception):
    pass

class InvalidVIN(Exception):
    pass

class InitialStateNotFound(Exception):
    pass
