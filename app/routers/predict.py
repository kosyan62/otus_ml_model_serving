import logging

from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.ml import predict
from app.models import User
from app.schemas import PredictRequest, PredictResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ml"])


@router.post("/predict", response_model=PredictResponse)
def predict_diabetes(
    body: PredictRequest,
    current_user: User = Depends(get_current_user),
) -> PredictResponse:
    logger.info(
        "predict request | user=%s pregnancies=%d glucose=%d bmi=%.1f age=%d",
        current_user.username,
        body.Pregnancies,
        body.Glucose,
        body.BMI,
        body.Age,
    )
    result = predict(body.Pregnancies, body.Glucose, body.BMI, body.Age)
    logger.info("predict response | user=%s prediction=%d", current_user.username, result)
    return PredictResponse(prediction=result)
