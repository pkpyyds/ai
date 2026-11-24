from sqlalchemy.orm import Session
from app.models.entities import AuditLog, ContentJob, Product, ReviewTask
from app.repositories.workspace import WorkspaceRepository


class Conflict(Exception):
    pass


class WorkspaceService:
    """Demo-only workflow. Never substitutes for authentication or frozen business policy."""
    def __init__(self, db: Session, tenant_id: int = 1):
        self.db = db
        self.tenant_id = tenant_id
        self.repo = WorkspaceRepository(db, tenant_id)

    def list_products(self, status):
        result = []
        for p in self.repo.products(status):
            task = self.repo.pending_task(p.id)
            result.append({'id': p.id, 'title': p.title, 'category': p.category, 'platform_product_id': p.platform_product_id, 'status': p.status, 'task_id': task.id if task else None})
        return result

    def decide_review(self, task_id: int, approved: bool, comment: str):
        if not approved and not comment.strip():
            raise ValueError('驳回必须填写意见')
        try:
            task = self.repo.claim_task(task_id, comment, 'APPROVED' if approved else 'REJECTED')
            if task is None:
                raise Conflict('核验任务不存在、已处理或状态冲突')
            expected = {'FIRST': 'FIRST_REVIEW_PENDING', 'SECOND': 'SECOND_REVIEW_PENDING'}.get(task.stage)
            if expected is None:
                raise Conflict('未知核验阶段')
            target = ('CANDIDATE' if task.stage == 'FIRST' else 'CONTENT_GEN_PENDING') if approved else 'REJECTED'
            if not self.repo.transition_product(task.product_id, expected, target):
                raise Conflict('商品状态冲突')
            if approved and task.stage == 'FIRST':
                if not self.repo.transition_product(task.product_id, 'CANDIDATE', 'SECOND_REVIEW_PENDING'):
                    raise Conflict('创建复核任务失败')
                target = 'SECOND_REVIEW_PENDING'
                self.repo.add(ReviewTask(tenant_id=self.tenant_id, product_id=task.product_id, stage='SECOND'))
            elif approved:
                self.repo.add(ContentJob(tenant_id=self.tenant_id, product_id=task.product_id))
            self.repo.add(AuditLog(tenant_id=self.tenant_id, action='review_approved' if approved else 'review_rejected', target=f'review:{task_id}', detail=comment))
            self.db.commit()
            return {'task_id': task_id, 'status': 'APPROVED' if approved else 'REJECTED', 'product_status': target}
        except Exception:
            self.db.rollback()
            raise

    def list_jobs(self):
        return [{'id': j.id, 'product_id': j.product_id, 'product_title': title, 'status': j.status} for j, title in self.repo.jobs()]

    def list_logs(self):
        return [{'id': x.id, 'action': x.action, 'target': x.target, 'detail': x.detail, 'created_at': x.created_at.isoformat()} for x in self.repo.logs()]
