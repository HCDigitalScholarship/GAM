from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.html import format_html

from ckeditor.fields import RichTextField


class Persona(models.Model):
    """A person."""

    nombre_de_la_persona = models.CharField(max_length=200, null=True)
    nombre = models.CharField(max_length=200, blank=True)
    segundo = models.CharField(max_length=200, blank=True)
    apellido_paterno = models.CharField(max_length=200, blank=True)
    apellido_materno = models.CharField(max_length=200, blank=True)
    fecha_de_nacimiento = models.CharField(max_length=200, blank=True)
    fecha_desaparicion = models.CharField(max_length=200, blank=True)
    edad_en_el_momento = models.CharField(max_length=200, blank=True)
    género = models.CharField(max_length=200, blank=True)
    etnicidad = models.CharField(max_length=200, blank=True)
    ocupación = models.CharField(max_length=200, blank=True)
    actividades_políticas = models.ManyToManyField('Organización', blank=True)
    # relaciones = models.ManyToManyField('Relación', blank=True)
    image = models.ManyToManyField('Imagen', blank=True)
    notas = RichTextField(blank=True)

    def __str__(self):
        return self.nombre_de_la_persona

    def get_absolute_url(self):
        return "/persona/%i/" % self.id


class Relación(models.Model):
    """A relationship."""

    persona_A = models.ManyToManyField(Persona, blank=False, related_name='A')
    persona_B = models.ManyToManyField(Persona, blank=False, related_name='B')
    relación = models.CharField(max_length=200, null=True)


class Lugar(models.Model):
    """A place."""

    nombre_del_lugar = models.CharField(max_length=200, null=True)
    image = models.ManyToManyField('Imagen', blank=True)
    punto = geomodels.PointField(blank=True, null=True)

    def __str__(self):
        return self.nombre_del_lugar


class Organización(models.Model):
    """An organization entity.

    Typically refers to a political organziation that a person was affiliated with.
    """

    nombre_de_la_organización = models.CharField(max_length=200, null=True)
    image = models.ManyToManyField('Imagen', blank=True)

    def __str__(self):
        return self.nombre_de_la_organización


class Caso(models.Model):
    """This one is complicated. Basically, these are bundles of papers that were put
    together as the workers at GAM investigated a report or request for information.
    They were later put into folders together under a "case" title. The title often
    refers to one or more people involved in the case (so they look like names), but
    they refer to a "case."  This list of cases is being used by the archive team in
    Guatemala to process and catalog the materials.  It's not clear how this will work
    out in the long term.
    """

    caso = models.CharField(max_length=200, blank=True)
    fecha_desaparicion = models.CharField(max_length=200, blank=True)
    departamento = models.CharField(max_length=200, blank=True)
    local = models.CharField(max_length=200, blank=True)
    area = models.CharField(max_length=200, blank=True)
    ambiente = models.CharField(max_length=200, blank=True)
    estanteria_no = models.CharField(max_length=200, blank=True)
    plato_no = models.CharField(max_length=200, blank=True)
    caja_no = models.CharField(max_length=200, blank=True)
    legajo_no = models.CharField(max_length=200, blank=True)
    carpeta_no = models.CharField(max_length=200, blank=True)
    descripcion_caso = RichTextField()

    def __str__(self):
        return self.caso


class Portapapeles(models.Model):
    """A clipboard. An entity for creating lists of individual images, manuscripts and
    cases for users during research. For example, a member of the legal team may want to
    include all the documents they have come across that relate to a current case.
    """

    nombre_del_portapapeles = models.CharField(max_length=200, blank=True)
    usuario = models.ManyToManyField(User, blank=True)
    casos = models.ManyToManyField(Caso, blank=True)
    imágenes = models.ManyToManyField('Imagen', blank=True)
    manuscrito = models.ManyToManyField('Item', blank=True)

    def __str__(self):
        return self.nombre_del_portapapeles


PERSON_STATUS_CHOICES = (
    ('NONE', 'Sin correcciones'),
    ('IN', 'En progreso'),
    ('DONE', 'Compitió'),
    ('FINAL', 'Competido y verificado'),
)
PLACE_STATUS_CHOICES = (
    ('NONE', 'Sin correcciones'),
    ('IN', 'En progreso'),
    ('DONE', 'Compitió'),
    ('FINAL', 'Competido y verificado'),
)
ORGANIZATION_STATUS_CHOICES = (
    ('NONE', 'Sin correcciones'),
    ('IN', 'En progreso'),
    ('DONE', 'Compitió'),
    ('FINAL', 'Competido y verificado'),
)


class Caja(models.Model):
    """A folder."""

    archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE, default=1)
    colección = models.ForeignKey('Colección', on_delete=models.CASCADE, default=1)
    número_de_caja = models.CharField(max_length=200, blank=True)
    carpetas = models.ManyToManyField('Carpeta', blank=True, related_name='carpetas')
    departamento = models.ManyToManyField(
        Lugar, blank=True, related_name='departamento'
    )
    municipios = models.ManyToManyField(Lugar, blank=True, related_name='municipios')
    letras = models.CharField(max_length=200, blank=True)
    legajos = models.CharField(max_length=200, blank=True)
    fechas_extremas = models.CharField(max_length=200, blank=True)
    volumen_en_metros_lineales = models.CharField(max_length=200, blank=True)
    sistema_digital = models.CharField(max_length=200, blank=True)
    descripción = RichTextField(blank=True, default='')

    def __str__(self):
        return '{}/{}/{}'.format(self.archivo, self.colección, self.número_de_caja)


