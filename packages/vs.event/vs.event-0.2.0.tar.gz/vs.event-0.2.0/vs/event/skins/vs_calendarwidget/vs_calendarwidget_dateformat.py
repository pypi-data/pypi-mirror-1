language = context.REQUEST.LANGUAGE
if language == 'de':
    return '%d.%m.%Y'
return '%Y/%m/%d'
