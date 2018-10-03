
import logging

_logger = logging.getLogger(__name__)

def validation(dataset_field, value):
    """
    Валидация значения модели.
    
    @param model_ct: Тип контента модели
    @param field:  Поле модели
    """
    
    try:
        # Вода, фактическое суточное потребление
        if dataset_field.model_content_type.app_label == 'water' and  \
            dataset_field.model_content_type.model == 'waterconsumption' and dataset_field.model_field_name == 'actual_day':
            pass
            
        # Топливо, фактическое потребление
        if model_ct.app_label == 'fuel' and model_ct.model == 'fuelconsumption' and field == 'actual_day':
            pass
        
    except Exception as ex:
        _logger.error(ex)
    
    return False