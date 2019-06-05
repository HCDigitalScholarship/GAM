from django.core.management.base import BaseCommand, CommandError
from gam_app.tracking import *
from gam_app.models import *
import os
import bagit
import zipfile
import pyvips
import re
import uuid
from PIL import Image
import shutil
import sys


class file_counter(object):
    def __init__(self):
        self.position = self.size = 0

    def seek(self, offset, whence=0):
        if whence == 1:
            offset += self.position
        elif whence == 2:
            offset += self.size
        self.position = min(offset, self.size)

    def tell(self):
        return self.position

    def write(self, string):
        self.position += len(string)
        self.size = max(self.size, self.position)


def smaller_than(im, size, guess=70, subsampling=1, low=1, high=100):
    while low < high:
        counter = file_counter()
        im.save(counter, format='JPEG', subsampling=subsampling, quality=guess)
        if counter.size < size:
            low = guess
        else:
            high = guess - 1
        guess = (low + high + 1) // 2
    return low


def change_size_if_needed(file):
    if os.path.getsize(file) > 4000000:
        im = Image.open(file)
        size = smaller_than(im, 4000000)
        #  print(size) very useful to improve performance, print average value and change line 62 for less processing
        im.save(file, 'JPEG', quality=size)


def import_image_file(filename, nombre_de_la_bolsa):
    new_filename = (
        str(uuid.uuid4()) + '-' + filename.split('/')[-1].split('.')[0] + '.jpg'
    )
    if not os.path.isdir('/mnt/bags/{}/documents/'.format(nombre_de_la_bolsa)):
        os.mkdir('/mnt/bags/{}/documents/'.format(nombre_de_la_bolsa))

    new_path = '/mnt/bags/{}/documents/'.format(nombre_de_la_bolsa)

    #  convert the tiff to jpeg
    try:
        im = Image.open(filename)
        im.save(new_path + new_filename, 'JPEG', quality=85)

    except Exception as e:
        print(e)

    # convert all files to 4mb, adds significant time to import, but still good image quality. Consistent with earlier
    # import_dip script.
    change_size = True
    if change_size:
        change_size_if_needed(new_path + new_filename)

        #  save a copy of the jpg in the documents directory
        im.save('/mnt/documents/' + new_filename, 'JPEG')
    #  create a dzi from the jpeg
    try:
        print('[*] %s' % new_filename)
        dzi_me = pyvips.Image.new_from_file(new_path + new_filename)

        if not os.path.isdir('/mnt/dzis1/{}/'.format(nombre_de_la_bolsa)):
            os.mkdir('/mnt/dzis1/{}/'.format(nombre_de_la_bolsa))
        dzi_me.dzsave('/mnt/dzis1/{}/{}'.format(nombre_de_la_bolsa, new_filename))

        #  Here we re-add the jpg to the filename, this is not really a good thing, but too late to change it
        os.rename(
            '/mnt/dzis1/{}/{}'.format(nombre_de_la_bolsa, new_filename.replace('.jpg', '.dzi')),
            '/mnt/dzis1/{}/{}'.format(nombre_de_la_bolsa, new_filename + '.dzi'),
        )
        os.rename(
            '/mnt/dzis1/{}/{}'.format(nombre_de_la_bolsa, new_filename.replace('.jpg', '_files')),
            '/mnt/dzis1/{}/{}'.format(nombre_de_la_bolsa, new_filename + '_files'),
        )

    except Exception as e:
        print(e)

    #  This section reads the filename for information about the location of the file in the archive.
    # remove uuid
    location = new_filename.split('-')[-1]
    # remove .jpg
    location = location.split('.')[0]
    physical_location = location
    # print(physical_location)
    # print(location)
    parts = location.split('_')
    # print(parts)
    archive = parts[0].lower()
    collection = parts[1].lower()
    box = parts[2]
    bundle = parts[3]
    try:
        folder = parts[4]
    except IndexError:
        # Initially, the filenames did not have the archive and collection names. Those bags need reformatting.
        reformat_old_bag(dip_name)

    image = parts[5]

    if archive == 'gam':
        archivo_id = Archivo.objects.get(nombre_del_archivo='Archivo del GAM')
    else:
        archivo_name = input(
            "That archive does not exist, please enter a new archive name: "
        )
        Archivo.objects.get_or_create(nombre_del_archivo=archivo_name)
        archivo_id = Archivo.objects.get(nombre_del_archivo='%s' % archivo_name)

    if collection == 'des':
        # print(collection)
        collection_id = Colección.objects.get(nombre_de_la_colección='Desaparecidos')

    elif collection == 'nin':
        collection_id = Colección.objects.get(
            nombre_de_la_colección='Niñez Desparecida'
        )

    else:
        collection_name = input(
            "That collection does not exist, please enter a new collection name: "
        )
        Colección.objects.get_or_create(nombre_de_la_colección=collection_name)
        collection_id = Colección.objects.get(
            nombre_de_la_colección='%s' % collection_name
        )

    # create the document in the db
    # print('nombre_del_archivo= ',new_filename,
    #    'localizacion_fisica= ',physical_location,
    #    'archivo_id= ', archivo_id.pk,
    #    'colección_id= ', collection_id.pk,
    #    'caja= ', box,
    #    'legajo= ', bundle,
    #    'carpeta= ', folder,
    #    'número_de_imagen= ', image,
    #    'bag_name= ', nombre_de_la_bolsa,
    #      )

    # create the document in the db
    Imagen.objects.update_or_create(
        nombre_del_archivo=new_filename,
        localizacion_fisica=physical_location,
        archivo_id=archivo_id.pk,
        colección_id=collection_id.pk,
        caja=box,
        legajo=bundle,
        carpeta=folder,
        número_de_imagen=image,
        bag_name=nombre_de_la_bolsa,
    )


