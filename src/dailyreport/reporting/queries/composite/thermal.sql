SELECT 
  DISTINCT ON(wn, ft)
  wn as "water_category_name",
  ft as "fuel_type",

  %(branch)s as branch,
  %(thermal)s as thermal,
  
  "water_plan_day", 
  "water_actual_day", 
  "water_diff_day", 
  "water_actual_month", 
  "water_plan_month", 
  "water_diff_month",
  "water_plan_sum",
  "water_farward_temperature_estimated", 
  "water_backward_temperature_estimated", 
  "water_farward_temperature_actual", 
  "water_backward_temperature_actual", 
  "water_farward_temperature_diff", 
  "water_backward_temperature_diff",
  
  "fuel_plan_month",
  "fuel_plan_month_sum",
  "fuel_actual_month", 
  "fuel_plan_day", 
  "fuel_actual_day", 
  "fuel_diff_month", 
  "fuel_diff_day", 
  "fuel_plan_eqv", 
  "fuel_actual_eqv", 
  "real_plan_sum", 
  "real_plan_day",
  (fuel_actual_day * fuel_actual_eqv) as "fuel_actual_day_with_eqv", 
  (fuel_plan_day * fuel_plan_eqv) as "fuel_plan_day_with_eqv",
  "fuel_correct",

  "fuel_pickup", 
  "fuel_pickup_sum_period",   
  "income_month", 
  "income_today",

  "remain_tonnes", 
  "remain_days", 
  "remain_first_day_month",

  (SELECT SUM(plan_month) FROM electicity_consumption WHERE "date" = %(my_date)s AND boiler_id IN  %(my_boiler)s ) as "elec_plan_month", 
  (SELECT SUM(plan_day) FROM electicity_consumption WHERE "date" = %(my_date)s AND boiler_id IN %(my_boiler)s ) as "elec_plan_day", 
  (SELECT SUM(actual_day) FROM electicity_consumption WHERE "date" = %(my_date)s AND boiler_id IN %(my_boiler)s) as "elec_actual_day", 
  (SELECT 
      CASE WHEN AVG(diff_period_percent) IS NULL THEN 0.0 ELSE ROUND(CAST(AVG(diff_period_percent) as numeric), 3) END
   FROM electicity_consumption WHERE "date" = %(my_date)s AND boiler_id IN %(my_boiler)s AND actual_sum_period > 0) as "elec_diff_period_percent", 
  (SELECT SUM(plan_sum_period) FROM electicity_consumption WHERE "date" = %(my_date)s AND boiler_id IN %(my_boiler)s) as "elec_plan_sum_period", 
  (SELECT SUM(actual_sum_period) FROM electicity_consumption WHERE "date" = %(my_date)s AND boiler_id IN %(my_boiler)s) as "elec_actual_sum_period",

  (SELECT SUM(energy_value) FROM power_performance WHERE "date" = %(my_date)s  AND boiler_id IN %(my_boiler)s) as energy_value,
  (SELECT SUM(energy_value_month) FROM power_performance WHERE "date" = %(my_date)s  AND boiler_id IN %(my_boiler)s) as energy_value_month,

  (SELECT 
    CASE WHEN avg(outdoor_temp_actual) IS NULL THEN 0.0 ELSE ROUND(CAST(avg(outdoor_temp_actual) as numeric), 3) END
   FROM
     environment
   WHERE 
    "date" = %(my_date)s
    AND boiler_id IN %(my_boiler)s
    AND outdoor_temp_actual <> -273) as outdoor_temp_actual,

  (SELECT 
    CASE WHEN avg(outdoor_temp_plan) IS NULL THEN 0.0 ELSE ROUND(CAST(avg(outdoor_temp_plan) as numeric), 3) END
    FROM
      environment
    WHERE
      "date" = %(my_date)s
      AND boiler_id IN %(my_boiler)s
      AND outdoor_temp_plan <> -273) as outdoor_temp_plan  
  
