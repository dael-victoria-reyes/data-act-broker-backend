from tests.unit.dataactcore.factories.staging import DetachedAwardFinancialAssistanceFactory
from tests.unit.dataactvalidator.utils import number_of_errors, query_columns
from dataactcore.models.domainModels import CityCode

_FILE = 'fabs41_detached_award_financial_assistance_2'


def test_column_headers(database):
    expected_subset = {"row_number", "place_of_performance_code"}
    actual = set(query_columns(_FILE, database))
    assert expected_subset == actual


def test_success(database):
    """ For PrimaryPlaceOfPerformanceCode XX##### or XX####R, where valid 5 or 9-digit PrimaryPlaceOfPerformanceZIP+4
        is provided : city code ##### or ####R should be valid and exist in the provided state, but will only trigger
        a warning if not.
    """

    # XX00000 validates here because it passes as long as the zip is valid in that state, this is checked
    # in a different place
    city_code = CityCode(city_code="10987", state_code="NY")
    city_code_2 = CityCode(city_code="1098R", state_code="NY")
    det_award_1 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="NY*****",
                                                          place_of_performance_zip4a="2")
    det_award_2 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="NY**123",
                                                          place_of_performance_zip4a="1")
    det_award_3 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="NY**123",
                                                          place_of_performance_zip4a=None)
    det_award_4 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="ny10987",
                                                          place_of_performance_zip4a="12345")
    det_award_5 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="NY10987",
                                                          place_of_performance_zip4a="12345-6789")
    det_award_6 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="Na10987",
                                                          place_of_performance_zip4a=None)
    det_award_7 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="Ny10988",
                                                          place_of_performance_zip4a='')
    det_award_8 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="nY000000",
                                                          place_of_performance_zip4a='12345')
    det_award_9 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="Ny10988",
                                                          place_of_performance_zip4a='city-wide')

    # Testing with R ending
    det_award_10 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="Ny1098R",
                                                           place_of_performance_zip4a='12345-6789')
    errors = number_of_errors(_FILE, database, models=[det_award_1, det_award_2, det_award_3, det_award_4, det_award_5,
                                                       det_award_6, det_award_7, det_award_8, det_award_9, det_award_10,
                                                       city_code, city_code_2])
    assert errors == 0


def test_failure(database):
    """ Test failure for PrimaryPlaceOfPerformanceCode XX##### or XX####R, where valid 5 or 9-digit
        PrimaryPlaceOfPerformanceZIP+4 is provided : city code ##### or ####R should be valid and exist in the provided
        state, but will only trigger a warning if not.
    """

    city_code = CityCode(city_code="10987", state_code="NY")
    city_code_2 = CityCode(city_code="1098R", state_code="NY")
    det_award_1 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="ny10986",
                                                          place_of_performance_zip4a="12345")
    det_award_2 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="NY10986",
                                                          place_of_performance_zip4a='12345')
    det_award_3 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="na10987",
                                                          place_of_performance_zip4a='12345-6789')
    det_award_4 = DetachedAwardFinancialAssistanceFactory(place_of_performance_code="na1098R",
                                                          place_of_performance_zip4a='12345-6789')
    errors = number_of_errors(_FILE, database, models=[det_award_1, det_award_2, det_award_3, det_award_4, city_code,
                                                       city_code_2])
    assert errors == 4