def import_resumen_file(path):
    """This is a function used to read the resumen file, which contains folder descriptions.  The script
    reads the file and updates or creates folder descriptions in the database."""

    with open(path, encoding='ISO-8859-1') as fp:
        content = fp.readlines()
        content = [x.strip() for x in content]

    # Gets rid of empty strings (white spaces in this case) from the list
    while '' in content:
        content.remove('')
    # Dictionary containing bag name as key and bag date and description as value
    carpeta_descripcion = {}
    keys = []
    for i in range(len(content)):

        if re.search('^\w{3}_\w{3}_\d{3}', content[i]):
            keys.append(i)

    for i in range(len(keys)):
        try:
            carpeta_descripcion[content[keys[i]]] = content[(keys[i] + 1) : keys[i + 1]]
        except IndexError:
            carpeta_descripcion[content[keys[i]]] = content[(keys[i] + 1) :]

    # print(carpeta_descripcion)
    for carpeta in carpeta_descripcion:
        print('[*]', carpeta)
        parts = carpeta.split('_')
        archive = parts[0].lower()
        collection = parts[1].lower()
        box = parts[2]
        bundle = parts[3]
        folder = parts[4]
        descripción = carpeta_descripcion[carpeta]
        descripción = '\n'.join(descripción)

        if archive == 'gam':
            archivo_id = Archivo.objects.get(nombre_del_archivo='Archivo del GAM')
        else:
            archivo_name = input(
                "That archive does not exist, please enter a new archive name: "
            )
            Archivo.objects.get_or_create(nombre_del_archivo=archivo_name)
            archivo_id = Archivo.objects.get(nombre_del_archivo='%s' % archivo_name)

        if collection == 'des':
            collection_id = Colección.objects.get(
                nombre_de_la_colección='Desaparecidos'
            )
        elif collection == 'nin':
            collection_id = Colección.objects.get(
                nombre_de_la_colección='Niñez Desparecida'
            )

        else:
            collection = input(
                "That collection does not exist, please enter a new archive name: "
            )
            Colección.objects.get_or_create(nombre_de_la_colección=collection)
            collection_id = Colección.objects.get(
                nombre_de_la_colección='%s' % collection
            )

        # print('archivo_id= ', archivo_id.pk,
        #      'colección_id= ', collection_id.pk,
        #      'caja= ', box,
        #      'legajo= ', bundle,
        #      'carpeta= ', folder,
        #      'descripción= ', descripción)

        Carpeta.objects.update_or_create(
            archivo_id=archivo_id.pk,
            colección_id=collection_id.pk,
            caja=box,
            legajo=bundle,
            carpeta=folder,
            descripción=descripción,
        )


class Command(BaseCommand):
    help = """Este es un comando que controlará automáticamente los depósitos en el almacenamiento en la nube en busca 
    de nuevas bolsas. Luego validará, descomprimirá e importará las nuevas bolsas."""

    def handle(self, *args, **options):
        bolsas = set(getBags())
        bolsas_importadas = set(getImportedBags())
        bolsas_nuevas = bolsas.difference(bolsas_importadas)
        bolsas_nuevas = list(bolsas_nuevas)

        if len(bolsas_nuevas) == 0:
            print('no hay bolsas nuevas')
            sys.exit()

        for bolsa in bolsas_nuevas:
            print(bolsas_nuevas.index(bolsa), bolsa)

        dip = input("Ingrese el número de la bolsa para importar: ")
        nombre_de_la_bolsa = bolsas_nuevas[int(dip)]
        print("Importando la bolsa {}".format(nombre_de_la_bolsa))

        #  download and unzip the bag file
        if os.path.isfile('/mnt/bags/{}'.format(nombre_de_la_bolsa + '.zip')):
            print('file already downloaded')
            zip_file = zipfile.ZipFile(
                '/mnt/bags/{}'.format(nombre_de_la_bolsa + '.zip')
            )
            zip_file.extractall('/mnt/bags/')
            zip_file.close()
            os.remove('/mnt/bags/{}'.format(nombre_de_la_bolsa + '.zip'))

        elif descargar_una_sola_bolsa(nombre_de_la_bolsa + '.zip'):
            zip_file = zipfile.ZipFile(
                '/mnt/bags/{}'.format(nombre_de_la_bolsa + '.zip')
            )
            zip_file.extractall('/mnt/bags/')
            zip_file.close()
            os.remove('/mnt/bags/{}'.format(nombre_de_la_bolsa + '.zip'))
            print('archivo descargado exitosamente')

        #  Validate the bag
        bag = bagit.Bag('/mnt/bags/{}'.format(nombre_de_la_bolsa))
        if bag.is_valid():
            print('la bolsa es valida')
            tiff_files = [
                os.path.join(root, name)
                for root, dirs, files in os.walk(
                    '/mnt/bags/{}/data/'.format(nombre_de_la_bolsa)
                )
                for name in files
                if name.endswith(('.tiff', '.tif'))
            ]
            txt_files = [
                os.path.join(root, name)
                for root, dirs, files in os.walk(
                    '/mnt/bags/{}/data/'.format(nombre_de_la_bolsa)
                )
                for name in files
                if name.endswith(('.txt', '.TXT'))
            ]

            [import_image_file(file, nombre_de_la_bolsa) for file in tiff_files]
            [import_resumen_file(file) for file in txt_files]

            shutil.rmtree('/mnt/bags/{}'.format(nombre_de_la_bolsa))
            os.system('s4cmd -r --verbose --config=/home/ajanco/.s3cfg --num-threads=6 --endpoint-url https://nyc3.digitaloceanspaces.com sync /mnt/dzis1/{}/  s3://dzis'.format(nombre_de_la_bolsa))

        else:
            print('la bolsa no es valida')
