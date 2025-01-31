-- AwardingSubTierAgencyCode must be provided when AwardingOfficeCode is not provided.
SELECT
    row_number,
    awarding_sub_tier_agency_c,
    awarding_office_code
FROM detached_award_financial_assistance
WHERE submission_id = {0}
    AND COALESCE(awarding_sub_tier_agency_c, '') = ''
    AND COALESCE(awarding_office_code, '') = ''