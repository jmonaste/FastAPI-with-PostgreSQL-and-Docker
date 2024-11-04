# services/exceptions.py
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


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





class StateNotFoundException(Exception):
    pass

class StateCommentsNotFoundException(Exception):
    pass