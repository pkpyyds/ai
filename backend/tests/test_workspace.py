import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.entities import AuditLog, ContentJob, Product, ReviewTask


@pytest.fixture
def state():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)
    with sessions() as session:
        item = Product(tenant_id=1, platform='demo', platform_product_id='sp1', title='示例', category='办公用品', status='FIRST_REVIEW_PENDING')
        session.add(item); session.flush()
        session.add(ReviewTask(tenant_id=1, product_id=item.id, stage='FIRST'))
        session.commit()
    def override_db():
        with sessions() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    old = settings.app_demo_mode
    settings.app_demo_mode = True
    yield TestClient(app), sessions
    settings.app_demo_mode = old
    app.dependency_overrides.clear()
    engine.dispose()


def test_two_stage_review_creates_only_pending_content_job(state):
    client, sessions = state
    product = client.get('/api/v1/products/pool').json()['data'][0]
    first_id = product['task_id']
    assert client.post(f'/api/v1/reviews/{first_id}/approve', json={'comment': 'ok'}).status_code == 200
    assert client.post(f'/api/v1/reviews/{first_id}/approve', json={'comment': 'ok'}).status_code == 409
    assert client.get('/api/v1/products/pool').json()['data'] == []
    candidate = client.get('/api/v1/products/candidates').json()['data'][0]
    assert client.post(f"/api/v1/reviews/{candidate['task_id']}/approve", json={'comment': 'ok'}).status_code == 200
    jobs = client.get('/api/v1/content-jobs').json()['data']
    assert len(jobs) == 1 and jobs[0]['status'] == 'PENDING'
    with sessions() as db:
        assert db.scalar(select(Product)).status == 'CONTENT_GEN_PENDING'
        assert len(db.scalars(select(AuditLog)).all()) == 2
        assert len(db.scalars(select(ContentJob)).all()) == 1


def test_rejection_requires_comment_and_does_not_advance(state):
    client, sessions = state
    task = client.get('/api/v1/products/pool').json()['data'][0]['task_id']
    assert client.post(f'/api/v1/reviews/{task}/reject', json={'comment': ''}).status_code == 422
    assert client.post(f'/api/v1/reviews/{task}/reject', json={'comment': '不符合'}).status_code == 200
    assert client.get('/api/v1/products/candidates').json()['data'] == []
    with sessions() as db:
        assert db.scalar(select(Product)).status == 'REJECTED'
        assert db.scalars(select(ContentJob)).all() == []


def test_demo_disabled_by_default(state):
    client, _ = state
    settings.app_demo_mode = False
    assert client.get('/api/v1/products/pool').status_code == 503
    assert client.get('/api/v1/health').json()['data']['crawl_enabled'] is False
