from .models import *
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from gam_app import advanced_search_postgres
from django.template import RequestContext
from gam_app.forms import (
    EditForm,
    SearchForm,
    PortapapelesForm,
    CarpetaForm,
    PersonaAutoForm,
    LugarAutoForm,
    OrganizacionAutoForm,
    CarpetaPersonaForm,
)
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib.auth.models import User
from django.db.models import Count, Q


#  search engine dependencies
from dal import autocomplete

#  For Mission Control
from gam_app.tracking import getBags, getImportedBags

#  For CRUD
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from gam_app.forms import PersonaForm, LugarForm, OrganizaciónForm
from django.views import generic

#  For datatables server-side processing
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

# Create your views here.


def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        query = request.POST.get('search', None)
        if form.is_valid():
            state = Imagen.objects.filter(texto_de_OCR__icontains=query)
            context = {'state': state, 'form': form}
            return render(request, 'all_documents_page.html', context)
        else:
            print(form.errors)
    else:
        search = ""
        form = SearchForm(initial={'search': search})
    return render(request, 'index.html', {'form': form})


def search(request, query):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            state = Imagen.objects.filter(texto_de_OCR__icontains=query)
            context = {'state': state, 'form': form}
            return render(request, 'all_documents_page.html', context)
        else:
            print(form.errors)
    else:
        search = "Buscar..."
        form = SearchForm(initial={'search': search})
    return render(request, 'index.html', {'form': form})


@login_required
def track_bags(request):
    bags = getBags()
    imported_bags = getImportedBags()
    context = {'bags': bags, 'imported_bags': imported_bags}
    return render(request, 'track_bags.html', context)


@login_required
def mission_control(request):
    context = {}
    return render(request, 'mission_control2.html', context)