FROM 
  (
  SELECT 
    wc."name" as wn, fi."type" as ft 
  FROM 
    water_consuption_category as wc
    FULL OUTER JOIN fuel_info as fi ON wc.boiler_id = fi.boiler_id
  WHERE 
    fi.boiler_id IN %(my_boiler)s 
    AND wc.boiler_id IN %(my_boiler)s
    AND fi.active = true
    AND wc.active = true
  ) as base

  LEFT OUTER JOIN 
  ( 
    SELECT 
      category.name as "water_category_name",
      SUM(plan_day) as "water_plan_day", 
      SUM(actual_day) as "water_actual_day", 
      SUM(diff_day) as "water_diff_day", 
      SUM(actual_month) as "water_actual_month", 
      SUM(plan_month) as "water_plan_month", 
      SUM(diff_month) as "water_diff_month",
      SUM(ROUND(CAST(plan_month * %(day_coef)s as numeric), 3)) as "water_plan_sum",
      SUM(farward_temperature_estimated) as "water_farward_temperature_estimated", 
      SUM(backward_temperature_estimated) as "water_backward_temperature_estimated", 
      SUM(farward_temperature_actual) as "water_farward_temperature_actual", 
      SUM(backward_temperature_actual) as "water_backward_temperature_actual", 
      SUM(farward_temperature_diff) as "water_farward_temperature_diff", 
      SUM(backward_temperature_diff) as "water_backward_temperature_diff"
    FROM
      water_consumption as consumption
      INNER JOIN water_consuption_category as category ON category.id = consumption.category_id
    WHERE
      consumption."date" = %(my_date)s
      AND category.boiler_id IN %(my_boiler)s
      AND category.active = true
    GROUP BY
      category.name
  ) as water ON water.water_category_name = base.wn

  LEFT OUTER JOIN 
  ( 
    SELECT
      info."type",
      SUM(plan_month) as "fuel_plan_month", 
      SUM(plan_month_sum) as "fuel_plan_month_sum",
      SUM(actual_month) as "fuel_actual_month", 
      SUM(plan_day) as "fuel_plan_day", 
      SUM(actual_day) as "fuel_actual_day", 
      SUM(diff_month) as "fuel_diff_month", 
      SUM(diff_day) as "fuel_diff_day", 
      ROUND( CAST(AVG(plan_eqv) as numeric),3 )as "fuel_plan_eqv", 
      ROUND( CAST(AVG(actual_eqv) as numeric),3 )as "fuel_actual_eqv", 
      SUM(real_plan_sum) as "real_plan_sum", 
      SUM(real_plan_day) as "real_plan_day",
      SUM(correct) as "fuel_correct"
    FROM
      fuel_consumption as consumption
      INNER JOIN fuel_info as info ON info.id = consumption.fuel_info_id
    WHERE
      consumption."date" = %(my_date)s
      AND info.boiler_id IN %(my_boiler)s
      AND info.active = true
    GROUP BY 
      info."type"
  ) as fuel ON fuel.type = base.ft

  LEFT OUTER JOIN 
  ( 
    SELECT
      info."type", 
      SUM(pickup) as "fuel_pickup", 
      SUM(pickup_sum_period) as "fuel_pickup_sum_period",   
      SUM("month") as "income_month", 
      SUM(today) as "income_today"
    FROM
      fuel_income as income
      INNER JOIN fuel_info as info ON info.id = income.fuel_info_id
    WHERE
      income."date" = %(my_date)s
      AND info.boiler_id IN %(my_boiler)s
      AND info.active = true
    GROUP BY
      info."type"
  ) as income ON income.type = base.ft

  LEFT OUTER JOIN 
  ( 
    SELECT
      info."type",
      SUM(tonnes) as "remain_tonnes", 
      SUM(days) as "remain_days", 
      SUM(first_day_month) as "remain_first_day_month"
    FROM
      fuel_remain as remain
      INNER JOIN fuel_info as info ON info.id = remain.fuel_info_id
    WHERE
      remain."date" = %(my_date)s
      AND info.boiler_id IN %(my_boiler)s
      AND info.active = true
    GROUP BY
      info."type"
  ) as remain ON remain.type = base.ft;
