# -*- coding: utf-8 -*-

import datetime
import time
import calendar
import pytz
from django.conf import settings
from dateutil.parser import parse

def get_now():
    return datetime.datetime.now()

def get_today():
    now = datetime.date.today()
    return now

def current_day():
    """
    Текущий день
    """
    now = datetime.datetime.now()
    return now.day

def current_year():
    """
    Текущий год
    """
    now = datetime.datetime.now()
    return now.year

def current_month():
    """
    Текущий месяц
    """
    now = datetime.datetime.now()
    return now.month
    
def current_hour():
    now = datetime.datetime.now()
    return now.hour

def get_month_day(date, day):
    """
    Возвращает день месяца указанной даты
    """
    _day = datetime.date(date.year, date.month, day)
    return _day

def get_range(date, day_shift=0):
    """
    Дата в диапазоне с первого числа месяца даты до предыдущего дня указанной даты
    """
    start_date = datetime.date(date.year, date.month, 1)
    _day = date.day+day_shift
    end_date = datetime.date(date.year, date.month, _day)
    return (start_date, end_date)

def get_range_revers(date):
    """
    Диапазон дат с даты и до конца месяца
    """
    last_day = get_month_last_day(date)
    end_date = datetime.date(date.year, date.month, last_day)
    
    return (date, end_date)
    

def get_period_dates(start, end):
    """
    Возвращает список дат периода
    """
    date_list = []
    days = (end - start).days
   
    date_list = [ start + datetime.timedelta(days=x) for x in range(0,days+1) ]
    return date_list

def get_month_range(year, month):
    """
    Возвращает диапазон начала и окончания месяца
    """
    day = calendar.monthrange(year, month)
    
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, day[1])
    
    return (start_date, end_date) 

def get_month_last_day(date):
    day = calendar.monthrange(date.year, date.month) 
    return day[1]


def contains(period, date):
    """
    Период содержит дату
    @param period: Период (start, end)
    @param date: Дата
    """
    #print "PERIOD CONTAINS" + unicode(period) + unicode(date) + " - " + unicode(period[0] <= date and period[1] >= date)
    
    if period[0] <= date and period[1] >= date:
        return True
    else:
        return False

def string_to_datetime(datetime_string, timezone=pytz.utc, format='%Y-%m-%dT%H:%M:%S.000Z'):
    """
    """
    #app_timezone = pytz.timezone(settings.TIME_ZONE)
    
    #year,month,day,hour,min,sec,weekday,yearday = time.strptime(datetime_string, format)[0:8]
    #localized = timezone.localize(datetime.datetime(year,month,day,hour,min,sec))
    
    #date_time = localized.astimezone(app_timezone)
    return parse(datetime_string)
    
    #return date_time

def string_to_date(datetime_string, timezone = pytz.utc):
    """
    Преобразовать строку даты определенной зоны. По умолчанию
    дата в UTC.
    """
    date_time = string_to_datetime(datetime_string, timezone)
    return date_time.date()

def string_to_date2(str_date):
    y,m,d = time.strptime(str_date, "%Y-%m-%d")[0:3]
    date = datetime.date(y,m,d)
    return date
