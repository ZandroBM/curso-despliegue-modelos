from pydantic import BaseModel,Field
from datetime import date
from typing import Literal


#Clase para definir la estructura de entrada que require la predicción
class ClienteInput(BaseModel):
    antiguedad_meses: int = Field(...,description="meses que lleva como cliente"),
    gasto_mensual: float = Field(...,description="cuánto paga por mes "),
    visitas_ultimo_mes: int = Field(...,description="veces que usó el servicio en el último mes"),
    dias_desde_ultima_visita: int = Field(...,description="días desde la última vez que lo usó"),
    tickets_soporte:  int = Field(...,description="reclamos abiertos en el último mes "),
    descuento_activo: Literal[0,1] = Field(...,description="si hoy tiene un descuento aplicado"),
    plan:  Literal['basico','estandar','premium'] = Field(...,description="basico, estandar o premium"),
    metodo_pago:  Literal['tarjeta','transferencia','efectivo'] = Field(...,description="tarjeta, transferencia o efectivo")

