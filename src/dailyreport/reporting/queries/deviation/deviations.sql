SELECT 
  dev.id as "id", 
  (SELECT COUNT(id) FROM public.deviation_comment WHERE deviation_id = dev.id) as row_span,
  row_number() OVER (PARTITION BY dev.id ORDER BY dev.start_date, dev.id, com.date) row_id,
  st."name" as "state_name", 
  res."name" as "resource_name", 
  boiler."name" as "boiler_name", 
  thermal."name" as "thermal_name",
  branch."name" as "branch_name",
  dev.created as "deviation_created", 
  dev.close_date as "close_date", 
  dev.start_date as "start_date", 
  date_part('day',now() - dev.start_date)::integer as "duration",
  dev.state_id as "deviation_state_id", 
  dev.resource_id as resource_id, 
  --dev.boiler_id, 
  '[' || to_char(com.date,'YYYY-MM-DD HH:MI') || ' | ' || us.username || '] - ' || com."text" as "comment",
  -- com.author_id, 
  -- com."text", 
  cau."name",
  --cau.id as 
  CASE WHEN dev.water_id IS NOT NULL THEN w.actual_day
	WHEN dev.fuel_id IS NOT NULL THEN f.actual_day
	WHEN dev.electricity_id IS NOT NULL THEN e.actual_day
	ELSE NULL	
  END as actual,

  CASE WHEN dev.water_id IS NOT NULL THEN w.plan_day
	WHEN dev.fuel_id IS NOT NULL THEN f.plan_day
	WHEN dev.electricity_id IS NOT NULL THEN e.plan_day
	ELSE NULL
  END as plan
FROM 
  public.deviation as dev
  INNER JOIN public.boiler as boiler ON boiler.id = dev.boiler_id
  INNER JOIN public.thermal as thermal ON thermal.id = boiler."thermalArea_id"
  INNER JOIN public.branch as branch ON branch.id = boiler.branch_id
  INNER JOIN public.deviation_comment as com ON com.deviation_id = dev.id
  INNER JOIN public.auth_user as us ON us.id = com.author_id
  INNER JOIN public.resource as res ON res.id = dev.resource_id
  INNER JOIN public.deviation_state as st ON st.id = dev.state_id 
  FULL OUTER JOIN public.deviation_cause as cau ON cau.id = dev.cause_id
  FULL OUTER JOIN public.water_consumption as w ON w.id = dev.water_id
  FULL OUTER JOIN public.fuel_consumption as f ON f.id = dev.fuel_id
  FULL OUTER JOIN public.electicity_consumption as e ON e.id = dev.electricity_id
WHERE 
  dev.id IN %(deviation_ids)s
ORDER BY
  dev.start_date, dev.id, com.date;

