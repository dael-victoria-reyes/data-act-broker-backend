"""drop_job_dep_fks

Revision ID: 9058e0136aba
Revises: 915a6bef6076
Create Date: 2016-08-26 10:31:16.538917

"""

# revision identifiers, used by Alembic.
revision = '9058e0136aba'
down_revision = '915a6bef6076'
branch_labels = None
depends_on = None

from alembic import op


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_data_broker():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('job_dependency_prerequisite_id_fkey', 'job_dependency', type_='foreignkey')
    op.drop_constraint('job_dependency_job_id_fkey', 'job_dependency', type_='foreignkey')
    ### end Alembic commands ###


def downgrade_data_broker():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('job_dependency_job_id_fkey', 'job_dependency', 'job', ['job_id'], ['job_id'])
    op.create_foreign_key('job_dependency_prerequisite_id_fkey', 'job_dependency', 'job', ['prerequisite_id'], ['job_id'])
    ### end Alembic commands ###

