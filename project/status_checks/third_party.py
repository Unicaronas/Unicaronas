from watchman.decorators import check


@check
def _caronas_unicamp():
    return {'Caronas Unicamp': {'ok': True}}


@check
def _blablacar():
    return {'API': {'ok': True}}


def facebook():
    return {'Facebook Groups': [_caronas_unicamp()]}


def blablacar():
    return {'BlaBlaCar': [_blablacar()]}
