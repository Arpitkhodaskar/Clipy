from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_security():
    return {"message": "Security endpoint - Coming soon"}