class ImagenListJson(BaseDatatableView):
    model = Imagen
    columns = ['localizacion_fisica', 'status', 'traducción']

    # define column names that will be used in sorting order is important and should be same as order of columns displayed by datatables.
    # For non sortable columns use empty value like ''
    order_columns = ['localizacion_fisica', 'status', 'traducción']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # we want to render 'traducción' as custom columns
        if column == 'traducción':
            if row.traducción == '':
                return escape('sin traducción')
            else:
                return escape('traducido')
        else:
            return super(ImagenListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(localizacion_fisica__icontains=search)
        return qs


class ImagenListDescJson(BaseDatatableView):
    model = Imagen
    columns = ['localizacion_fisica', 'texto_de_OCR']

    # define column names that will be used in sorting order is important and should be same as order of columns displayed by datatables.
    # For non sortable columns use empty value like ''
    order_columns = ['localizacion_fisica', 'texto_de_OCR']

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site and make it return huge amount of data
    max_display_length = 500

    def render_column(self, row, column):
        # we want to render 'traducción' as custom columns
        if column == 'localizacion_fisica':
            return format_html(
                "<a href='/imagen/{0}/{1}/{2}/{3}/{4}'>{1}/{2}/{3}/{4}</a>".format(
                    row.archivo,
                    row.colección,
                    row.caja,
                    row.legajo,
                    row.carpeta,
                    row.número_de_imagen,
                )
            )
        if column == 'texto_de_OCR':
            return format_html("<div align='left'>{0}</div>".format(row.texto_de_OCR))
        # else:
        #    return super(ImagenListDescJson, self).render_column(row, column)
        # return super(ImagenListDescJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(texto_de_OCR__icontains=search)
        return qs


class CarpetaListJson(BaseDatatableView):
    model = Carpeta
    columns = ['carpeta_titulo', 'person_status', 'place_status', 'organization_status']
    order_columns = [
        'carpeta_titulo',
        'person_status',
        'place_status',
        'organization_status',
    ]
    max_display_length = 500

    def render_column(self, row, column):
        # we want to render 'carpeta_titulo' as custom columns
        if column == 'carpeta_titulo':
            return format_html(
                "<a href='../procesamiento/{0}/{1}/{2}/{3}/{4}'>{1}/{2}/{3}/{4}</a>".format(
                    row.archivo, row.colección, row.caja, row.legajo, row.carpeta
                )
            )
        else:
            return super(CarpetaListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)
        if search:
            q = (
                Q(person_status__icontains=search)
                | Q(place_status__icontains=search)
                | Q(organization_status__icontains=search)
            )
            qs = qs.filter(q)

        return qs


class CarpetaListJson_Buscar(BaseDatatableView):
    model = Carpeta
    columns = ['carpeta_titulo', 'descripción']
    order_columns = ['carpeta_titulo', '']
    max_display_length = 500

    def render_column(self, row, column):
        # we want to render 'carpeta_titulo' as custom columns
        if column == 'carpeta_titulo':
            # return escape('{0}/{1}/{2}/{3}'.format(row.colección, row.caja, row.legajo, row.carpeta))
            return format_html(
                "<a href='../procesamiento/{0}/{1}/{2}/{3}/{4}'>{1}/{2}/{3}/{4}</a>".format(
                    row.archivo, row.colección, row.caja, row.legajo, row.carpeta
                )
            )
        if column == 'descripción':
            return format_html("<div align='left'>{0}</div>".format(row.descripción))

        # else:
        #    return super(CarpetaListJson_Buscar, self).render_column(row, column)

    def filter_queryset(self, qs):
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(descripción__icontains=search)
        return qs


def lugar(request, lugar):
    l_id = Lugar.objects.filter(nombre_del_lugar=lugar)
    for a in l_id:
        lugar_id = a.id
    lugar_id = lugar_id
    state = Imagen.objects.filter(ubicación_geográfica=lugar_id)
    context = {'state': state}
    return render(request, 'all_documents_page.html', context)


# For CRUDs
class ImageFieldAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated():
        #    return Imagen.objects.none()

        qs = Imagen.objects.all()

        if self.q:
            qs = qs.filter(localizacion_fisica__icontains=self.q)

        return qs


class PersonaCreate(CreateView):
    model = Persona
    form_class = PersonaForm


class PersonaUpdate(UpdateView):
    model = Persona
    form_class = PersonaForm


class PersonaDelete(DeleteView):
    model = Persona
    success_url = reverse_lazy('persona')


class PersonaDetailView(generic.DetailView):
    model = Persona


class LugarCreate(CreateView):
    model = Lugar
    form_class = LugarForm


class LugarUpdate(UpdateView):
    model = Lugar
    form_class = LugarForm


class LugarDelete(DeleteView):
    model = Lugar
    success_url = reverse_lazy('lugar')


class OrganizacionCreate(CreateView):
    model = Organización
    form_class = OrganizaciónForm


class OrganizacionUpdate(UpdateView):
    model = Organización
    form_class = OrganizaciónForm


class OrganizacionDelete(DeleteView):
    model = Organización
    success_url = reverse_lazy('organizacion')


# These are the views for the autocomplete fields in document_page.html
class PersonaNameLookup(autocomplete.Select2ListView):
    def create(self, text):
        return text

    def get_list(self):
        result_list = [model.nombre_de_la_persona for model in Persona.objects.all()]
        if self.q:
            data = Persona.objects.all().filter(nombre_de_la_persona__icontains=self.q)
            result_list = [model.nombre_de_la_persona for model in data]
        return result_list


class LugarNameLookup(autocomplete.Select2ListView):
    def create(self, text):
        return text

    def get_list(self):
        result_list = [model.nombre_del_lugar for model in Lugar.objects.all()]
        if self.q:
            data = Lugar.objects.all().filter(nombre_del_lugar__icontains=self.q)
            result_list = [model.nombre_del_lugar for model in data]
        return result_list


class OrganizacionNameLookup(autocomplete.Select2ListView):
    def create(self, text):
        return text

    def get_list(self):
        result_list = [
            model.nombre_de_la_organización for model in Organización.objects.all()
        ]
        if self.q:
            data = Organización.objects.all().filter(
                nombre_de_la_organización__icontains=self.q
            )
            result_list = [model.nombre_de_la_organización for model in data]
        return result_list


class autocompletar_manuscrito(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Manuscrito.objects.all()
        if self.q:
            qs = qs.filter(nombre_del_manuscrito__icontains=self.q)
        return qs


@login_required
def explorar(request):
    if request.user.is_staff:

        archives = Archivo.objects.all()
        collections = Imagen.objects.values(
            'archivo__nombre_del_archivo', 'colección__nombre_de_la_colección'
        ).distinct()
        for collection in collections:
            collection['descripción'] = get_object_or_404(
                Colección,
                nombre_de_la_colección=collection['colección__nombre_de_la_colección'],
            ).descripción

        # carpetas = Imagen.objects.values('archivo__nombre_del_archivo','colección__nombre_de_la_colección', 'caja', 'legajo', 'carpeta').distinct()
        carpetas = Carpeta.objects.all()
        #        print(carpetas)
        # for carpeta in carpetas:
        #    print(carpeta)
        #        carpeta['descripción'] = get_object_or_404(Carpeta, archivo=carpeta['archivo__nombre_del_archivo'], carpeta_no= carpeta['carpeta']).descripcion_caso

        context = {
            'archives': archives,
            'collections': collections,
            'carpetas': carpetas,
        }
        return render(request, 'personal_explorar.html', context)

    else:
        # TODO convert to return Items not images

        archives = Archivo.objects.all()
        collections = Imagen.objects.values(
            'archivo__nombre_del_archivo', 'colección__nombre_de_la_colección'
        ).distinct()
        for collection in collections:
            collection['descripción'] = get_object_or_404(
                Colección,
                nombre_de_la_colección=collection['colección__nombre_de_la_colección'],
            ).descripción

        # carpetas = Imagen.objects.values('archivo__nombre_del_archivo','colección__nombre_de_la_colección', 'caja', 'legajo', 'carpeta').distinct()
        #        carpetas  = Carpeta.objects.all()

        context = {
            'archives': archives,
            'collections': collections,
        }  # , 'carpetas':carpetas}
        return render(request, 'publico_explorar.html', context)

def bokeh(request):
    pass

def sobre(request):
    return render(request, 'about.html')


def über(request):
    return render(request, 'about.html')


def advanced_search_submit(request):
    context = advanced_search_postgres.advanced_search(request)
    if context:
        context['state'] = context['results']
        print(type(context['state']))
        # print(context)

        # to determine the number of returning objects for each model
        persona_count = 0
        lugar_count = 0
        imagen_count = 0

        persona = []
        lugar = []
        imagen = []

        for obj in context['results']:
            if isinstance(obj, Persona):
                persona_count += 1
                persona.append(obj)
            elif isinstance(obj, Lugar):
                lugar_count += 1
                lugar.append(obj)
            elif isinstance(obj, Imagen):
                imagen_count += 1
                imagen.append(obj)

        context['persona_count'] = persona_count
        context['lugar_count'] = lugar_count
        context['imagen_count'] = imagen_count

        context['persona'] = persona
        context['lugar'] = lugar
        context['imagen'] = imagen

        '''
        # wanted to provide relevant carpeta on the result page, but it seems this relationship is not used yet
        relevant_carpeta = []
        for obj in context['state']:
            print (type(obj))
            if obj.__class__.__name__ == 'Persona':
                relevant_carpeta.append(Carpeta.objects.filter(persona__nombre_de_la_persona=obj.nombre_de_la_persona))
            elif obj.__class__.__name__ == 'Lugar':
                relevant_carpeta.append(Carpeta.objects.filter(ubicación_geográfica__nombre_del_lugar = obj.nombre_del_lugar))
        context['relevant_resources'] = relevant_carpeta
        print (context['relevant_resources'])
        '''
        return render(request, 'search_result_page.html', context)
    else:
        context = {"failed": True}
        return render(request, 'no_results.html', context)
        # return redirect('index')
    # return render(request, 'index.html', context)


@login_required
def procesamiento(request, archivo, colección, caja, legajo, carpeta):
    state = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
        carpeta=carpeta,
    ).order_by('número_de_imagen')
    location = {
        'archivo': archivo,
        'colección': colección,
        'caja': caja,
        'legajo': legajo,
        'carpeta': carpeta,
    }
    possible_carpeta = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
    ).order_by('carpeta')
    carpeta_list = []
    current_carpeta = Carpeta.objects.get(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
        carpeta=carpeta,
    )
    carpeta_persona_form = CarpetaPersonaForm()

    # make a list of the possible carpetas with index values
    for index, page in enumerate(possible_carpeta):
        if page.carpeta not in carpeta_list:
            carpeta_list.append(page.carpeta)
    for item in carpeta_list:
        if item == carpeta:
            current = item
            print('current is', current)

    # find index in list for current
    index_current = carpeta_list.index(current)
    previous_carpeta = carpeta_list[index_current - 1]
    try:
        next_carpeta = carpeta_list[index_current + 1]
    except:
        next_carpeta = carpeta_list[0]

    carpeta_info = Caso.objects.filter(
        caja_no=caja, legajo_no=legajo, carpeta_no=carpeta
    )

    images_in_carpeta = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
        carpeta=carpeta,
    ).order_by('número_de_imagen')
    persona_auto_form = PersonaAutoForm(
        initial={'person_status': current_carpeta.person_status}
    )
    lugar_auto_form = LugarAutoForm()
    organizacion_auto_form = OrganizacionAutoForm()
    context = {
        'state': state,
        'persona_auto_form': persona_auto_form,
        'lugar_auto_form': lugar_auto_form,
        'organizacion_auto_form': organizacion_auto_form,
        'location': location,
        'previous_carpeta': previous_carpeta,
        'next_carpeta': next_carpeta,
        'carpeta_info': carpeta_info,
        'current_carpeta': current_carpeta,
        'carpeta_persona_form': carpeta_persona_form,
        'images_in_carpeta': images_in_carpeta,
    }

    if request.method == 'POST':
        if 'persona' in request.POST:
            persona_auto_form = PersonaAutoForm(request.POST)
            person_name = request.POST.get('nombre_de_la_persona', None)
            if persona_auto_form.is_valid():
                persona = Persona.objects.get_or_create(
                    nombre_de_la_persona=person_name
                )[0].pk
                context.update({'persona': persona})
        #            return redirect('/persona/{}/update/'.format(persona), target="_blank")
        #            return HttpResponseRedirect(reverse('persona_update',args=(persona,)))

        elif 'lugar' in request.POST:
            lugar_auto_form = LugarAutoForm(request.POST)
            place_name = request.POST.get('nombre_del_lugar', None)
            if lugar_auto_form.is_valid():
                lugar = Lugar.objects.get_or_create(nombre_del_lugar=place_name)[0].pk
                context.update({'lugar': lugar})

        elif 'organizacion' in request.POST:
            organizacion_auto_form = OrganizacionAutoForm(request.POST)
            organization_name = request.POST.get('nombre_de_la_organización', None)
            if organizacion_auto_form.is_valid():
                organizacion = Organización.objects.get_or_create(
                    nombre_de_la_organización=organization_name
                )[0].pk
                context.update({'organizacion': organizacion})

        elif 'carpeta_persona' in request.POST:
            carpeta_persona_form = CarpetaPersonaForm(
                request.POST or None,
                initial={'person_status': current_carpeta.person_status},
                instance=current_carpeta,
            )
            print(current_carpeta.person_status)
            print(type(current_carpeta.person_status))

            if carpeta_persona_form.is_valid():
                carpeta_persona_form.save()

        else:
            print(form.errors)

    return render(request, 'procesamiento.html', context)


