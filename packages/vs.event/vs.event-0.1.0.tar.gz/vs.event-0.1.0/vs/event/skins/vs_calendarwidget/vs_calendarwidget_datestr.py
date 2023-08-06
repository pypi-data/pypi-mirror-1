##parameters=date, format='%d.%m.%Y', with_time=0, ignore_unset_time=0

try:
    if with_time and not (ignore_unset_time and date.TimeMinutes() == '00:00'):
        format += ' %H:%Mh' 
    return date.strftime(format)
except:
    return ''
