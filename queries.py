Q5_GEMINI_TRENDS = """
SELECT 
    application.ticket_number,
    serviceMaster.name AS Service_Name,
    ulb.name AS ULB_Name,
    application.status,
    application.request_type,
    application.createdAt,
    application.updatedAt,
    eDistrict.submissionDateTime,
    eDistrict.appointmentDateTime,
    eDistrict.collectionDateTime,
    eDistrict.actionDate,
    eDistrict.approvedDateTime,
    eDistrict.sentBackDateTime,
    eDistrict.rejectionDateTime,
    eDistrict.deliveryDateTime,
    eDistrict.reason,
    DATEDIFF(NOW(), application.updatedAt) AS Days_Since_Update,
    DATEDIFF(NOW(), eDistrict.submissionDateTime) AS Days_Since_Submission,
    CASE 
        WHEN DATEDIFF(NOW(), application.updatedAt) BETWEEN 0 AND 15 THEN '0-15 Days'
        WHEN DATEDIFF(NOW(), application.updatedAt) BETWEEN 16 AND 30 THEN '16-30 Days'
        WHEN DATEDIFF(NOW(), application.updatedAt) BETWEEN 31 AND 60 THEN '31-60 Days'
        WHEN DATEDIFF(NOW(), application.updatedAt) > 60 THEN '60+ Days'
    END AS Age_Group,
    MONTHNAME(application.createdAt) AS Application_Month,
    DAYNAME(application.createdAt) AS Application_Day
FROM application
LEFT JOIN serviceCategory 
    ON application.serviceCategoryId = serviceCategory.id
LEFT JOIN serviceMaster 
    ON serviceCategory.serviceMasterId = serviceMaster.id
LEFT JOIN address 
    ON application.addressId = address.id
LEFT JOIN ulb 
    ON address.ulbId = ulb.id
LEFT JOIN eDistrict 
    ON application.id = eDistrict.applicationId
WHERE application.Is_active = 1
LIMIT 2500;
"""