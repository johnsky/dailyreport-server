SELECT 
  branch_name as "branch", 
  thermal_name as "thermal", 
  boiler_name as "boiler",

  wid,
  fid,
 
  wname as "water_category_name",
  ftype as "fuel_type",
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

  "fuel_mark", 
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

  "elec_plan_month", 
  "elec_plan_day", 
  "elec_actual_day", 
  "elec_diff_period_percent", 
  "elec_plan_sum_period", 
  "elec_actual_sum_period",

  energy_value,
  energy_value_month,

  outdoor_temp_actual,
  outdoor_temp_plan  
  
FROM 
  (
    SELECT * FROM 
      ( 
      SELECT 
        boiler.id as boiler_id, 
        boiler.name as boiler_name, 
        branch.name as branch_name, 
        thermal.name as thermal_name 
      FROM boiler 
        INNER JOIN branch ON branch.id = boiler.branch_id 
        INNER JOIN thermal ON thermal.id = boiler."thermalArea_id" 
      WHERE 
        boiler.id = %(my_boiler)s
        AND boiler.enabled = true 
      ORDER BY 
        branch."name", thermal."name", boiler."name" 
      ) as company_object

      FULL OUTER JOIN
      (
    SELECT  
      "name" as wname, row_number() over(ORDER BY "name" DESC) as wr, boiler_id as wb, id as wid
    FROM  
      water_consuption_category 
    WHERE  
      boiler_id = %(my_boiler)s AND active=true 
    GROUP BY "name", boiler_id, id
      ) as water_category ON company_object.boiler_id = water_category.wb 

      FULL OUTER JOIN
      (
    SELECT  
      "type" as ftype , row_number() over(ORDER BY "type" DESC) as fr, boiler_id as fb, id as fid
    FROM  
      fuel_info 
    WHERE  
      boiler_id =%(my_boiler)s AND active=true 
    GROUP BY "type", boiler_id, id
      ) as fuel ON company_object.boiler_id = fuel.fb AND water_category.wr = fuel.fr
  ) as base

  LEFT OUTER JOIN 
  ( 
    SELECT 
      water_consumption.plan_day as "water_plan_day", 
      water_consumption.actual_day as "water_actual_day", 
      water_consumption.diff_day as "water_diff_day", 
      water_consumption.actual_month as "water_actual_month", 
      water_consumption.plan_month as "water_plan_month", 
      water_consumption.diff_month as "water_diff_month",   
      water_consumption.category_id as "water_category_id",
      ROUND(CAST(water_consumption.plan_month * %(day_coef)s as numeric), 3) as "water_plan_sum",
      water_consumption.farward_temperature_estimated as "water_farward_temperature_estimated", 
      water_consumption.backward_temperature_estimated as "water_backward_temperature_estimated", 
      water_consumption.farward_temperature_actual as "water_farward_temperature_actual", 
      water_consumption.backward_temperature_actual as "water_backward_temperature_actual", 
      water_consumption.farward_temperature_diff as "water_farward_temperature_diff", 
      water_consumption.backward_temperature_diff as "water_backward_temperature_diff"
    FROM
      water_consumption
    WHERE
      "date" = %(my_date)s
      AND boiler_id =%(my_boiler)s
  ) as water ON water.water_category_id = base.wid

  LEFT OUTER JOIN 
  ( 
    SELECT
      fuel_consumption.fuel_info_id,
      fuel_consumption.mark as "fuel_mark", 
      fuel_consumption.plan_month as "fuel_plan_month", 
      fuel_consumption.actual_month as "fuel_actual_month", 
      fuel_consumption.plan_day as "fuel_plan_day", 
      fuel_consumption.actual_day as "fuel_actual_day", 
      fuel_consumption.diff_month as "fuel_diff_month", 
      fuel_consumption.diff_day as "fuel_diff_day", 
      fuel_consumption.plan_eqv as "fuel_plan_eqv", 
      fuel_consumption.actual_eqv as "fuel_actual_eqv", 
      fuel_consumption.real_plan_sum, 
      fuel_consumption.real_plan_day,
      fuel_consumption.correct as "fuel_correct",
      fuel_consumption.plan_month_sum as "fuel_plan_month_sum"
    FROM
      fuel_consumption
    WHERE
      "date" = %(my_date)s
      AND boiler_id = %(my_boiler)s
  ) as fuel ON fuel.fuel_info_id = base.fid

  LEFT OUTER JOIN 
  ( 
    SELECT
      fuel_info_id, 
      pickup as "fuel_pickup", 
      pickup_sum_period as "fuel_pickup_sum_period",   
      "month" as "income_month", 
      today as "income_today"
    FROM
      fuel_income
    WHERE
      "date" = %(my_date)s
      AND boiler_id = %(my_boiler)s
  ) as income ON income.fuel_info_id = base.fid

  LEFT OUTER JOIN 
  ( 
    SELECT
      fuel_info_id, 
      tonnes as "remain_tonnes", 
      days as "remain_days", 
      first_day_month as "remain_first_day_month"
    FROM
      fuel_remain
    WHERE
      "date" = %(my_date)s
      AND boiler_id = %(my_boiler)s
  ) as remain ON remain.fuel_info_id = base.fid

  LEFT OUTER JOIN 
  ( 
    SELECT
      boiler_id, 
      plan_month as "elec_plan_month", 
      plan_day as "elec_plan_day", 
      actual_day as "elec_actual_day", 
      diff_period_percent as "elec_diff_period_percent", 
      plan_sum_period as "elec_plan_sum_period", 
      actual_sum_period as "elec_actual_sum_period"
    FROM
      electicity_consumption
    WHERE
      "date" = %(my_date)s
      AND boiler_id = %(my_boiler)s
  ) as electro ON electro.boiler_id = base.boiler_id

  LEFT OUTER JOIN 
  ( 
    SELECT
      boiler_id, 
      power_performance.energy_value, 
      power_performance.energy_value_month
    FROM
      power_performance
    WHERE
      "date" = %(my_date)s
      AND boiler_id = %(my_boiler)s
  ) as power ON power.boiler_id = base.boiler_id

  LEFT OUTER JOIN 
  ( 
    SELECT
      boiler_id, 
      CASE environment.outdoor_temp_actual WHEN -273.0 THEN 0.0 ELSE environment.outdoor_temp_actual END, 
      CASE environment.outdoor_temp_plan WHEN -273.0 THEN 0.0 ELSE environment.outdoor_temp_plan END
    FROM
      environment
    WHERE
      "date" = %(my_date)s
      AND boiler_id = %(my_boiler)s
  ) as env ON env.boiler_id = base.boiler_id

ORDER BY branch, thermal, boiler;
