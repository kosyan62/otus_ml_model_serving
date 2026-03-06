import logging

from fastapi import APIRouter, Request, Security

from app.auth import doc_bearer, require_role
from app.ml import predict
from app.schemas import PredictRequest, PredictResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ml"], dependencies=[Security(doc_bearer), require_role("user")])


@router.post("/predict", response_model=PredictResponse)
def predict_diabetes(body: PredictRequest, request: Request) -> PredictResponse:
    username = getattr(request.user, "display_name", "unknown")
    logger.info(
        "predict request | user=%s pregnancies=%d glucose=%d bmi=%.1f age=%d",
        username, body.Pregnancies, body.Glucose, body.BMI, body.Age,
    )
    prediction = predict(body.Pregnancies, body.Glucose, body.BMI, body.Age)
    logger.info("predict response | user=%s prediction=%d", username, prediction)
    return PredictResponse(prediction=prediction)
