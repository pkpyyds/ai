"""Explicit local-only demo seed, never part of migrations or production startup."""
from sqlalchemy import select
from app.config import settings
from app.database import SessionLocal
from app.models.entities import Product, ReviewTask


def main():
    if not settings.app_demo_mode:
        raise SystemExit('Set APP_DEMO_MODE=true explicitly before seeding demo data')
    with SessionLocal() as db:
        if db.scalar(select(Product.id).limit(1)):
            print('Demo database already contains data; skipped.')
            return
        for i, (title, category, status, stage) in enumerate([
            ('便携式旅行收纳袋', '家居收纳', 'FIRST_REVIEW_PENDING', 'FIRST'),
            ('不锈钢保温咖啡杯', '厨房用品', 'FIRST_REVIEW_PENDING', 'FIRST'),
            ('桌面理线收纳盒', '办公用品', 'FIRST_REVIEW_PENDING', 'FIRST'),
            ('可折叠笔记本支架', '办公用品', 'SECOND_REVIEW_PENDING', 'SECOND'),
        ], 1):
            p = Product(tenant_id=1, platform='demo', platform_product_id=f'SP-{1000+i}', title=title, category=category, status=status)
            db.add(p); db.flush()
            db.add(ReviewTask(tenant_id=1, product_id=p.id, stage=stage))
        db.commit()
    print('Demo fixtures created.')


if __name__ == '__main__':
    main()
