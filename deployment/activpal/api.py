from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

from inference import predict_file

app = FastAPI(
    title="WEALTH activPAL Prediction API",
    description="Physical Behaviour and Energy Expenditure prediction from activPAL data",
    version="1.0.0",
)

INPUT_DIR = Path("/app/input")
INPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    input_file = INPUT_DIR / file.filename

    with input_file.open("wb") as buffer:
        buffer.write(await file.read())

    output_file = predict_file(input_file)

    return FileResponse(
        path=output_file,
        media_type="text/csv",
        filename=output_file.name,
    )