from gam_app.models import *
from django.db.models import Q
import time
from gam_app import generate_keywords_from_statement_list

from itertools import chain


def advanced_search(request):

    # right now it looks like [Iraq-Any Field-Iran-OR-Keyword-]
    # so we split on - and delete the last one (there is always a tailing empty list
    request_list = request.GET["full_info"].split("-")[:-1]

    # request list needs to be split into threes
    # right now it looks like ['Iraq','','Any Field', 'Iran', 'OR', 'Keyword,...]
    # note that the first one will not have the logical operator
    start = time.time()
    formatted_request_list = []
    ticker = 1
    three_pair = {}
    for item in request_list:
        if ticker == 1:
            three_pair["search_string"] = item.strip()
        elif ticker == 2:
            three_pair["logic"] = item.strip()
        elif ticker == 3:
            three_pair["field"] = item.strip()
            formatted_request_list.append(three_pair)
            three_pair = {}
            ticker = 0  # set to zero since we are going inc after
        ticker += 1

    query = False
    for request_part in formatted_request_list:
        search_string = request_part["search_string"]
        logic = request_part["logic"]
        field = request_part["field"]

        queryset = make_queryset(search_string, field)

        if query and queryset:
            if logic == "AND":
                query = query & queryset
            elif logic == "OR":
                query = query | queryset
            elif logic == "NOT":
                query = query - queryset
        elif queryset:
            query = queryset
        else:
            return False

    result_list = list(query)
    # print('result', result_list)
    q_time = time.time() - start
    print("generating result_list took %s seconds" % q_time)
    # print(result_list)
    # print("testo", Imagen.objects.filter(persona__nombre_de_la_persona__icontains="Manuel"))
    context = {
        'results': result_list,
        'search': search_string,
        'full_info': request.GET["full_info"],
        'num_results': len(result_list),
    }
    return context


def make_queryset(search_string, field):  # this will return queryset in SET
    if field == "Cualquier Campo":
        # return Persona, Lugar, and Imagen objects.
        q1 = set(
            Persona.objects.filter(
                Q(nombre_de_la_persona__icontains=search_string)
                | Q(género__icontains=search_string)
                | Q(etnicidad__icontains=search_string)
            )
        )
        q2 = set(Lugar.objects.filter(nombre_del_lugar__icontains=search_string))
        # it is still a question whether there is a need to return Imagen objects
        q3 = set(
            Imagen.objects.filter(
                Q(texto_de_OCR__icontains=search_string)
                | Q(notas__icontains=search_string)
            )
        )
        queryset = q1 | q2 | q3
        # print('queryset', queryset)
    elif field == 'Persona':
        q1 = set(Persona.objects.filter(nombre_de_la_persona__icontains=search_string))
        # q2 = set(Imagen.objects.filter(Q(texto_de_OCR__icontains=search_string) | Q(traducción__icontains=search_string)))
        queryset = q1  # | q2
        # print('queryset', queryset)
    elif field == 'Ubicación Geográfica':
        q1 = set(Lugar.objects.filter(nombre_del_lugar__icontains=search_string))
        # q2 = set(Imagen.objects.filter(Q(texto_de_OCR__icontains=search_string) | Q(traducción__icontains=search_string)))
        queryset = q1  # | q2
        # print('queryset', queryset)
    elif field == 'Género':
        queryset = set(Persona.objects.filter(género__icontains=search_string))
        # print('queryset', queryset)
    elif field == 'Etnicidad':
        queryset = set(Persona.objects.filter(etnicidad__icontains=search_string))
        # print('queryset', queryset)
    else:
        print("Found an invalid field.")
        print("If you've just updated the field options dropdown,")
        return False
    return queryset


def make_query_part(search_string, field):
    print(field)
    if field == "Cualquier Campo":
        query_part = Q(
            # Q(persona__nombre_de_la_persona__icontains=search_string) |
            # Q(carpeta__descripción__icontains=search_string) |
            Q(ubicación_geográfica__nombre_del_lugar__icontains=search_string)
            | Q(género__icontains=search_string)
            | Q(etnicidad__icontains=search_string)
            | Q(texto_de_OCR__icontains=search_string)
        )
    elif field == 'Persona':
        query_part = Q(persona__nombre_de_la_persona__icontains=search_string)
    elif field == 'Ubicación Geográfica':
        query_part = Q(ubicación_geográfica__nombre_del_lugar__icontains=search_string)
    elif field == 'Género':
        query_part = Q(género__icontains=search_string)
    elif field == 'Etnicidad':
        query_part = Q(etnicidad__icontains=search_string)
    elif field == 'Texto':
        query_part = Q(texto_de_OCR__icontains=search_string)
    else:
        print("Found an invalid field.")
        print("If you've just updated the field options dropdown,")
        print("go and update 'make_query_part' in 'advanced_search.py'")
        return False
    return query_part


# used for filtering
def advanced_search_make_query(request):
    request_list = request.GET["full_info"].split(",")

    # request list needs to be split into threes
    # right now it looks like ['Iraq','','Any Field', 'Iran', 'OR', 'Keyword,...]
    # note that the first one will not have the logical operator
    formatted_request_list = []
    ticker = 1
    three_pair = {}
    for item in request_list:
        if ticker == 1:
            three_pair["search_string"] = item
        elif ticker == 2:
            three_pair["logic"] = item
        elif ticker == 3:
            three_pair["field"] = item
            formatted_request_list.append(three_pair)
            three_pair = {}
            ticker = 0  # set to zero since we are going inc after
        ticker += 1

    query = []
    for request_part in formatted_request_list:
        search_string = request_part["search_string"]
        logic = request_part["logic"]
        field = request_part["field"]
        query_part = make_query_part(search_string, field)
        if query and query_part:
            if logic == "AND":
                query = query & query_part
            elif logic == "OR":
                query = query | query_part
            elif logic == "NOT":
                query = query & ~query_part
        elif query_part:
            query = query_part
        else:
            return False

    return query
