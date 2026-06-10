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
    def convert(
        asset_type_count,
        typeplate_count,
        asset_count,
        service_count,
        instruction_manual_count,
        inspection,
        shop,
    ) -> "DashboardResponse":
        return DashboardResponse(
            assetType=asset_type_count,
            typeplate=typeplate_count,
            asset=asset_count,
            service=service_count,
            shop=shop,
            instructionManual=instruction_manual_count,
            inspection=inspection,
            timeRecording=0,
            iot=0,
        )
