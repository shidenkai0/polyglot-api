from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.tutor.models import Tutor
from app.tutor.schemas import (
    TutorCreate,
    TutorRead,
    TutorUpdate,
    public_to_internal_model_name,
)
from app.user.auth import ActiveVerifiedUser, SuperUser

router = APIRouter(
    responses={404: {"description": "Not found"}},
    tags=["tutors"],
)


TUTOR_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor not found")


@router.post("/tutor")
async def create_tutor(tutor_create: TutorCreate, user: SuperUser) -> TutorRead:
    """
    Create a new tutor.
    """
    tutor = await Tutor.create(
        name=tutor_create.name,
        language=tutor_create.language,
        avatar_url=tutor_create.avatar_url,
        visible=tutor_create.visible,
        model=public_to_internal_model_name(tutor_create.model),
    )

    return TutorRead.from_tutor(tutor)


@router.get("/tutors")
async def get_tutors(user: ActiveVerifiedUser) -> List[TutorRead]:
    """
    Get all tutors.
    """
    if user.is_superuser:
        tutors = await Tutor.get_all()
    elif user:
        tutors = await Tutor.get_visible()

    return [TutorRead.from_tutor(tutor) for tutor in tutors]


@router.get("/tutor/{tutor_id}")
async def get_tutor(tutor_id: UUID, user: SuperUser) -> TutorRead:
    """
    Get a tutor by ID.
    """
    tutor = await Tutor.get(tutor_id)
    if tutor is None:
        raise TUTOR_NOT_FOUND

    return TutorRead.from_tutor(tutor)


@router.put("/tutor/{tutor_id}", responses={status.HTTP_404_NOT_FOUND: {"description": "Tutor not found"}})
async def update_tutor(tutor_id: UUID, tutor_update: TutorUpdate, user: SuperUser) -> TutorRead:
    """
    Update a tutor by ID.
    """
    tutor = await Tutor.get(tutor_id)
    if tutor is None:
        raise TUTOR_NOT_FOUND

    internal_model = public_to_internal_model_name(tutor_update.model) if tutor_update.model else None

    await tutor.update(
        name=tutor_update.name,
        avatar_url=tutor_update.avatar_url,
        language=tutor_update.language,
        visible=tutor_update.visible,
        model=internal_model,
    )

    return TutorRead.from_tutor(tutor)


@router.delete("/tutor/{tutor_id}", responses={status.HTTP_404_NOT_FOUND: {"description": "Tutor not found"}})
async def delete_tutor(tutor_id: UUID, user: SuperUser) -> Response:
    """
    Delete a tutor by ID.
    """
    tutor = await Tutor.get(tutor_id)
    if tutor is None:
        raise TUTOR_NOT_FOUND
    await Tutor.delete(tutor_id)

    return Response(status_code=204)
