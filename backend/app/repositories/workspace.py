from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.entities import AuditLog, ContentJob, Product, ReviewTask


class WorkspaceRepository:
    def __init__(self, db: Session, tenant_id: int):
        self.db, self.tenant_id = db, tenant_id

    def products(self, status: str):
        return self.db.scalars(select(Product).where(Product.tenant_id == self.tenant_id, Product.status == status).order_by(Product.id.desc())).all()

    def pending_task(self, product_id: int):
        return self.db.scalar(select(ReviewTask).where(ReviewTask.tenant_id == self.tenant_id, ReviewTask.product_id == product_id, ReviewTask.status == 'PENDING'))

    def claim_task(self, task_id: int, comment: str, status: str):
        task = self.db.scalar(select(ReviewTask).where(ReviewTask.id == task_id, ReviewTask.tenant_id == self.tenant_id))
        if not task:
            return None
        changed = self.db.execute(update(ReviewTask).where(ReviewTask.id == task_id, ReviewTask.tenant_id == self.tenant_id, ReviewTask.status == 'PENDING').values(status=status, comment=comment)).rowcount
        return task if changed == 1 else None

    def transition_product(self, product_id: int, expected: str, target: str):
        return self.db.execute(update(Product).where(Product.id == product_id, Product.tenant_id == self.tenant_id, Product.status == expected).values(status=target, version=Product.version + 1)).rowcount == 1

    def add(self, obj):
        self.db.add(obj)

    def jobs(self):
        return self.db.execute(select(ContentJob, Product.title).join(Product, Product.id == ContentJob.product_id).where(ContentJob.tenant_id == self.tenant_id, Product.tenant_id == self.tenant_id).order_by(ContentJob.id.desc())).all()

    def logs(self):
        return self.db.scalars(select(AuditLog).where(AuditLog.tenant_id == self.tenant_id).order_by(AuditLog.id.desc()).limit(100)).all()
