from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.schemas.contracts import ReviewDecision
from app.services.workspace import Conflict, WorkspaceService

router = APIRouter(prefix='/api/v1', tags=['workspace'])


def demo_only():
    if not settings.app_demo_mode:
        raise HTTPException(status_code=503, detail='演示接口未启用；认证和租户权限尚未实现')


def service(db: Session = Depends(get_db), _=Depends(demo_only)):
    return WorkspaceService(db)


@router.get('/products/pool')
def pool(svc: WorkspaceService = Depends(service)):
    return {'code': 0, 'message': 'ok', 'data': svc.list_products('FIRST_REVIEW_PENDING')}


@router.get('/products/candidates')
def candidates(svc: WorkspaceService = Depends(service)):
    return {'code': 0, 'message': 'ok', 'data': svc.list_products('SECOND_REVIEW_PENDING')}


def decide(task_id: int, body: ReviewDecision, approved: bool, svc: WorkspaceService):
    try:
        return {'code': 0, 'message': 'ok', 'data': svc.decide_review(task_id, approved, body.comment)}
    except Conflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post('/reviews/{task_id}/approve')
def approve(task_id: int, body: ReviewDecision, svc: WorkspaceService = Depends(service)):
    return decide(task_id, body, True, svc)


@router.post('/reviews/{task_id}/reject')
def reject(task_id: int, body: ReviewDecision, svc: WorkspaceService = Depends(service)):
    return decide(task_id, body, False, svc)


@router.get('/content-jobs')
def content_jobs(svc: WorkspaceService = Depends(service)):
    return {'code': 0, 'message': 'ok', 'data': svc.list_jobs()}


@router.get('/audit-logs')
def audit_logs(svc: WorkspaceService = Depends(service)):
    return {'code': 0, 'message': 'ok', 'data': svc.list_logs()}
