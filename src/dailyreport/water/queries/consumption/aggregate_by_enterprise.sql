SELECT
  'Примтеплоэнерго' as "object", 
  SUM(water_consumption.plan_day) as plan_day, 
  SUM(water_consumption.actual_day) as actual_day, 
  ROUND(SUM(water_consumption.plan_day - water_consumption.actual_day)::numeric,3) as diff,
  ROUND(((SUM(water_consumption.plan_day) - SUM(water_consumption.actual_day))*-100/SUM(water_consumption.plan_day))::numeric,2) as percent,
  water_consumption.date
FROM 
  public.boiler, 
  public.water_consumption, 
  public.water_consuption_category, 
  public.branch, 
  public.thermal
WHERE 
  boiler.id = water_consuption_category.boiler_id AND
  boiler."thermalArea_id" = thermal.id AND
  water_consuption_category.id = water_consumption.category_id AND
  water_consuption_category."name" = 'Общий расход' AND
  branch.id = boiler.branch_id AND
  boiler.enabled = true AND 
  water_consuption_category.active = true AND 
  water_consumption.date BETWEEN %(from_date)s AND %(to_date)s AND
  water_consumption.plan_day > 0
  boiler.id IN %(boilers)s
GROUP BY
  "date"
ORDER BY
  water_consumption.date ASC;