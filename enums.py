from enum import Enum
import enum

class VehicleStatus(str, enum.Enum):
    INI = "Inicio"
    DAE = "Vehículo dañado antes de la entrada"
    ERC = "En reparación por parte del cliente"
    SL  = "Vehículo sólo lavado (sin terminación ni control de calidad)"
    LYT = "Vehículo con lavado y terminación"
    DDL = "Vehículo dañado durante el lavado"
    ET  = "En terminación"
    DDT = "Vehículo dañado durante la terminación"
    ECC = "En control de calidad"
    APR = "Aprobado"