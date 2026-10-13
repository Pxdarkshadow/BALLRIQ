from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import audio, matches, nlp, ir, rag, evaluation, bda

app = FastAPI(title="BALLRIQ", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches.router)
app.include_router(nlp.router)
app.include_router(ir.router)
app.include_router(rag.router)
app.include_router(evaluation.router)
app.include_router(bda.router)
app.include_router(audio.router)


@app.get("/")
async def root():
    return {"message": "BALLRIQ API", "docs": "/docs"}
