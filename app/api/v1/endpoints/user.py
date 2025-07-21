from fastapi import APIRouter


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", summary="Get current user", response_model=dict)
def get_me():
    return {"username": "sodipto", "email": "johndoe@example.com"}
