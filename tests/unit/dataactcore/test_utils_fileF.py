from dataactcore.utils import fileF
from tests.unit.dataactcore.factories.fsrs import (FSRSGrantFactory, FSRSProcurementFactory, FSRSSubcontractFactory,
                                                   FSRSSubgrantFactory)
from tests.unit.dataactcore.factories.staging import AwardFinancialAssistanceFactory, AwardProcurementFactory
from tests.unit.dataactcore.factories.job import SubmissionFactory
from tests.unit.dataactcore.factories.domain import DunsFactory


def test_copy_values_procurement():
    model_row = fileF.ModelRow(None, FSRSProcurementFactory(duns='DUNS'), FSRSSubcontractFactory(duns='DUNS SUB'),
                               None, None)
    mapper = fileF.DeriveValues(procurement='duns')
    assert mapper(model_row) == 'DUNS'
    mapper = fileF.DeriveValues(subcontract='duns')
    assert mapper(model_row) == 'DUNS SUB'
    mapper = fileF.DeriveValues(grant='duns')
    assert mapper(model_row) is None


def test_copy_values_grant():
    model_row = fileF.ModelRow(None, None, None, FSRSGrantFactory(duns='DUNS'), FSRSSubgrantFactory(duns='DUNS SUB'))
    mapper = fileF.DeriveValues(grant='duns')
    assert mapper(model_row) == 'DUNS'
    mapper = fileF.DeriveValues(subgrant='duns')
    assert mapper(model_row) == 'DUNS SUB'
    mapper = fileF.DeriveValues(procurement='duns')
    assert mapper(model_row) is None


def test_prime_unique_id():
    model_row_contract = fileF.ModelRow(
        None, FSRSProcurementFactory(contract_agency_code='A', contract_idv_agency_code='B', contract_number=None,
                                     idv_reference_number='D'), None, None, None
    )
    model_row_grant = fileF.ModelRow(
        None, None, None, FSRSGrantFactory(federal_agency_id=None, fain='F'), None
    )
    key = fileF.mappings['PrimeAwardUniqueKey'](model_row_contract)
    assert key == 'CONT_AW_A_B_-none-_D'

    key = fileF.mappings['PrimeAwardUniqueKey'](model_row_grant)
    assert key == 'ASST_AW_-none-_F'


def test_determine_sub_award_type():
    model_row_subcontract = fileF.ModelRow(
        None, None, FSRSSubcontractFactory(), None, None
    )
    model_row_subgrant = fileF.ModelRow(
        None, None, None, None, FSRSSubgrantFactory()
    )
    sub_type = fileF.mappings['SubAwardType'](model_row_subcontract)
    assert sub_type == 'sub-contract'

    sub_type = fileF.mappings['SubAwardType'](model_row_subgrant)
    assert sub_type == 'sub-grant'


def test_country_name():
    model_row = fileF.ModelRow(
        None, None, None, None, FSRSSubgrantFactory(awardee_address_country='USA', principle_place_country='DE')
    )
    entity = fileF.mappings['SubAwardeeLegalEntityCountryName'](model_row)
    assert entity == 'United States'

    place = fileF.mappings['SubAwardeePlaceOfPerformanceCountryName'](model_row)
    assert place == 'Germany'


def test_zipcode_guard():
    model_row = fileF.ModelRow(
        None, None,
        FSRSSubcontractFactory(company_address_country='USA', company_address_zip='12345'),
        None, None
    )
    us_zip = fileF.mappings['SubAwardeeLegalEntityZIP+4'](model_row)
    foreign_zip = fileF.mappings['SubAwardeeLegalEntityForeignPostalCode'](model_row)
    assert us_zip == '12345'
    assert foreign_zip is None

    model_row.subcontract.company_address_country = 'RU'
    us_zip = fileF.mappings['SubAwardeeLegalEntityZIP+4'](model_row)
    foreign_zip = fileF.mappings['SubAwardeeLegalEntityForeignPostalCode'](model_row)
    assert us_zip is None
    assert foreign_zip == '12345'


def test_extract_cfda():
    model_row_grant = fileF.ModelRow(
        None, None, None, FSRSGrantFactory(cfda_numbers='49.021 One CFDA; 49.028 Two CFDA'), None
    )
    cfda_numbers = fileF.mappings['CFDA_Numbers'](model_row_grant)
    cfda_titles = fileF.mappings['CFDA_Titles'](model_row_grant)
    assert cfda_numbers == '49.021,49.028'
    assert cfda_titles == 'One CFDA,Two CFDA'

    model_row_grant = fileF.ModelRow(
        None, None, None, FSRSGrantFactory(cfda_numbers='37.021 One CFDA, with commas'), None
    )
    cfda_numbers = fileF.mappings['CFDA_Numbers'](model_row_grant)
    cfda_titles = fileF.mappings['CFDA_Titles'](model_row_grant)
    assert cfda_numbers == '37.021'
    assert cfda_titles == 'One CFDA, with commas'

    model_row_grant = fileF.ModelRow(
        None, None, None, FSRSGrantFactory(cfda_numbers='21.021 One CFDA, with an extra semicolon and space; '), None
    )
    cfda_numbers = fileF.mappings['CFDA_Numbers'](model_row_grant)
    cfda_titles = fileF.mappings['CFDA_Titles'](model_row_grant)
    assert cfda_numbers == '21.021'
    assert cfda_titles == 'One CFDA, with an extra semicolon and space'