# image view
@login_required
def documento5(request, archivo, colección, caja, legajo, carpeta, número_de_imagen):

    if request.method == 'POST':
        if request.POST['input'] == 'text_edit':
            edit_form = EditForm(request.POST)
            if edit_form.is_valid():
                print('this is the request', request)
                texto_de_OCR = request.POST['texto_de_OCR']
                print('*', texto_de_OCR)
                file = request.POST.get('nombre_del_archivo', None)
                persona = request.POST.get('persona', None)
                print('here is the persona')
                print(persona)
                archivo = get_object_or_404(
                    Archivo, nombre_del_archivo=request.POST.get('archivo', None)
                )
                archivo_id = archivo.id
                collection = get_object_or_404(
                    Colección,
                    nombre_de_la_colección=request.POST.get('colección', None),
                )
                box = request.POST.get('caja', None)
                bundle = request.POST.get('legajo', None)
                folder = request.POST.get('carpeta', None)
                old_text = request.POST.get('old_text', None)
                time = datetime.datetime.now()
                usuario_id = User.objects.get(username=request.user).pk
                carpeta_titulo = request.POST.get('carpeta_titulo', None)
                carpeta_descripción = request.POST.get('descripción', None)
                status = request.POST.get('status', None)
                print(carpeta_titulo, carpeta_descripción)
                # save previous text
                transcription = Transcrito(
                    usuario_id=usuario_id,
                    nombre_del_archivo=file,
                    tiempo_modificado=time,
                    texto_transcrito=old_text,
                )
                transcription.save()

                lugar = request.POST.get('ubicación_geográfica', None)
                actividades_políticas = request.POST.get('actividades_políticas', None)
                fecha_desaparicion = request.POST.get('fecha_desaparicion', None)
                genero = request.POST.get('genero', None)
                manuscritos = request.POST.get('manuscripts', None)
                # save with the new data
                image = Imagen.objects.get(nombre_del_archivo=file)
                try:
                    image.texto_de_OCR = texto_de_OCR
                except:
                    image.text_de_OCR = texto_de_OCR
                carpeta_query = Carpeta.objects.get(
                    archivo__nombre_del_archivo=archivo,
                    colección__nombre_de_la_colección=colección,
                    caja=caja,
                    legajo=legajo,
                    carpeta=carpeta,
                )
                carpeta_query.carpeta_titulo = carpeta_titulo
                carpeta_query.descripción = carpeta_descripción
                carpeta_query.save()

                try:
                    carpeta_form = CarpetaForm(
                        initial={
                            'descripción': carpeta_query.descripción,
                            'carpeta_titulo': carpeta_query.carpeta_titulo,
                        }
                    )
                except:
                    carpeta_form = ''

                image.status = status
                image.save()
                state = Imagen.objects.get(
                    archivo__nombre_del_archivo=archivo,
                    colección__nombre_de_la_colección=colección,
                    caja=caja,
                    legajo=legajo,
                    carpeta=carpeta,
                    número_de_imagen=número_de_imagen,
                )
                id = state.id
                possible_pages = Imagen.objects.filter(
                    archivo__nombre_del_archivo=state.archivo,
                    colección__nombre_de_la_colección=state.colección,
                    caja=state.caja,
                    legajo=state.legajo,
                    carpeta=state.carpeta,
                ).order_by('número_de_imagen')
                pages_list = []
                for index, page in enumerate(possible_pages):
                    pages_list.append(page)

                    # print(index, page)
                    if page == state:
                        print('current= ', page.número_de_imagen, index)
                        current = int(index)
                previous = pages_list[current - 1].número_de_imagen
                try:
                    next_one = pages_list[current + 1].número_de_imagen
                except:
                    next_one = pages_list[0].número_de_imagen
                total = len(possible_pages)
                current = current + 1
                print('previous= ', previous)
                print('next= ', next_one)
                images_in_carpeta = Imagen.objects.all().filter(
                    caja=caja, legajo=legajo, carpeta=carpeta
                )
                # state = Imagen.objects.get(archivo__nombre_del_archivo=archivo, colección__nombre_de_la_colección=colección, caja=caja, legajo=legajo, carpeta=carpeta, número_de_imagen=número_de_imagen)
                # context  = {'state':state, 'form':edit_form, 'carpeta_form':carpeta_form}
                context = {
                    'carpeta_form': carpeta_form,
                    'state': state,
                    'form': edit_form,
                    'id': id,
                    'current': current,
                    'total': total,
                    'previous': previous,
                    'next_one': next_one,
                    'images_in_carpeta': images_in_carpeta,
                }

                return render(request, 'document_page.html', context)

            else:
                print(edit_form.errors)

    else:
        state = Imagen.objects.get(
            archivo__nombre_del_archivo=archivo,
            colección__nombre_de_la_colección=colección,
            caja=caja,
            legajo=legajo,
            carpeta=carpeta,
            número_de_imagen=número_de_imagen,
        )
        print(state.texto_de_OCR)
        # TODO add forward + backward buttons
        possible_pages = Imagen.objects.filter(
            archivo__nombre_del_archivo=state.archivo,
            colección__nombre_de_la_colección=state.colección,
            caja=state.caja,
            legajo=state.legajo,
            carpeta=state.carpeta,
        ).order_by('número_de_imagen')
        pages_list = []
        for index, page in enumerate(possible_pages):
            pages_list.append(page)

            # print(index, page)
            if page == state:
                print('current= ', page.número_de_imagen, index)
                current = int(index)
        previous = pages_list[current - 1].número_de_imagen
        try:
            next_one = pages_list[current + 1].número_de_imagen
        except:
            next_one = pages_list[0].número_de_imagen
        total = len(possible_pages)
        current = current + 1
        print('previous= ', previous)
        print('next= ', next_one)
        # next_one = pages_list[int(current)+1]
        # print(current, next_one, previous)
        # print(index, page)
        # if page == state:
        #    print('this is it', page.número_de_imagen, index)
        #        current = index
        #    next_one = current + 1, page
        #    print(next_one)
        # print (possible_pages)

        id = state.id

        form = EditForm(initial={'texto_de_OCR':state.texto_de_OCR, 'notas':state.notas.encode('utf8')})
        images_in_carpeta = Imagen.objects.all().filter(
            caja=caja, legajo=legajo, carpeta=carpeta
        )

        carpeta_query = Carpeta.objects.filter(
            archivo__nombre_del_archivo=archivo,
            colección__nombre_de_la_colección=colección,
            caja=caja,
            legajo=legajo,
            carpeta=carpeta,
        )

        try:
            carpeta_form = CarpetaForm(
                initial={
                    'descripción': carpeta_query[0].descripción,
                    'carpeta_titulo': carpeta_query[0].carpeta_titulo,
                }
            )
        except:
            carpeta_form = ''
        context = {
            'carpeta_form': carpeta_form,
            'state': state,
            'form': form,
            'id': id,
            'current': current,
            'total': total,
            'previous': previous,
            'next_one': next_one,
            'images_in_carpeta': images_in_carpeta,
        }
        return render(request, 'document_page.html', context)


