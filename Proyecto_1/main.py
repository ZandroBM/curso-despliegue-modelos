from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

NOMBRE_BUNDLE = "modelo_bundle_e_cardiaca.pkl"
estado_servicio = {"bundle" : None}

@asynccontextmanager
async def lifespan(app:FastAPI):
    estado_servicio["bundle"] = joblib.load(NOMBRE_BUNDLE)
    print("Bundle cargado correctamente")
    yield 
    estado_servicio["bundle"] = None 

app = FastAPI(
    title = "API de Prediccion de Enfermedad Cardíaca",
    description = "Recibe datos Clinicos de un paciente y predice riesgo de cardiopatia coronaria (chd)",
    version = "1.0.0",
    lifespan = lifespan
)


class PacienteInput(BaseModel):
    sbp: int = Field(...,description="Presion arterial sistólica"),
    Tabaco: float = Field(...,description="Tabaco acomulado (kg)"),
    ldl: float = Field(...,description="Colesterol LDL"),
    Adiposidad: float = Field(...,description="Adiposidad"),
    Familia: Literal['Presente','Ausente'] = Field(...,description="Antecedentes Familiares de enfermedades Cardíacas"),
    Tipo: int = Field(...,description="Comportamiento tipo-A"),
    Obesidad: float = Field(...,description="Obesidad"),
    Alcohol: float = Field(...,description="Consumo actual de alcohol"),
    Edad: int = Field(...,description="Edad")

class PacienteOutput(BaseModel):
    chd_predicho: int
    probabilidad: float
    riesgo: str


@app.get("/")
def estado():
    return{
        "servicio": "API de predicción cardíaca",
        "modelo_cargado": estado_servicio["bundle"] is not None
}   

#predecir
@app.post("/predecir",response_model = PacienteOutput)
def predecir(paciente: PacienteInput):
    #Validar el modelo
    bundle = estado_servicio["bundle"]
    if bundle is None:
        raise HTTPException(status_code=503,detail="El modelo aun no esta cargado")

    fila = paciente.model_dump()
    fila["Familia"] = bundle["mapeo_familia"][fila["Familia"]]
    X_nuevo = pd.DataFrame([fila])[bundle["columnas"]]
    prediccion = bundle["pipeline"].predict(X_nuevo)[0]
    probabilidad = bundle["pipeline"].predict_proba(X_nuevo)[0,1]

    #devolver resultados
    return PacienteOutput(
        chd_predicho=prediccion,
        probabilidad=round(probabilidad,4),
        riesgo= "Alto" if prediccion == 1 else "Bajo"
    )