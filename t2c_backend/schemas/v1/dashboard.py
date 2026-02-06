from pydantic import BaseModel, ConfigDict, Field


class DashboardResponse(BaseModel):
    asset_type: int = Field(..., alias="assetType")
    typeplate: int
    asset: int
    service: int
    shop: int
    instruction_manual: int = Field(..., alias="instructionManual")
    inspection: int
    time_recording: int = Field(..., alias="timeRecording")
    iot: int

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def convert(data) -> "DashboardResponse":
        return DashboardResponse(
            assetType=data.asset_type_count,
            typeplate=data.typeplate_count,
            asset=data.asset_count,
            service=data.service_count,
            shop=0,
            instructionManual=data.instruction_manual_count,
            inspection=0,
            timeRecording=0,
            iot=0,
        )
