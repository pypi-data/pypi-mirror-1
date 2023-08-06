from sqlalchemy.orm.exc import NoResultFound

def get_or_create(model, **kwargs):
    try:
        return model.query.filter_by(**kwargs).one()
    except NoResultFound:
        return model(**kwargs)

def make_list(str_or_list):
    '''Makes list from a string or passes argument as is.'''
    if isinstance(str_or_list, basestring):
        return [str_or_list,]
    return str_or_list

