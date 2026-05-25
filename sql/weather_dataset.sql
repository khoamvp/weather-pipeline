SELECT *
FROM `pipeline-496517.weather_data.daily_weather`

WHERE DATE(extracted_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)

ORDER BY city, extracted_date;