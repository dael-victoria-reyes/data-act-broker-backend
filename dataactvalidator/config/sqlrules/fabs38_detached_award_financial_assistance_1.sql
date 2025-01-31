-- FundingOfficeCode must be submitted for new awards (ActionType = A or blank) whose ActionDate is on or after
-- October 1, 2018, and whose CorrectionDeleteIndicator is either Blank or C.
CREATE OR REPLACE function pg_temp.is_date(str text) returns boolean AS $$
BEGIN
    perform CAST(str AS DATE);
    return TRUE;
EXCEPTION WHEN others THEN
    return FALSE;
END;
$$ LANGUAGE plpgsql;

SELECT
    row_number,
    funding_office_code,
    action_type,
    correction_delete_indicatr,
    action_date
FROM detached_award_financial_assistance
WHERE submission_id = {0}
    AND COALESCE(funding_office_code, '') = ''
    AND UPPER(COALESCE(action_type, '')) IN ('A', '')
    AND UPPER(COALESCE(correction_delete_indicatr, '')) <> 'D'
    AND (CASE WHEN pg_temp.is_date(COALESCE(action_date, '0'))
            THEN CAST(action_date AS DATE)
        END) >= CAST('10/01/2018' AS DATE);
