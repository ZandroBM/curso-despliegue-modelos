from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from Tarea1.esquema import ClienteInput
 

NOMBRE_BUNDLE = "Tarea1/modelo_churn.joblib"
estado_servicio = {"bundle" : None}

@asynccontextmanager
async def lifespan(app:FastAPI):
    estado_servicio["bundle"] = joblib.load(NOMBRE_BUNDLE)
    print("Bundle cargado correctamente")
    yield 
    estado_servicio["bundle"] = None 

app = FastAPI(
    title = "API de Servicio de Prónostico de Deserción",
    description = "Pronóstico de clientes que podrían abandonar el servicio",
    version = "1.0.0",
    lifespan = lifespan
)


@app.get("/")
def estado():
    return {
        "servicio": "API de Servicio de Prónostico de Deserción",
        "modelo_cargado": estado_servicio["bundle"] is not None
    }

#predecir
@app.post("/predecir")
def predecir(cli: ClienteInput):
    #Validar el modelo
    bundle = estado_servicio["bundle"]
    if bundle is None:
        raise HTTPException(status_code=503,detail="El modelo aun no esta cargado")

    #Realizar la predicción 
    fila = cli.model_dump()
    X_nuevo = pd.DataFrame([fila])[bundle["columnas"]]
    probabili = bundle["pipeline"].predict_proba(X_nuevo)[0,1]

    #definir el umbral
    umbral = 0.5

    #devolver resultados
    return {
        "probabilidad":round(probabili,4),
        "prediccion": "CANCELA" if probabili >= umbral  else "sigue activo",
        "riesgo": "alto" if probabili >= umbral else "medio" if probabili >= umbral * 0.70 else "bajo",
        "umbral": umbral
    }
   
