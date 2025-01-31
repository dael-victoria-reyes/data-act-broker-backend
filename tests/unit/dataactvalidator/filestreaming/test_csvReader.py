import csv

from unittest.mock import Mock

from dataactvalidator.filestreaming import csvReader


def test_count_and_set_headers_flex():
    """Verify that we are setting the correct flex headers"""
    reader = csvReader.CsvReader()
    csv_schema = [Mock(name_short='some_col'), Mock(name_short='other')]
    header_row = ['ignored', 'flex_my_col', 'some_col', 'flex_other', 'some_col']

    result = reader.count_and_set_headers(csv_schema, header_row)
    assert result == {'some_col': 2, 'other': 0}
    assert reader.expected_headers == [None, None, 'some_col', None, 'some_col']
    assert reader.flex_headers == [None, 'flex_my_col', None, 'flex_other', None]


def test_get_next_record_flex():
    """Verify that we get a list of FlexFields if present"""
    reader = csvReader.CsvReader()
    reader.column_count = 6
    reader.expected_headers = ['a', 'b', 'c', None, None, None]
    reader.flex_headers = [None, None, None, 'flex_d', 'flex_e', None]
    reader.csv_reader = csv.reader(['A,"B\n",C,D,E,F'], dialect='excel', delimiter=',')
    return_dict, flex_fields = reader.get_next_record()
    assert return_dict == {'a': 'A', 'b': 'B\n', 'c': 'C'}
    assert len(flex_fields) == 2
    assert flex_fields[0].header == 'flex_d'
    assert flex_fields[0].cell == 'D'
    assert flex_fields[1].header == 'flex_e'
    assert flex_fields[1].cell == 'E'


def test_normalize_headers():
    """ Verify we return the transformed headers depending on the long_headers parameter and that special exceptions
        are processed correctly.
    """
    # Verify names are properly lowercased and not mapped if long_headers is false
    headers = [
        'AllocationTransferAgencyIdentifier', 'BeginningPeriodOfAvailability', 'flex_mycol', 'FLEX_(ANOTHER)'
    ]
    mapping = {'allocationtransferagencyidentifier': 'ata', 'beginningperiodofavailability': 'boa'}

    result = csvReader.normalize_headers(headers, False, mapping)
    assert list(result) == [
        'allocationtransferagencyidentifier', 'beginningperiodofavailability', 'flex_mycol', 'flex_another'
    ]

    # Verify names are properly lowercased and mapped to short names if long_headers is true
    result = csvReader.normalize_headers(headers, True, mapping)
    assert list(result) == ['ata', 'boa', 'flex_mycol', 'flex_another']

    # Verify that special hardcoded exceptions are properly handled
    headers = ['deobligationsrecoveriesrefundsofprioryearbyprogramobjectclass_cpe', 'facevalueloanguarantee',
               'budgetauthorityavailableamounttotal_cpe', 'CorrectionLateDeleteIndicator', 'place_of_performance_zip4']
    mapping = {
        'deobligationsrecoveriesrefundsdofprioryearbyprogramobjectclass_cpe': 'drfpbpo',
        'facevalueofdirectloanorloanguarantee': 'fvdllg',
        'totalbudgetaryresources_cpe': 'tbr',
        'correctiondeleteindicator': 'cdi',
        'place_of_performance_zip4a': 'zip4a'
    }

    # Test for long special headers to be properly mapped
    result = csvReader.normalize_headers(headers, False, mapping)
    assert list(result) == [
        'deobligationsrecoveriesrefundsdofprioryearbyprogramobjectclass_cpe', 'facevalueofdirectloanorloanguarantee',
        'totalbudgetaryresources_cpe', 'correctiondeleteindicator', 'place_of_performance_zip4a']

    # Test for short special headers to be properly mapped
    result = csvReader.normalize_headers(headers, True, mapping)
    assert list(result) == ['drfpbpo', 'fvdllg', 'tbr', 'cdi', 'zip4a']