# carpeta view
@login_required
def documento4(request, archivo, colección, caja, legajo, carpeta):

    state = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
        carpeta=carpeta,
    ).order_by('número_de_imagen')
    location = {
        'archivo': archivo,
        'colección': colección,
        'caja': caja,
        'legajo': legajo,
        'carpeta': carpeta,
    }
    possible_carpeta = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
    ).order_by('carpeta')
    carpeta_list = []
    # make a list of the possible carpetas with index values
    for index, page in enumerate(possible_carpeta):
        if page.carpeta not in carpeta_list:
            carpeta_list.append(page.carpeta)
    for item in carpeta_list:
        if item == carpeta:
            current = item
            print('current is', current)
    # find index in list for current
    try:
        index_current = carpeta_list.index(current)

        try:
            previous_carpeta = carpeta_list[index_current - 1]
            next_carpeta = carpeta_list[index_current + 1]
        except:
            next_carpeta = carpeta_list[0]
    except:
        pass

    context = {
        'state': state,
        'location': location,
        'previous_carpeta': previous_carpeta,
        'next_carpeta': next_carpeta,
    }
    return render(request, 'all_documents_page.html', context)


# legajo view
@login_required
def documento3(request, archivo, colección, caja, legajo):

    state = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
    ).order_by('carpeta')
    location = {
        'archivo': archivo,
        'colección': colección,
        'caja': caja,
        'legajo': legajo,
    }
    possible_legajo = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
    ).order_by('legajo')
    legajo_list = []
    # make a list of the possible carpetas with index values
    for index, page in enumerate(possible_legajo):
        if page.legajo not in legajo_list:
            legajo_list.append(page.legajo)
    for item in legajo_list:
        if item == legajo:
            current = item
    print(legajo_list, current, legajo_list.index(current))

    # find index in list for current
    index_current = legajo_list.index(current)
    previous_legajo = legajo_list[index_current - 1]
    try:
        next_legajo = legajo_list[index_current + 1]
        print(next_legajo)
    except:
        next_legajo = legajo_list[0]
        print(next_legajo)
    carpetas = Carpeta.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
        legajo=legajo,
    )

    context = {
        'state': state,
        'location': location,
        'previous_legajo': previous_legajo,
        'next_legajo': next_legajo,
        'carpetas': carpetas,
    }
    return render(request, 'grandes_colecciones.html', context)


