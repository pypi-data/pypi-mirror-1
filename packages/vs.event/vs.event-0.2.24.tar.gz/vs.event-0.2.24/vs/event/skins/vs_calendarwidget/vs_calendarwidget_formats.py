##parameters=language=None

if not language:
    language = context.REQUEST.LANGUAGE

european_fmt = dict(python_fmt='%d.%m.%Y',
                    jquery_fmt='dd.mm.yy')

us_fmt = dict(python_fmt='%Y/%m/%d',
              jquery_fmt='yy/mm/dd')

language_mapping = {
    'de' : european_fmt,
    'at' : european_fmt,
    'ch' : european_fmt,
    'en' : us_fmt,
}

return language_mapping.get(language, us_fmt)