class Carpeta(models.Model):
    carpeta_titulo = models.CharField(max_length=200, blank=True)
    persona = models.ManyToManyField('Persona', blank=True)
    organización = models.ManyToManyField('Organización', blank=True)
    nombre_de_la_carpeta = models.CharField(max_length=200, blank=True)
    archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE)
    colección = models.ForeignKey('Colección', on_delete=models.CASCADE)
    caja = models.CharField(max_length=200, blank=True)
    legajo = models.CharField(max_length=200, blank=True)
    carpeta = models.CharField(max_length=200, blank=True)
    número_de_víctimas = models.IntegerField(null=True, blank=True)
    ubicación_geográfica = models.ManyToManyField('Lugar', blank=True)
    tipo_de_violencia = models.CharField(max_length=200, blank=True)
    descripción = RichTextField(blank=True, default='')
    descripción_generada_automaticamente = RichTextField(blank=True)
    person_status = models.CharField(
        max_length=20, choices=PERSON_STATUS_CHOICES, null=True, blank=True
    )
    place_status = models.CharField(
        max_length=20, choices=PLACE_STATUS_CHOICES, null=True, blank=True
    )
    organization_status = models.CharField(
        max_length=20, choices=ORGANIZATION_STATUS_CHOICES, null=True, blank=True
    )

    def __str__(self):
        return '{}/{}/{}'.format(self.caja, self.legajo, self.carpeta)


class Colección(models.Model):
    """An archival collection."""

    archivo = models.ForeignKey('Archivo', on_delete=models.CASCADE)
    nombre_de_la_colección = models.CharField(max_length=200, blank=True)
    descripción = RichTextField(blank=True, default='')

    def __str__(self):
        return self.nombre_de_la_colección


class Archivo(models.Model):
    """Archivo means both archive and file in Spanish. This model refers to an Archive,
    as in the Archives of GAM or the Internet Archive.
    """

    nombre_del_archivo = models.CharField(max_length=200, blank=True)
    descripción = RichTextField(blank=True, default='')

    def __str__(self):
        return self.nombre_del_archivo


STATUS_CHOICES = (
    ('NONE', 'Sin correcciones'),
    ('IN', 'En progreso'),
    ('DONE', 'Compitió'),
    ('FINAL', 'Competido y verificado'),
)


class Imagen(models.Model):
    """An image in the archive. The core entiy in the data model."""

    # persona = models.ManyToManyField('Persona', blank=True)
    nombre_del_archivo = models.CharField(max_length=200, blank=True)
    localizacion_fisica = models.CharField(max_length=200, blank=True)
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE, default=1)
    colección = models.ForeignKey(Colección, on_delete=models.CASCADE, default=1)
    caja = models.CharField(max_length=200, blank=True)
    legajo = models.CharField(max_length=200, blank=True)
    carpeta = models.CharField(max_length=200, blank=True)
    # Note that image number is CharField given use of 001a and 001b.
    número_de_imagen = models.CharField(max_length=200, blank=True)
    item = models.ForeignKey('Item', on_delete=models.CASCADE, blank=True, null=True)
    forma_de_GAM = models.CharField(max_length=200, blank=True)
    texto_de_OCR = RichTextField(blank=True)
    notas = RichTextField(blank=True)
    traducción = RichTextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True)
    bag_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombre_del_archivo

    def get_absolute_url(self):
        args = [
            self.archivo,
            self.colección,
            self.caja,
            self.legajo,
            self.carpeta,
            self.número_de_imagen,
        ]
        return reverse('documento5', args=args)

    def url(self):
        args = [
            self.archivo,
            self.colección,
            self.caja,
            self.legajo,
            self.carpeta,
            self.número_de_imagen,
        ]
        link = reverse('documento5', args=args)
        return format_html(u'<a target="_blank" href="{}">abierto</a>'.format(link))

    def get_image_url(self):
        return '/static/documents/' + self.nombre_del_archivo


class Item(models.Model):
    """An entity to link single-page images together as part of multi-page documents
    such as a pamphlet or book.
    """

    nombre_del_item = models.CharField(max_length=200, null=True)
    site = models.ManyToManyField(Site)

    def __str__(self):
        return self.nombre_del_item

    def archivo(self):
        if self.nombre_del_item.split('_')[0] == 'gam':
            archivo = Archivo.objects.get(nombre_del_archivo='Archivo del GAM')
            return archivo

    def colección(self):
        if self.nombre_del_item.split('_')[1] == 'des':
            colección = Colección.objects.get(nombre_de_la_colección='Desaparecidos')
            return colección

        if self.nombre_del_item.split('_')[1] == 'nin':
            colección = Colección.objects.get(
                nombre_de_la_colección='Niñez Desparecida'
            )
            return colección

    def caja(self):
        return self.nombre_del_item.split('_')[2]

    def legajo(self):
        return self.nombre_del_item.split('_')[3]

    def carpeta(self):
        return self.nombre_del_item.split('_')[4]


class Transcrito(models.Model):
    """Transcriptions, these work with the machine readable text associated with an
    image. The text is initially ocr'd with Google Vision. When a user maker a
    correction, the previous version is saved here.
    """

    nombre_del_archivo = models.CharField(max_length=200, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tiempo_modificado = models.DateTimeField()
    texto_transcrito = RichTextField()
