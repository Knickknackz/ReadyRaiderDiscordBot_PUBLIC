"""
Used to contain more global Functions, should probably move this
"""
def search_format(key, cType, value):
    """
    returns API Search Constraint Format
    :param key:
        API Key
    :param cType:
        API Constraint Type
    :param value:
        API Value
    :return:
        String that represents search format
    """
    return '{"key": "'+str(key)+'", "constraint_type":"'+str(cType)+'", "value":"' + str(value) + '"}'