def test_derive_duns_name(database):
    duns = DunsFactory(awardee_or_recipient_uniqu='123456789', legal_business_name='Test Duns')
    database.session.add(duns)
    database.session.commit()

    model_row_grant = fileF.ModelRow(
        None, None, None, FSRSGrantFactory(parent_duns=duns.awardee_or_recipient_uniqu), None
    )
    duns_name = fileF.mappings['UltimateParentLegalEntityName'](model_row_grant)
    assert duns_name == duns.legal_business_name

    model_row_grant = fileF.ModelRow(
        None, None, None, None, FSRSSubgrantFactory(parent_duns=duns.awardee_or_recipient_uniqu)
    )
    duns_name = fileF.mappings['SubAwardeeUltimateParentLegalEntityName'](model_row_grant)
    assert duns_name == duns.legal_business_name


def test_generate_f_rows(database, monkeypatch):
    """generate_f_rows should find and convert subaward data relevant to a
    specific submission id. We'll compare the resulting DUNs values for
    uniqueness"""
    # Setup - create awards, procurements/grants, subawards
    sess = database.session
    sub_1 = SubmissionFactory()
    sub_2 = SubmissionFactory()
    sess.add_all([sub_1, sub_2])
    sess.commit()

    awards = [AwardProcurementFactory(submission_id=sub_1.submission_id, piid='PIID1', parent_award_id='PIID1',
                                      awarding_sub_tier_agency_c='1234'),
              AwardProcurementFactory(submission_id=sub_1.submission_id, piid='PIID2', parent_award_id='PIID2',
                                      awarding_sub_tier_agency_c='1234'),
              AwardFinancialAssistanceFactory(submission_id=sub_1.submission_id, fain='FAIN1'),
              AwardFinancialAssistanceFactory(submission_id=sub_1.submission_id, fain='FAIN2'),
              AwardProcurementFactory(submission_id=sub_2.submission_id, piid='PIID1', parent_award_id='PIID1',
                                      awarding_sub_tier_agency_c='1234'),
              AwardFinancialAssistanceFactory(submission_id=sub_2.submission_id, fain='FAIN1')]
    sess.add_all(awards)
    procurements = {}
    for piid in ('PIID1', 'PIID2', 'PIID3'):
        procurements[piid] = [
            FSRSProcurementFactory(contract_number=piid, idv_reference_number=piid,
                                   subawards=[FSRSSubcontractFactory() for _ in range(3)],
                                   contracting_office_aid='1234'),
            FSRSProcurementFactory(contract_number=piid, idv_reference_number=piid,
                                   subawards=[],
                                   contracting_office_aid='1234'),
            FSRSProcurementFactory(contract_number=piid, idv_reference_number=piid,
                                   subawards=[FSRSSubcontractFactory() for _ in range(2)],
                                   contracting_office_aid='1234')
        ]
        sess.add_all(procurements[piid])
    grants = {}
    cfda_numbers = '49.021 One CFDA; 49.028 Two CFDA'
    for fain in ('FAIN0', 'FAIN1'):
        grants[fain] = [
            FSRSGrantFactory(fain=fain, subawards=[FSRSSubgrantFactory() for _ in range(3)], cfda_numbers=cfda_numbers),
            FSRSGrantFactory(fain=fain, subawards=[]),
            FSRSGrantFactory(fain=fain, subawards=[FSRSSubgrantFactory() for _ in range(2)], cfda_numbers=cfda_numbers)
        ]
        sess.add_all(grants[fain])
    sess.commit()

    actual = {result['SubAwardeeOrRecipientUniqueIdentifier'] for result in fileF.generate_f_rows(sub_1.submission_id)}
    expected = set()
    expected.update(sub.duns for proc in procurements['PIID1'] for sub in proc.subawards)
    expected.update(sub.duns for proc in procurements['PIID2'] for sub in proc.subawards)
    expected.update(sub.duns for grant in grants['FAIN1'] for sub in grant.subawards)
    assert actual == expected


def test_generate_f_rows_naics_desc(database, monkeypatch):
    """The NAICS description should be retireved from an AwardProcurement"""
    sub = SubmissionFactory()
    database.session.add(sub)
    database.session.commit()

    award = AwardProcurementFactory(submission_id=sub.submission_id, awarding_sub_tier_agency_c='1234')
    other_aps = [AwardProcurementFactory(submission_id=award.submission_id, awarding_sub_tier_agency_c='1234')
                 for _ in range(3)]
    proc = FSRSProcurementFactory(contract_number=award.piid, idv_reference_number=award.parent_award_id,
                                  subawards=[FSRSSubcontractFactory(naics=award.naics)],
                                  contracting_office_aid='1234')

    database.session.add_all([award, proc] + other_aps)
    database.session.commit()

    actual = {result['NAICS_Description'] for result in fileF.generate_f_rows(award.submission_id)}
    assert actual == {award.naics_description}
