from datetime import datetime

def transform_datetime(dt):
    """ converts datetime parameter"""                               

    if dt is None:
        dt = ''
    else:
        assert isinstance(dt, datetime)
        dt = dt.strftime('%Y-%m-%d %H:%M:%S')
 
    return dt