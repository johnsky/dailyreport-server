select
  co3.title as company,
  co2.title as branch,
  co1.title as tr,
  p.title as kotel,
  'Покупное тепло' as tstp,
  'Покупное тепло' as title,
  ltree2text(ct.treeId) || ' ' || GetCostTypeFullTitle(ct.costTypeId) as costTypeTitleFullPath, -- выводить полный путь!
  CASE WHEN c.valueplan=0 THEN 0 ELSE c.valueplan END,
  CASE WHEN c.valuereal=0 THEN 0 ELSE c.valuereal END,
  (c.valuereal - c.valueplan) as otklonenie, CASE WHEN c.valueplan=0 THEN 0 ELSE ((c.valuereal - c.valueplan)/c.valueplan*100) END as procent_otkl,
  to_char(c.dateTimeStart, 'YYYY') || ' ' || to_char(c.dateTimeStart, 'TMMonth') as date
FROM cost c
  INNER JOIN companyObject co1 ON co1.companyObjectId=c.providerWaterId and co1.systemId = c.providerWaterSystemId and c.isProviderIntoPrimtepCompany = false
  INNER JOIN companyObject co2 ON co2.treeId = text2ltree(substring(ltree2text(co1.treeId) FROM '.*(?=\\.\\d?)'))
  INNER JOIN companyObject co3 ON co3.treeId = text2ltree(substring(ltree2text(co2.treeId) FROM '.*(?=\\.\\d?)'))
  INNER JOIN provider p ON c.providerHotId = p.providerId AND c.providerHotSystemId = p.systemId
  INNER JOIN costType ct ON c.costTypeId = ct.costTypeId
  UNION
  -- котельные, поставщики воды
  select
  co4.title as company,
  co3.title as fil,
  co2.title as tr,
  co1.title as kotel,
  co1.title as tstp,
  p.title as title,
  ltree2text(ct.treeId) || ' ' || GetCostTypeFullTitle(ct.costTypeId) as costTypeTitleFullPath, -- выводить полный путь!
  CASE WHEN c.valueplan=0 THEN 0 ELSE c.valueplan END,
  CASE WHEN c.valuereal=0 THEN 0 ELSE c.valuereal END,
  (c.valuereal - c.valueplan) as otklonenie,
  CASE WHEN c.valueplan=0 THEN 0 ELSE ((c.valuereal - c.valueplan)/c.valueplan*100) END as procent_otkl,
  to_char(c.dateTimeStart, 'YYYY') || ' ' || to_char(c.dateTimeStart, 'TMMonth') as date
  FROM cost c
   INNER JOIN companyObject co1 ON co1.companyObjectId=c.providerHotId and co1.systemId = c.providerHotSystemId and c.isProviderIntoPrimtepCompany = true and (co1.companyObjectTypeId = 5 or co1.companyObjectTypeId = 3)
   INNER JOIN companyObject co2 
    ON co2.treeId = text2ltree(substring(ltree2text(co1.treeId) FROM '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co3 
    ON co3.treeId = text2ltree(substring(ltree2text(co2.treeId) FROM '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co4
    ON co4.treeId = text2ltree(substring(ltree2text(co3.treeId) FROM '.*(?=\\.\\d?)'))
   INNER JOIN provider p
    ON c.providerWaterId = p.providerId AND c.providerWaterSystemId = p.systemId
   INNER JOIN costType ct
    ON c.costTypeId = ct.costTypeId
  UNION
  -- котельные
  select
    co4.title as company,
    co3.title as fil,
    co2.title as tr,
    co1.title as kotel,
    co1.title as tstp,
    'Выработка' as title,
    ltree2text(ct.treeId) || ' ' || GetCostTypeFullTitle(ct.costTypeId) as costTypeTitleFullPath, -- выводить полный путь!
    CASE WHEN c.valueplan=0 THEN 0 ELSE c.valueplan END,
    CASE WHEN c.valuereal=0 THEN 0 ELSE c.valuereal END,
    (c.valuereal - c.valueplan) as otklonenie,
    CASE WHEN c.valueplan=0 THEN 0 ELSE ((c.valuereal - c.valueplan)/c.valueplan*100) END as procent_otkl,
    to_char(c.dateTimeStart, 'YYYY') || ' ' || to_char(c.dateTimeStart, 'TMMonth') as date
  FROM cost c
   INNER JOIN companyObject co1 ON co1.companyObjectId=c.providerHotId and co1.systemId = c.providerHotSystemId and c.isProviderIntoPrimtepCompany = true and co1.companyObjectTypeId = 5
   INNER JOIN companyObject co2 
    ON co2.treeId = text2ltree(substring(ltree2text(co1.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co3 
    ON co3.treeId = text2ltree(substring(ltree2text(co2.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co4
    ON co4.treeId = text2ltree(substring(ltree2text(co3.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN costType ct
    ON c.costTypeId = ct.costTypeId
  WHERE 
      c.providerWaterId = 0 and
      c.providerWaterSystemId = 0 and
      (ct.costTypeId = 34 OR ct.costTypeId = 35)
  UNION
  -- ЦТП
  select
    co5.title as company,
    co4.title as fil,
    co3.title as tr,
    co2.title as kotel,
    co1.title as tstp,
    p.title as title,
    ltree2text(ct.treeId) || ' ' || GetCostTypeFullTitle(ct.costTypeId) as costTypeTitleFullPath, -- выводить полный путь!
    CASE WHEN c.valueplan=0 THEN 0 ELSE c.valueplan END,
    CASE WHEN c.valuereal=0 THEN 0 ELSE c.valuereal END,
    (c.valuereal - c.valueplan) as otklonenie,
    CASE WHEN c.valueplan=0 THEN 0 ELSE ((c.valuereal - c.valueplan)/c.valueplan*100) END as procent_otkl,
    to_char(c.dateTimeStart, 'YYYY') || ' ' || to_char(c.dateTimeStart, 'TMMonth') as date
  FROM cost c
   INNER JOIN companyObject co1 ON co1.companyObjectId=c.providerHotId and co1.systemId = c.providerHotSystemId and c.isProviderIntoPrimtepCompany = true and co1.companyObjectTypeId = 6
   INNER JOIN companyObject co2 
    ON co2.treeId = text2ltree(substring(ltree2text(co1.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co3 
    ON co3.treeId = text2ltree(substring(ltree2text(co2.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co4
    ON co4.treeId = text2ltree(substring(ltree2text(co3.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN companyObject co5
    ON co5.treeId = text2ltree(substring(ltree2text(co4.treeId) from '.*(?=\\.\\d?)'))
   INNER JOIN provider p
    ON c.providerWaterId = p.providerId AND c.providerWaterSystemId = p.systemId
   INNER JOIN costType ct
    ON c.costTypeId = ct.costTypeId;
          
          
  -- запрос в excel который использоватлся раньше
  -- тут список котельных сверху вниз со структурой! TODO нужно забирать еще и данные о внешних источниках тепла
  select
  co1.title as company,
  co2.title as fil,
  co3.title as tr,
  co4.title as kotel,
  co4.title as tstp,
  pp.title,
  --ct1.title || '.' || ct2.title || '.' || ct3.title || '.' ||  ct4.title-- || '.' || ct5.title --|| '.' || ct6.title--,
  ltree2text(ct.treeId) || ' ' || GetCostTypeFullTitle(ct.costTypeId) as costTypeTitleFullPath, -- выводить полный путь!
  --ct.treeId,
  --CASE
  --WHEN c.valueplan=0 THEN '' --c.valueplan=0 THEN 0
  --ELSE cast(c.valueplan as text) || ' ' || cast(c.valuereal as text) || ' ' || cast((c.valuereal - c.valueplan) as text) || ' ' || cast(((c.valuereal - c.valueplan)/c.valueplan*100) as text)
  --c.valueplan::text || c.valuereal::text || (c.valuereal - c.valueplan)::text || ((c.valuereal - c.valueplan)/c.valueplan*100)::text
  --END as ttttest,
  CASE
  WHEN c.valueplan=0 THEN 0
  ELSE c.valueplan
  END,
  CASE
  WHEN c.valuereal=0 THEN 0
  ELSE c.valuereal
  END,
  (c.valuereal - c.valueplan) as otklonenie,
  CASE
  WHEN c.valueplan=0 THEN 0
  ELSE ((c.valuereal - c.valueplan)/c.valueplan*100) --abs
  END as procent_otkl,
  --c.datetimestart as year,
  --c.datetimeend as month
  to_char(c.dateTimeStart, 'YYYY') || ' ' || to_char(c.dateTimeStart, 'TMMonth') as date
  from companyObject co1
   INNER JOIN companyObject co2 
    ON co1.treeId = text2ltree(substring(ltree2text(co2.treeId) from '.*(?=\\.\\d?)')) AND co1.treeId = text2ltree('1')
   LEFT JOIN companyObject co3 
    ON co2.treeId = text2ltree(substring(ltree2text(co3.treeId) from '.*(?=\\.\\d?)'))
   LEFT JOIN companyObject co4
    ON co3.treeId = text2ltree(substring(ltree2text(co4.treeId) from '.*(?=\\.\\d?)'))

   -- провайдеры
   INNER JOIN (select distinct on (c.providerhotId, c.providerhotsystemid, p.providerId, p.systemId ) c.providerhotId, c.providerHotSystemId, c.providerWaterSystemId, c.providerWaterId, p.title 
     from cost c
     INNER JOIN provider p ON p.providerId = c.providerWaterId and p.systemId = c.providerWaterSystemId) pp
   ON pp.providerhotId = co4.companyObjectId and pp.providerHotSystemId = co4.systemId

   -- статьи
   INNER JOIN (select distinct on (c.providerhotId, c.providerhotsystemid, ct.costTypeId, ct.title)
   c.providerhotId, c.providerhotsystemid, ct.costTypeId, ct.title, ct.treeId
     from cost c
     INNER JOIN costType ct ON ct.costTypeId = c.costTypeId) ct
   ON ct.providerhotId = co4.companyObjectId and ct.providerHotSystemId = co4.systemId
   
   INNER JOIN cost c 
    ON c.providerHotId = co4.companyObjectId and c.providerHotSystemId = co4.systemId and 
      (c.costTypeId = ct.costTypeId) AND
      c.providerWaterSystemId = pp.providerWaterSystemId and c.providerWaterId = pp.providerWaterId

   WHERE co4.title is not null
   --ORDER BY co4.companyObjectId, ct.treeId
  UNION
  --список ЦТП сверху вниз
  SELECT
    co1.title as company,
    co2.title as fil,
    co3.title as tr,
    co4.title as kotel,
    co5.title as tstp,
    pp.title,
    --ct1.title || '.' || ct2.title || '.' || ct3.title || '.' ||  ct4.title-- || '.' || ct5.title --|| '.' || ct6.title--,
    ltree2text(ct.treeId) || ' ' || GetCostTypeFullTitle(ct.costTypeId) as costTypeTitleFullPath, -- выводить полный путь!
    --ct.treeId,
    --CASE
    --WHEN c.valueplan=0 THEN ''
    --ELSE cast(c.valueplan as text) || ' ' || cast(c.valuereal as text) || ' ' || cast((c.valuereal - c.valueplan) as text) || ' ' || cast(((c.valuereal - c.valueplan)/c.valueplan*100) as text)
    --END as ttttest,
    CASE WHEN c.valueplan=0 THEN 1 ELSE c.valueplan END,
    CASE WHEN c.valuereal=0 THEN 1 ELSE c.valuereal END,
    (c.valuereal - c.valueplan) as otklonenie,
    CASE WHEN c.valueplan=0 THEN 0 ELSE ((c.valuereal - c.valueplan)/c.valueplan*100) END as procent_otkl,
    --c.datetimestart as year,
    --c.datetimeend as month
    to_char(c.dateTimeStart, 'YYYY') || ' ' || to_char(c.dateTimeStart, 'TMMonth') as date
  FROM companyObject co1
   INNER JOIN companyObject co2 
    ON co1.treeId = text2ltree(substring(ltree2text(co2.treeId) from '.*(?=\\.\\d?)')) AND co1.treeId = text2ltree('1')
   LEFT JOIN companyObject co3 
    ON co2.treeId = text2ltree(substring(ltree2text(co3.treeId) from '.*(?=\\.\\d?)'))
   LEFT JOIN companyObject co4
    ON co3.treeId = text2ltree(substring(ltree2text(co4.treeId) from '.*(?=\\.\\d?)'))
   LEFT JOIN companyObject co5
    ON co4.treeId = text2ltree(substring(ltree2text(co5.treeId) from '.*(?=\\.\\d?)'))

   -- провайдеры
   INNER JOIN (select distinct on (c.providerhotId, c.providerhotsystemid, p.providerId, p.systemId ) c.providerhotId, c.providerHotSystemId, c.providerWaterSystemId, c.providerWaterId, p.title 
     from cost c
     INNER JOIN provider p ON p.providerId = c.providerWaterId and p.systemId = c.providerWaterSystemId) pp
   ON pp.providerhotId = co5.companyObjectId and pp.providerHotSystemId = co5.systemId

   -- статьи
   INNER JOIN (select distinct on (c.providerhotId, c.providerhotsystemid, ct.costTypeId, ct.title)
   c.providerhotId, c.providerhotsystemid, ct.costTypeId, ct.title, ct.treeId
     from cost c
     INNER JOIN costType ct ON ct.costTypeId = c.costTypeId) ct
   ON ct.providerhotId = co5.companyObjectId and ct.providerHotSystemId = co5.systemId
   
   INNER JOIN cost c 
    ON c.providerHotId = co5.companyObjectId and c.providerHotSystemId = co5.systemId and 
      (c.costTypeId = ct.costTypeId) AND
      c.providerWaterSystemId = pp.providerWaterSystemId and c.providerWaterId = pp.providerWaterId

   WHERE co5.title is not null;