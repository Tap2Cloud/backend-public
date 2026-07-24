from sqlalchemy import func, select

from t2c_backend.models import (
    Asset,
    AssetType,
    AssetTypeDocument,
    Audit,
    AuditTask,
    Location,
    Typeplate,
)
from t2c_backend.models.service import Service
from t2c_backend.utils.enums import TaskType


class DashboardService:
    _model = None

    def __init__(self, app, session) -> None:
        self.app = app
        self.session = session

    async def get_dashboard_statistics(self, organization_id: int):
        asset_count_result = await self.session.execute(
            select(func.count(Asset.id))
            .outerjoin(Location, Location.id == Asset.location_id)
            .where(Location.organization_id == organization_id)
        )
        asset_count = asset_count_result.scalar() or 0

        asset_type_count_result = await self.session.execute(
            select(func.count(AssetType.id))
            .outerjoin(Location, Location.id == AssetType.location_id)
            .where(Location.organization_id == organization_id)
        )
        asset_type_count = asset_type_count_result.scalar() or 0

        typeplate_count_result = await self.session.execute(
            select(func.count(Typeplate.id))
            .outerjoin(AssetType, AssetType.id == Typeplate.asset_type_id)
            .outerjoin(Location, Location.id == AssetType.location_id)
            .where(Location.organization_id == organization_id)
        )
        typeplate_count = typeplate_count_result.scalar() or 0

        instruction_manual_count_result = await self.session.execute(
            select(func.count(AssetTypeDocument.id))
            .outerjoin(Location, Location.id == AssetTypeDocument.location_id)
            .where(Location.organization_id == organization_id)
        )
        instruction_manual_count = instruction_manual_count_result.scalar() or 0

        service_count_result = await self.session.execute(
            select(func.count(Service.id))
            .outerjoin(Asset, Asset.id == Service.asset_id)
            .outerjoin(Location, Location.id == Asset.location_id)
            .where(Location.organization_id == organization_id)
        )
        service_count = service_count_result.scalar() or 0

        audit_count_result = await self.session.execute(
            select(func.count(AuditTask.id))
            .outerjoin(Audit, Audit.id == AuditTask.audit_id)
            .outerjoin(Asset, Asset.id == Audit.asset_id)
            .outerjoin(Location, Location.id == Asset.location_id)
            .where(
                Location.organization_id == organization_id,
                AuditTask.task_type == TaskType.inspection,
            )
        )
        audit_count = audit_count_result.scalar() or 0

        return (
            asset_count,
            asset_type_count,
            typeplate_count,
            instruction_manual_count,
            service_count,
            audit_count,
        )


def setup(app, session, *args, **kwargs):
    return app.add_service(DashboardService(app, session), session.info["session_id"])
