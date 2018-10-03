import re


def parser_0(message):
    parsed = re.findall(r"((\d+(,\d+)?)(?= reais))", message, re.I)
    if parsed:
        return int(re.findall(r'\d{1,2}', str(parsed[0][0]))[0])
    return None


def parser_1(message):
    parsed = re.findall(r"(?<=\$)((\s+)?\d+)", message, re.I)
    if parsed:
        return int(re.findall(r'\d{1,2}', str(parsed[0][0]))[0])
    return None


def parser_2(message):
    parsed = re.findall(r"((\d+(,\d+)))", message, re.I)
    if parsed:
        return int(re.findall(r'\d{1,2}', str(parsed[0][0]))[0])
    return None


def find_price(item):
    message = item['message']
    message
    for i in range(3):
        parser = f"parser_{i}(message)"
        r = eval(parser)
        if r is not None:
            return r
    return None
