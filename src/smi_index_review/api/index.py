import json
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import ValidationError

from smi_index_review.api.config import Settings, get_settings
from smi_index_review.api.domain import (
    SMI,
    ConstituentsResponse,
    ResultsModel,
    StockDetails,
    Weights,
)

app = FastAPI(
    title=get_settings().app_name,
    description="API Routes for SMI Index Review",
    version=get_settings().api_version,
)


def load_dataset(settings: Annotated[Settings, Depends(get_settings)]) -> ResultsModel:
    data_path = settings.output_path
    if not data_path.is_file():
        raise HTTPException(
            status_code=404, detail=f"Data File path not found: {data_path}"
        )
    with open(data_path, encoding="utf-8") as f:
        raw_data = json.load(f)
        try:
            data = ResultsModel.model_validate(raw_data)
        except ValidationError as e:
            message = "; ".join(
                f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )
            raise HTTPException(
                status_code=400,
                detail=f"Data file is not alligned with schema -> ({message})",
            )
    return data


@app.get("/joiners", tags=["SMI Review"])
def get_joiners(
    data: Annotated[ResultsModel, Depends(load_dataset)],
) -> list[StockDetails]:
    return data.joiners


@app.get("/leavers", tags=["SMI Review"])
def get_leavers(
    data: Annotated[ResultsModel, Depends(load_dataset)],
) -> list[StockDetails]:
    return data.leavers


@app.get("/smi/data", tags=["SMI Review"])
def smi_review(data: Annotated[ResultsModel, Depends(load_dataset)]) -> list[SMI]:
    return data.smi_list


@app.get("/constituents", tags=["SMI Review"])
def get_constituents(
    data: Annotated[ResultsModel, Depends(load_dataset)],
) -> list[ConstituentsResponse]:
    return [
        ConstituentsResponse(
            id=member.id,
            FFMCAP_Rank=member.FFMCAP_Rank,
            review_status=member.review_status,
            weights=Weights(
                initial_weight=member.initial_weight, capped_weight=member.capped_weight
            ),
        )
        for member in data.smi_list
    ]


@app.get("/dataset/schema", tags=["Dataset Schema"])
def get_dataset_schema() -> dict:
    return ResultsModel.model_json_schema()