@login_required
def documento2(request, archivo, colección, caja):

    state = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
    ).order_by('legajo')
    location = {'archivo': archivo, 'colección': colección, 'caja': caja}
    possible_caja = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo, colección__nombre_de_la_colección=colección
    ).order_by('caja')
    caja_list = []
    # make a list of the possible carpetas with index values
    for index, page in enumerate(possible_caja):
        if page.caja not in caja_list:
            caja_list.append(page.caja)
    for item in caja_list:
        if item == caja:
            current = item
        else:
            current = caja_list[0]
    # find index in list for current
    index_current = caja_list.index(current)
    previous_caja = caja_list[index_current - 1]
    try:
        next_caja = caja_list[index_current + 1]
    except:
        next_caja = caja_list[0]
    # distinct = Imagen.objects.values('legajo').annotate(count=Count('legajo')).filter(count=1)

    legajos = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo,
        colección__nombre_de_la_colección=colección,
        caja=caja,
    )
    legajo_list = set([legajo.legajo for legajo in legajos])

    context = {
        'state': state,
        'location': location,
        'previous_caja': previous_caja,
        'next_caja': next_caja,
        'legajos': legajo_list,
    }
    return render(request, 'grandes_colecciones.html', context)


@login_required
def documento1(request, archivo, colección):

    state = Imagen.objects.filter(
        archivo__nombre_del_archivo=archivo, colección__nombre_de_la_colección=colección
    ).order_by('caja')
    cajas = Caja.objects.filter(
        archivo__nombre_del_archivo=archivo, colección__nombre_de_la_colección=colección
    )
    location = {'archivo': archivo, 'colección': colección}

    context = {'state': state, 'location': location, 'cajas': cajas}
    return render(request, 'grandes_colecciones.html', context)


