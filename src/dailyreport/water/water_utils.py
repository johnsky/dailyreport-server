# -*- coding: utf-8 -*-
from dailyreport.water.models import WaterConsumptionCategory, WaterConsumption,\
    WaterConsumptionPeriodic

WATER_CATEGORY_NAMES=(u"Общий расход",
                        u"На выработку тепла",
                        u"На собственные нужды теплоисточников",
                        u"На передачу тепловой энергии",
                        u"На передачу тепловой энергии",
                        u"Нормативная подпитка",
                        u"Сверхнормативная подпитка",
                        u"Реализовано потребителям",
                        u"Реализовано для ГВС",
                        u"Реализовано подпиточной воды",
                        u"Население",
                        u"Бюджетные организации",
                        u"Местный бюджет",
                        u"Краевой бюджет",
                        u"Федеральный бюджет",
                        u"Прочие потребители",
                        u"Передано другим структурным подразделениям",
                        u"Водоотведение от теплоисточников",
                        u"Водостнабжение филиала",
                        u"Водоотведение от хозбытовых нужд филиала")

WATER_CATEGORY_STRUCTURE={ u"Общий расход": [
                         { u"На выработку тепла": [
                             u"На собственные нужды теплоисточников",
                             {u"На передачу тепловой энергии": [
                                u"Нормативная подпитка",
                                u"Сверхнормативная подпитка",
                              ]}
                         ]},
                         {u"Реализовано потребителям": [
                            {u"Население": [ 
                                u"Реализовано для ГВС",
                                u"Реализовано подпиточной воды",
                            ]},
                            {u"Бюджетные организации": [
                                {u"Местный бюджет": [
                                    u"Реализовано для ГВС",
                                    u"Реализовано подпиточной воды",]},
                                {u"Краевой бюджет": [
                                    u"Реализовано для ГВС",
                                    u"Реализовано подпиточной воды",]},
                                {u"Федеральный бюджет": [
                                    u"Реализовано для ГВС",
                                    u"Реализовано подпиточной воды",]}                     
                            ]},
                            {u"Прочие потребители": [
                                u"Реализовано для ГВС",
                                u"Реализовано подпиточной воды",                   
                            ]}
                         ]},
                         u"Передано другим структурным подразделениям",
                         u"Водоотведение от теплоисточников",
                         u"Водостнабжение филиала",
                         u"Водоотведение от хозбытовых нужд филиала"
                     ]}


def get_common_category_name():
    """
    Получить категорию расхода воды "Общий расход"
    """
    return WATER_CATEGORY_STRUCTURE.keys()[0]

def create_categories(node, user, boiler, parent_category=None):
    """
    @param node: Либо строка имени узла, либо словарь с ключем-именем
                 узла и массивом имен узлов.
    """
    if type(node) is dict:
        parent_name = node.keys()[0]
        parent, created = WaterConsumptionCategory.objects.get_or_create(name = parent_name, creator=user, boiler=boiler, parent = parent_category)

        for child_node in node[parent_name]:
            create_categories(child_node, user, boiler, parent)
    else:
        sub_category, created = WaterConsumptionCategory.objects.get_or_create(name = node, creator=user, boiler=boiler, parent = parent_category)
        
def initialize_water_categories(creator, boiler):
    """
    Создает категорию расхода воды
    
    Общий расход
        1. На выработку тепла
            1.1 На собственные нужды теплоисточников
            1.2 На передачу тепловой энергии
                1.2.1 Нормативная подпитка
                1.2.2 Сверхнормативная подпитка
        2. Реализовано потребителям
            2.1 Реализовано для ГВС
            2.2 Реализовано подпиточной воды
            2.3 Население
                2.3.1 Реализовано для ГВС
                2.3.2 Реализовано подпиточной воды
            2.4 Бюджетные организации
                2.4.1 Реалзовано для ГВС
                2.4.2 Реализовано подпиточной воды
                2.4.3 Местный бюджет
                    2.4.3.1 Реализовано для ГВС
                    2.4.3.2 Реализовано подпиточной воды
                2.4.4 Краевой бюджет
                    2.4.4.1 Реализовано для ГВС
                    2.4.4.2 Реализовано подпиточной воды
                2.4.5 Федеральный бюджет
                    2.4.5.1 Реализовано для ГВС
                    2.4.5.2 Реализовано подпиточной воды
            2.5 Прочие потребители
                2.5.1 Реализовано для ГВС
                2.5.2 Реализовано подпиточной воды
        3. Передано другим структурным подразделениям
        4. Водоотведение от теплоисточников
        5. Водостнабжение филиала (АКБ, гаражи и т.д.)
        6. Водоотведение от хозбытовых нужд филиала
    """
    create_categories(WATER_CATEGORY_STRUCTURE, creator, boiler)

def update_category_data(category, date, period):
    """
    
    """
    WaterConsumption.objects.filter(category__id = category.id)
    WaterConsumptionPeriodic.objects.filter(category__id = category.id)
        
def update_parent_categories_data(category, date, period):
    """
    
    """
    if category.parent == None:
        pass
    else:
        WaterConsumptionPeriodic.objects.filter(category__id = category.id)
