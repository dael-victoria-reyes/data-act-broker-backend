-- PrimaryPlaceOfPerformanceForeignLocationDescription must be blank for aggregate or PII-redacted non-aggregate records
-- (RecordType = 1 or 3). For non-aggregate records (RecordType = 2), it must be blank for domestic places of
-- performance (PrimaryPlaceOfPerformanceCountryCode = USA).
SELECT
    row_number,
    place_of_performance_forei,
    place_of_perform_country_c,
    record_type
FROM detached_award_financial_assistance
WHERE submission_id = {0}
    AND COALESCE(place_of_performance_forei, '') <> ''
    AND (UPPER(place_of_perform_country_c) = 'USA'
         OR record_type in (1, 3)
    );
