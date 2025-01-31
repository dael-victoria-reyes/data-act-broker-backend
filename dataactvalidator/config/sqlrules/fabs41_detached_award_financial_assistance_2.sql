-- For PrimaryPlaceOfPerformanceCode XX##### or XX####R, where valid 5 or 9-digit PrimaryPlaceOfPerformanceZIP+4 is
-- provided : city code ##### or ####R should be valid and exist in the provided state, but will only trigger a warning
-- if not.
WITH detached_award_financial_assistance_d41_2_{0} AS
    (SELECT submission_id,
        row_number,
        place_of_performance_code,
        place_of_performance_zip4a
    FROM detached_award_financial_assistance
    WHERE submission_id = {0})
SELECT
    dafa.row_number,
    dafa.place_of_performance_code
FROM detached_award_financial_assistance_d41_2_{0} AS dafa
WHERE (UPPER(dafa.place_of_performance_code) ~ '^[A-Z][A-Z]\d\d\d\d\d$'
        OR UPPER(dafa.place_of_performance_code) ~ '^[A-Z][A-Z]\d\d\d\dR$')
    AND UPPER(dafa.place_of_performance_code) !~ '^[A-Z][A-Z]00000$'
    AND COALESCE(dafa.place_of_performance_zip4a, '') <> ''
    AND dafa.place_of_performance_zip4a <> 'city-wide'
    AND dafa.row_number NOT IN (
        SELECT DISTINCT sub_dafa.row_number
        FROM detached_award_financial_assistance_d41_2_{0} AS sub_dafa
        JOIN city_code
            ON SUBSTRING(sub_dafa.place_of_performance_code, 3, 5) = city_code.city_code
                AND UPPER(SUBSTRING(sub_dafa.place_of_performance_code, 1, 2)) = city_code.state_code
    );
