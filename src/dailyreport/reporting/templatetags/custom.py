# -*- coding: utf-8 -*-
from django import template

register = template.Library()

def percent(fact, plan):
    if plan == 0.0:
        if fact > 0.0:
            return 100.0
        else:
            return 0.0

    return ((fact-plan)/plan)*100

def deviation(value, field):
    if value==None or field==None:
        return ""
    try:
        fact = plan=""
        diff = 0.0
        
        if field == 'fuel_diff_day':
            fact = value['fuel_actual_day']
            plan = value['real_plan_day']
            diff = percent(float(fact),float(plan))
        elif field =='fuel_diff_month':
            fact = value['fuel_actual_month']
            plan = value['real_plan_sum']
            diff = percent(float(fact),float(plan))
        elif field == 'water_diff_day':
            fact = value['water_actual_day']
            plan = value['water_plan_day']
            diff = percent(float(fact),float(plan))
        elif field == 'water_diff_month':
            fact = value['water_actual_month']
            plan = value['water_plan_month']
            diff = percent(float(fact),float(plan))
        elif field == 'elec_diff_period_percent':
            diff = value['elec_diff_period_percent']
            
        #diff = percent(float(fact),float(plan))
        if diff < 1 and diff > 0:
            return "reddish"
        elif diff >=1 and diff<=5:
            return "brown"     
        elif diff >5:
            return "red"
        return ""
    except Exception as ex:
        return ""

def colorize(value):
    #print value
    if value==None:
        return ""
    try:
        p1 = deviation(value,'fuel_diff_day')
        p2 = deviation(value,'fuel_diff_month')
        p3 = deviation(value,'water_diff_day')
        p4 = deviation(value,'water_diff_month')
        p5 = deviation(value,'elec_diff_period_percent')
        p = [p1,p2,p3,p4,p5]

        if "red" in p:
            return "red"
        elif "brown" in p:
            return "brown"
        elif "reddish" in p:
            return "reddish"
        return ""
    except Exception as ex:
        return ""
def float_delimeter(value, field):
    try:
        if value == None:
            return 0.0
        if type(value).__name__== 'float':
            return unicode(value).replace('.', field)
        else:
            return value.replace('.', field)
    except:
        return value

register.filter('float_delimeter',float_delimeter)
register.filter('deviation', deviation)    
register.filter('colorize', colorize)
    