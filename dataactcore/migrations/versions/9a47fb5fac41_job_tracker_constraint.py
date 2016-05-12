"""job_tracker_constraint

Revision ID: 9a47fb5fac41
Revises: 2701ef6ccb69
Create Date: 2016-05-02 16:36:23.852437

"""

# revision identifiers, used by Alembic.
revision = '9a47fb5fac41'
down_revision = '2701ef6ccb69'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()





def upgrade_error_data():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def downgrade_error_data():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def upgrade_job_tracker():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_job_submission_id', 'job', type_='foreignkey')
    op.create_foreign_key('fk_job_submission_id', 'job', 'submission', ['submission_id'], ['submission_id'], ondelete='CASCADE')
    ### end Alembic commands ###


def downgrade_job_tracker():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_job_submission_id', 'job', type_='foreignkey')
    op.create_foreign_key('fk_job_submission_id', 'job', 'submission', ['submission_id'], ['submission_id'])
    ### end Alembic commands ###


def upgrade_user_manager():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def downgrade_user_manager():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def upgrade_validation():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###


def downgrade_validation():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###