@login_required
def documento0(request, archivo):

    state = Imagen.objects.filter(archivo__nombre_del_archivo=archivo).order_by(
        'número_de_imagen'
    )
    colecciones = Colección.objects.filter(archivo__nombre_del_archivo=archivo)

    location = {'archivo': archivo}
    context = {'state': state, 'location': location, 'colecciones': colecciones}

    return render(request, 'grandes_colecciones.html', context)


@login_required
def item(request, nombre_del_item):

    state = Imagen.objects.filter(item__nombre_del_item=nombre_del_item)

    archivo = state[0].archivo
    colección = state[0].colección
    caja = state[0].caja
    legajo = state[0].legajo
    carpeta = state[0].carpeta

    possible_items = Item.objects.filter(
        nombre_del_item__icontains=nombre_del_item[:-3]
    )
    item_list = []
    # make a list of the possible items with index values
    for index, item in enumerate(possible_items):
        if item not in item_list:
            item_list.append(item)
    print(item_list)
    for item in item_list:
        if str(item) == state[0].localizacion_fisica:
            current = item
            print('current is', current)
    # find index in list for current
    index_current = item_list.index(current)
    previous_carpeta = item_list[index_current - 1]
    try:
        next_carpeta = item_list[index_current + 1]
    except:
        next_carpeta = item_list[0]

    carpeta_info = Caso.objects.filter(
        caja_no=caja, legajo_no=legajo, carpeta_no=carpeta
    )

    images_in_carpeta = Imagen.objects.all().filter(
        caja=caja, legajo=legajo, carpeta=carpeta
    )

    location = {
        'archivo': archivo,
        'colección': colección,
        'caja': caja,
        'legajo': legajo,
        'carpeta': carpeta,
        'item': nombre_del_item.split('_')[-1],
    }

    context = {
        'state': state,
        'location': location,
        'previous_carpeta': previous_carpeta,
        'next_carpeta': next_carpeta,
        'carpeta_info': carpeta_info,
        'images_in_carpeta': images_in_carpeta,
    }

    return render(request, 'item.html', context)
