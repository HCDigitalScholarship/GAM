from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers

from gam_app.models import *
from acceso.models import *
from gam_app.models import Persona
import os
import random

def random_photo():
    photos = os.listdir('/srv/GAM/acceso/static/pat_goudvis')
    photo = random.choice(photos)
    return photo

def main(request):
    casos = Caso.objects.all()
    filters = Filtros.objects.all()
    filter_list = []
    for filter in filters:
        filter_list.append(filter.nombre_del_filtro)
    photo_list = []
    for caso in casos:
        photo_list.append(caso.fotos.first())

    photo = random_photo()
    #print('casos:  ', casos)
    context = {'casos': casos, 'photo_list': photo_list, 'filter_list':filter_list, 'photo': photo}
    return render(request, 'acceso/index.html', context)


def about(request):
    photo = random_photo()
    return render(request, 'acceso/about.html', {'photo':photo})


def map(request):
    photo = random_photo()
    return render(request, 'acceso/map.html', {'photo':photo})


def history(request):
    photo = random_photo()
    return render(request, 'acceso/history.html', {'photo':photo})


def caso(request, caso):
    caso = Caso.objects.get(slug_name=caso)
    #caso = CasoFilter(request.GET, queryset=Caso.objects.get(slug_name=caso))
    foto = []
    dragon = []
    imageprofile = caso.foto_de_perfil


    for x in caso.carpetas.all():
        dragon = Imagen.objects.filter(
            archivo=x.archivo,
            colección=x.colección,
            caja=x.caja,
            legajo=x.legajo,
            carpeta=x.carpeta,
        ).order_by('número_de_imagen')

    persona = Persona.objects.get(nombre_de_la_persona=caso)
    info = [persona.nombre_de_la_persona, persona.nombre, persona.segundo, persona.apellido_paterno, persona.apellido_materno, persona.fecha_de_nacimiento, persona.fecha_desaparicion, persona.edad_en_el_momento, persona.género, persona.etnicidad, persona.profesión, persona.actividades_políticas]
    for x in caso.fotos.all():
        foto.append(x)
    profile_photos = Foto.objects.filter(caso__slug_name=caso)
    context = {'caso': caso, 'images': foto,'info': info, 'dragon': dragon, 'face':imageprofile}

    return render(request, 'acceso/caso.html', context)


def simple(request):
    casos = Caso.objects.all()
    context = {'casos': casos}
    return render(request, 'simple/acceso.html', context)


def caso_index(request):
    return render(request, 'acceso/caso_index.html')


def caso_table(request, caso_id):
    # TODO: Probably want nombre_del_caso to be an explicit part of the URL rather than
    # a GET parameter.
    caso = Caso.objects \
        .filter(nombre_del_caso__icontains=request.GET.get('nombre_del_caso')) \
        .filter(descripción__icontains=request.GET.get('descripción'))
    return JsonResponse(serializers.serialize(caso))
