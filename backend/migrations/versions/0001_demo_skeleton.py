"""Initial demo skeleton; NOT the frozen production data contract."""
from alembic import op
import sqlalchemy as sa

revision = '0001_demo_skeleton'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('products', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.Integer(), nullable=False), sa.Column('platform', sa.String(32), nullable=False), sa.Column('platform_product_id', sa.String(128), nullable=False), sa.Column('title', sa.String(512), nullable=False), sa.Column('category', sa.String(128), nullable=False), sa.Column('status', sa.String(32), nullable=False), sa.Column('version', sa.Integer(), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint('tenant_id', 'platform', 'platform_product_id'))
    op.create_index('ix_products_tenant_id', 'products', ['tenant_id'])
    op.create_index('ix_products_status', 'products', ['status'])
    op.create_table('review_tasks', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.Integer(), nullable=False), sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False), sa.Column('stage', sa.String(16), nullable=False), sa.Column('status', sa.String(16), nullable=False), sa.Column('comment', sa.Text(), nullable=False))
    op.create_index('ix_review_tasks_tenant_id', 'review_tasks', ['tenant_id'])
    op.create_index('ix_review_tasks_product_id', 'review_tasks', ['product_id'])
    op.create_table('content_jobs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.Integer(), nullable=False), sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False), sa.Column('status', sa.String(32), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_content_jobs_tenant_id', 'content_jobs', ['tenant_id'])
    op.create_index('ix_content_jobs_product_id', 'content_jobs', ['product_id'])
    op.create_table('audit_logs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.Integer(), nullable=False), sa.Column('action', sa.String(64), nullable=False), sa.Column('target', sa.String(128), nullable=False), sa.Column('detail', sa.Text(), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('content_jobs')
    op.drop_table('review_tasks')
    op.drop_table('products')
