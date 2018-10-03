# -*- coding: utf-8 -*-

import logging
from jsonrpc import jsonrpc_method
from dailyreport.company_object.utils import get_boilers
from dailyreport.water.models import WaterConsumption, WaterConsumptionCategory
from dailyreport.water.water_utils import get_common_category_name

_logger = logging.getLogger(__name__)

@jsonrpc_method('water.getActualFromPlanValueDeviation', authenticated=True, safe=False)
def get_acutual_plan_value_deviation(request, company_objects, bookmarks,
                                     from_date, to_date, aggregation_type):
    """
    Получить данные по отклонению фактического значения от планового.
    @param company_objects: выбранные объекты
    @param bookmarks:
    @param from_date: 
    @param to_date:
    @param aggregation_type: Указывает то, как аггрегировать данные. Возможны следующие варианты: 
                            'enterprise' - по всему предприятию
                            'branch'     - по филиалам
                            'thermal'    - по тепловым районам 
                            None         - не выполнять аггрегации
    
    """
    try:
        if aggregation_type not in ['enterprise','thermal','branch',None]:
            raise ValueError(u"Неизвестный тип аггрегации")
        
        data = []
        boilers = get_boilers(request.user, company_objects, bookmarks)
        common_categoty_name = get_common_category_name()
        
        data = WaterConsumption.objects.get_consumption_data(boilers, from_date, to_date, aggregation_type)
        
        return data
    except Exception as ex:
        _logger.error(ex)
        raise ex
    
