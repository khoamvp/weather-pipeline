SELECT *

    -- nhiệt độ hôm qua
    LAG(temp_c, 1) OVER (
        PARTITION BY city
        ORDER BY extracted_date
    ) AS temp_yesterday,

    -- nhiệt độ 2 ngày trước
    LAG(temp_c, 2) OVER (
        PARTITION BY city
        ORDER BY extracted_date
    ) AS temp_2days_ago,

    -- trung bình nhiệt độ 3 ngày gần nhất
    AVG(temp_c) OVER (
        PARTITION BY city
        ORDER BY extracted_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_temp_3d,

    -- trung bình độ ẩm 3 ngày gần nhất
    AVG(humidity_pct) OVER (
        PARTITION BY city
        ORDER BY extracted_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_humidity_3d,

FROM `pipeline-496517.weather_data.daily_weather`

WHERE DATE(extracted_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)

ORDER BY city, extracted_date