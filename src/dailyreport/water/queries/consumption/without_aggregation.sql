SELECT 
  branch."name" as branch, 
  thermal."name" as thermal, 
  boiler."name" as boiler,  
  water_consumption.plan_day, 
  water_consumption.actual_day, 
  ROUND((water_consumption.plan_day - water_consumption.actual_day)::numeric,3) as diff,
  ROUND(((water_consumption.plan_day - water_consumption.actual_day)*-100/water_consumption.plan_day)::numeric,2) as percent,
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
  water_consumption.plan_day > 0 AND 
  boiler.id IN %(boilers)s
ORDER BY
  branch."name" ASC, 
  thermal."name" ASC, 
  boiler."name" ASC, 
  water_consumption.date ASC;
