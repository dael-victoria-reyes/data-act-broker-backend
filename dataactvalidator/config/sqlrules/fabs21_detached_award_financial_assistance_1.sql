-- When provided, FundingSubTierAgencyCode must be a valid 4-character sub-tier agency code from the Federal Hierarchy.
SELECT
    dafa.row_number,
    dafa.funding_sub_tier_agency_co
FROM detached_award_financial_assistance AS dafa
WHERE dafa.submission_id = {0}
    AND dafa.funding_sub_tier_agency_co <> ''
    AND NOT EXISTS (
        SELECT 1
        FROM sub_tier_agency AS sta
        WHERE sta.sub_tier_agency_code = dafa.funding_sub_tier_agency_co
    );
