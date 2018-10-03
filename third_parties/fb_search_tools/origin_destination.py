from search.finder import SynonymFinder
import re


def synonym_map():
    return SynonymFinder().get_synonym_map()


def find_origin_destination(item):
    message = item['message']
    origin = None
    destination = None

    for query, synonym in synonym_map().items():
        found = re.search(query, message)
        if found:
            # Se achou algo
            if origin is None:
                # Define origin se não encontrou
                origin = (synonym, found.start())
            elif origin[0] != synonym:
                # Se origin já foi encontrada e o destino é diferente da origem
                destination = (synonym, found.start())

                # Troca os dois se origin está depois de synonym
                if destination[1] < origin[1]:
                    origin, destination = destination, origin
                return origin[0], destination[0]
    return None
