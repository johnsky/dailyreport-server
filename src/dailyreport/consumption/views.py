# -*- coding: utf-8 -*-

from jsonrpc import jsonrpc_method
from django.core import serializers
from dailyreport.fuel.models import FuelInfo
from dailyreport.water.models import WaterConsumptionCategory
from dailyreport.company_object.models import BoilerHouse
from django.conf import settings
import traceback
import sys
import logging
from dailyreport.utils import qooxdoo_utils

_logger = logging.getLogger(__name__)

@jsonrpc_method('consumption.getFuelInfoByBoilerId', authenticated=True, safe=False)
def get_fuel_info_by_boiler(request, boiler_id):
    """
    Получить список расходов топлива для котельной.
    @param boiler_id: идентификатор котельной
    
    @return: список расхожов топлива для котельной 
    """

    return serializers.serialize("json", FuelInfo.objects.filter(boiler__id=boiler_id))
    
@jsonrpc_method('consumption.saveFuelInfo', authenticated=True, safe=False)
def save_fuel_info(request, fuel_infos):
    """
    Получить список расходов топлива для котельной.
    @param boiler_id: идентификатор котельной
    
    @return: список расхожов топлива для котельной 
    """
    try:
        _logger.debug(u"Сохранение информации о топливе для котельной: " + unicode(fuel_infos))
        for fuel_info in fuel_infos:
            if qooxdoo_utils.get_item(fuel_info, 'id') == 0:
                info = FuelInfo()
                info.active = True
                info.type = qooxdoo_utils.get_item(fuel_info,'type')
                info.creator = request.user
                info.boiler = BoilerHouse.objects.get(id= qooxdoo_utils.get_item(fuel_info,'companyObject','id'))
                info.save(save_revision=True)
            else:
                info = FuelInfo.objects.get(id=qooxdoo_utils.get_item(fuel_info, 'id'))
                info.active = qooxdoo_utils.get_item(fuel_info, 'active')
                info.type = qooxdoo_utils.get_item(fuel_info,'type')
                info.save(save_revision=True)

    except Exception as ex:
        traceback.print_exc(file=sys.stdout)
        logging.getLogger(__name__).error(ex)
        return {'success' : False}
    
    return {'success' : True}

@jsonrpc_method('consumption.getWaterCategoryByBoilerId', authenticated=True, safe=False)
def get_water_catgory_by_boiler(request, boiler_id):
    """
    Получить список категоий воды для котельной.
    @param boiler_id: идентификатор котельной
    
    @return: список категорий воды 
    """
    return serializers.serialize("json", WaterConsumptionCategory.objects.filter(boiler__id=boiler_id))

@jsonrpc_method('consumption.saveWaterCategory', authenticated=True, safe=False)
def save_water_category(request, water_categories):
    """
    Получить список расходов топлива для котельной.
    @param boiler_id: идентификатор котельной
    
    @return: список расхожов топлива для котельной 
    """
    print water_categories
    for water_category in water_categories:
        if qooxdoo_utils.get_item(water_category, 'id') == 0:
            category = WaterConsumptionCategory()
            category.active = True
            category.name = qooxdoo_utils.get_item(water_category,'name')
            category.creator = request.user
            category.boiler = BoilerHouse.objects.get(id=qooxdoo_utils.get_item(water_category,'companyObject','id'))
            category.save(save_revision=True)
        else:
            category = WaterConsumptionCategory.objects.get(id=qooxdoo_utils.get_item(water_category,'id'))
            category.active = qooxdoo_utils.get_item(water_category,'active')
            category.name = qooxdoo_utils.get_item(water_category, 'name')
            category.save(save_revision=True)
            
    return {'success' : True}