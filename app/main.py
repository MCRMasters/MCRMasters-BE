from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MCRMasters-BE",
    description="A FastAPI backend application for MCRMasters",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
