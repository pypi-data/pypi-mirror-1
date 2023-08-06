##parameters=date, with_time=0, ignore_unset_time=0

format = context.vs_calendarwidget_formats()['python_fmt']

try:
    if with_time and not (ignore_unset_time and date.TimeMinutes() == '00:00'):
        format += ' %H:%Mh' 
    return date.strftime(format)
except:
    return ''
