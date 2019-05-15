from itertools import cycle
from bokeh.embed import server_document
from bokeh.embed import server_session
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers

from acceso.models import *
from gam_app.models import Persona
from gam_app.models import Caso as Database
from gam_app.models import Carpeta
import os
import random
from django.views.generic.base import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape
from django.db.models import Count, Q
import mysql.connector
from mysql.connector import errorcode
import os
import sys
sys.path.append('/srv/GAM/archivo/')
from archivo.settings_secret import DATABASES
import plotly 
#plotly.tools.set_credentials_file(username='ajanco', api_key='2uxIhIy1JmOasiWozwd7')
plotly.plotly.sign_in('ajanco', '1prkGNW7WC9aNhGtxk0X')
import plotly.plotly as py
import plotly.graph_objs as go 
import cufflinks as cf
import plotly.offline as opy
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from collections import OrderedDict 
import dash
import dash_core_components as dcc
import dash_html_components as html

from django_plotly_dash import DjangoDash
#app = DjangoDash('SimpleExample')   # replaces dash.Dash
import json
from django.core.serializers.json import DjangoJSONEncoder
app = DjangoDash('SimpleExample')
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
                }
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Graph(
        id='Graph1',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    )
                ])


def cycle(iterable):
	saved = []
	for element in iterable:
		yield element
		saved.append(element)
	while saved:
		for element in saved:
			yield element

def bokeh(request):
    script = server_document(url="http://192.241.128.56:8000/en/acceso/bokeh/people", relative_urls=True)
    return render(request, 'acceso/bokeh.html', {'script': script})
	

def random_photo():
	#yield from cycle(os.listdir('/srv/GAM/acceso/static/pat_goudvis'))
	photos = os.listdir('/srv/GAM/acceso/static/pat_goudvis')
	photo = random.choice(photos)
	return photo

def next_photo():
		photos = os.listdir('/srv/GAM/acceso/static/pat_goudvis')
		num = 0
		while num < len(photos)-1:
			yield photos[num]
			num += 1

def main(request, options):
	casos = Caso.objects.all()
	filters = Filtros.objects.all()
	filter_list = []
	for filter in filters:
		filter_list.append(filter.nombre_del_filtro)
	photo_list = []
	for caso in casos:
		photo_list.append(caso.fotos.first())

	photo = random_photo()
	#photos = os.listdir('/srv/GAM/acceso/static/pat_goudvis')
	#photo = cycle(photos)
	#photo = next(photo)
	#print(photo)
	#print('casos:  ', casos)
	context = {'casos': casos, 'photo_list': photo_list, 'filter_list':filter_list, 'photo': photo}

	return render(request, 'acceso/index.html', context)

def filtrar_imagenes(request):
    photo_mostrar = random_photo()
    filter_list = ["none"]
    photos = Photo.objects.all()
    photo_list = {}
    for photo in photos:
        photo.folder = photo.folder[8:]
        caja, legajo, carpeta = photo.folder[:3], photo.folder[4:7], photo.folder[8:11]
        caso = Caso.objects.filter(carpetas__caja=caja, carpetas__legajo=legajo, carpetas__carpeta=carpeta)
        photo_list[photo] = caso[0]
        photo.folder = "GAM Des " +  caja + " " + legajo + " " + carpeta
    context = {'photo_list':photo_list, 'filter_list': filter_list, 'photo_mostrar':photo}
    return render(request, 'acceso/filtrar_imagenes.html', context)

def skynet(request):
	photo = [[532, "dataset/cat/2008_007496.jpg", 0.4442075490951538],
			 [548, 'dataset/cat/2008_003622.jpg', 0.46999311447143555],
			 [530, 'dataset/cat/2008_006999.jpg', 0.471227765083313],
			 [543, 'dataset/cat/2008_005252.jpg', 0.4816729426383972],
			 [517, 'dataset/cat/2008_004303.jpg', 0.4869983196258545],
			 [508, 'dataset/cat/2008_001885.jpg', 0.49179962277412415],
			 [541, 'dataset/cat/2008_005386.jpg', 0.4957163631916046],
			 [509, 'dataset/cat/2008_000182.jpg', 0.4999980032444],
			 [527, 'dataset/cat/2008_000345.jpg', 0.5011175274848938],
			 [545, 'dataset/cat/2008_001335.jpg', 0.5041385889053345]]
	n = 0
	photoclean = []
	for i in photo:
		photoclean.append(i[1])
	print(photoclean)

	return render(request, 'acceso/skynet.html', {'photo':photoclean})


def network(request):
	return render(request, 'acceso/red.html',)

def collection(request):
	photo = random_photo()
	return render(request, 'acceso/collection.html', {'photo':photo, })

def documentos(request):
	casos = Caso.objects.all()
	carpetas = [caso.carpetas.all() for caso in casos]
	all_carpetas = []
	for list_ in carpetas:
		for carpeta in list_:
			all_carpetas.append(carpeta)
	imagens = []
	for i, carpeta in enumerate(carpetas):
		images = Imagen.objects.filter(
			archivo=all_carpetas[i].archivo,
			colección=all_carpetas[i].colección,
			caja=all_carpetas[i].caja,
			legajo=all_carpetas[i].legajo,
			carpeta=all_carpetas[i].carpeta,
		).order_by('número_de_imagen')
		imagens.append(images)
	imagen_names = []
	for image in imagens:
		for imagen in image:
			imagen_names.append(imagen.nombre_del_archivo)
	return render(request, 'acceso/documentos.html', {'state':imagen_names, })


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
    personas = caso.personas.all()
    for x in caso.fotos.all():
        foto.append(x)
    profile_photos = Foto.objects.filter(caso__slug_name=caso)
    context = {'caso': caso, 'images': foto,'personas':personas, 'dragon': dragon, 'face':imageprofile}

    return render(request, 'acceso/caso.html', context)


def simple(request):
	casos = Caso.objects.all()
	context = {'casos': casos}
	return render(request, 'simple/acceso.html', context)


def caso_index(request):
	return render(request, 'acceso/caso_index.html')

def datatable(request):
	return render(request, 'acceso/datatable.html')

def caso_table(request, caso_id):
	# TODO: Probably want nombre_del_caso to be an explicit part of the URL rather than
	# a GET parameter.
	caso = Caso.objects \
		.filter(nombre_del_caso__icontains=request.GET.get('nombre_del_caso')) \
		.filter(descripción__icontains=request.GET.get('descripción'))
	return JsonResponse(serializers.serialize(caso))

def network_json(request):

	dict = {'nodes': [], 'links': [],'nodesuntracked':[]}
	with open('/srv/GAM/acceso/my_file.txt', 'r') as f:
		node_list = list([line.split(',')[0] for line in f])
		for node in set(node_list):
			dict['nodesuntracked'].append({"name": node, "group": 1}, )
		for node in set(node_list):
			node_index = dict['nodesuntracked'].index({"name": node, "group": 1}, )
			dict['nodes'].append({"name": node, "group": 1, "index": node_index,"pop":""})

	with open('/srv/GAM/acceso/my_file.txt', 'r') as f:
		for line in f:
			node = line.split(',')[0]
			target = line.split(',')[1]
			weight = line.replace('\n', '').split(',')[2]
			if weight != "0.0":
				node_index = dict['nodesuntracked'].index({"name":node, "group":1},)
				try:
					target_index = dict['nodesuntracked'].index({"name": target,"group":1},)
				except:
					pass
				dict['links'].append({"source": node_index, "target": target_index, "weight": float(weight) * 10})
	for node in dict['nodes']:
		popers = []
		for link in dict['links']:
			if (node["index"] == link["source"]):
				popers.append(link["target"])
			elif (node["index"] == link["target"]):
				popers.append(link["source"])
		node["pop"] = popers

   
	response = JsonResponse(dict)

	return response


class DbListJson(BaseDatatableView):
	# the model you're going to show
	model = Database

	# define columns that will be returned
	# they should be the fields of your model, and you may customize their displaying contents in render_column()
	# don't worry if your headers are not the same as your field names, you will define the headers in your template
	columns = ['caso', 'fecha_desaparicion', 'departamento','descripcion_caso', ]

	# define column names that will be used in sorting
	# order is important and should be same as order of columns displayed by datatables
	# for non sortable columns use empty value like ''
	order_columns = ['caso', 'fecha_desaparicion', 'departamento','descripcion_caso', ]

	# set max limit of records returned
	# this is used to protect your site if someone tries to attack your site and make it return huge amount of data
	max_display_length = 500

	def render_column(self, row, column):

		return super(DbListJson, self).render_column(row, column)

	def filter_queryset(self, qs):
		# use parameters passed in GET request to filter queryset

		# here is a simple example
		search = self.request.GET.get('search[value]', None)
		if search:
			q = Q(caso__icontains=search) | Q(descripcion_caso__icontains=search) | Q(fecha_desaparicion__icontains=search) | Q(departamento__icontains=search)
			qs = qs.filter(q)
		return qs

class Plotly(TemplateView):
	template_name = 'acceso/collection.html'
	def get_context_data(self, **kwargs):
		context = super(Plotly, self).get_context_data(**kwargs)
		try:
			conn = mysql.connector.connect(user=DATABASES['default']['USER'], password=DATABASES['default']['PASSWORD'], host=DATABASES['default']['HOST'], database=DATABASES['default']['NAME'])
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
		#c = conn.cursor()
		photos = os.listdir('/srv/GAM/acceso/static/pat_goudvis')
		photo = random.choice(photos)
		context['photo'] = photo
		df = pd.read_sql(
                """
                SELECT *
                FROM gam_app_caso
                """, con=conn)
		#context['count_caja'] = df.caja_no.nunique()-1
		estanteria = list(df.estanteria_no.unique())
		estanteria = estanteria[1:]
		estanteria.reverse()
		dd = {}
		caja_no = 0
		total_files = df.shape[0]
		for i in estanteria:
			ll = []
			count = 0
			dff = df[(df['estanteria_no'] == i) & (df['fecha_desaparicion'] != '')]
			dates = np.array(dff['fecha_desaparicion'], dtype=np.datetime64)
			dates = np.unique(dates)
			dates_sort = np.sort(dates, axis=0)
			dates_sort = list(pd.DatetimeIndex(dates_sort).year)
			dates_str = str(dates_sort[0]) + ' - ' + str(dates_sort[-1])
			ll.append(dates_str)
			fl = list(filter(None, list(df[df['estanteria_no'] == i].plato_no.unique())))
			ll.append(len(fl))
			for j in fl:
				fll = list(df[(df['estanteria_no'] == i) & (df['plato_no'] == j)].caja_no.unique())
				count += len(fll)
				caja_no += len(fll)
			ll.append(count)
			dd[i] = ll
		dd = OrderedDict(sorted(dd.items(), key = lambda t: t[0]))
		context['cases'] = dd
		context['files'] = total_files
		context['caja'] = caja_no
		
		df = df[df['fecha_desaparicion'] != '']
		dates = np.array(df['fecha_desaparicion'], dtype=np.datetime64)
		dates = np.unique(dates)
		dates = dates[2:]
		print(dates)
		counts = []
		for i in dates:
			counts.append(df[df['fecha_desaparicion'] == str(i)]['fecha_desaparicion'].count())
		def myconverter(o):
			if isinstance(o, datetime):
				return o.__str__()
		#context['x_first'] = pd.Series(dates).to_json(orient='values')
		context['x_first'] = json.dumps(np.datetime_as_string(dates).tolist())
		context['y_first'] = counts
		trace = go.Scatter(x=dates,
                   y=counts, line = dict(color = ('rgb(255,236,0)'),width = 4))
		data = [trace]
		layout = go.Layout(
    			title='Number of Missing People Over The Years',
    			xaxis=dict(
        			rangeselector=dict(
            				buttons=list([
                				dict(count=1,
                				     label='1m',
                				     step='month',
                				     stepmode='backward'),
                				dict(count=6,
                				     label='6m',
                				     step='month',
                				     stepmode='backward'),
                				dict(count=1,
                				    label='YTD',
                				    step='year',
                				    stepmode='todate'),
                				dict(count=1,
                				    label='1y',
                				    step='year',
                				    stepmode='backward'),
                				dict(step='all')
            				])
        				),
        			rangeslider=dict(
       	  			   visible = True
        		),
        		type='date'
    			),
			width = 800,
			height = 600,
			autosize=True
		)
		context['data_first'] = data
		context['layout_first'] = layout
		fig = dict(data=data, layout=layout)
		div = opy.plot(fig, auto_open=False, include_plotlyjs=True, output_type='div')
#		div_id = div.split('=')[1].split()[0].replace("'", "").replace('"', '')
#		js = '''
#		<script>
#
#		</script>'''.format(div_id=div_id)

		df_loc = pd.read_sql(
		"""
		SELECT departamento
		FROM gam_app_caso
		""", con=conn)
		df_loc = df_loc.dropna()
		ls = list(df_loc["departamento"])
		df_geo = pd.read_sql(
		"""
		SELECT Y(punto), X(punto), nombre_del_lugar
		FROM gam_app_lugar
		""", con=conn)
		df_geo = df_geo.dropna()
		lss = list(df_geo["nombre_del_lugar"])
		counts = []
		for i in lss:
			if ls.count(i) == 0:
				counts.append(1)
			else:
				counts.append(ls.count(i))
		df_geo["counts"] = counts
		#print(len(list(df_geo["Y(punto)"])))
		#print(len(list(df_geo["X(punto)"])))
		df_geo["text"] = df_geo["nombre_del_lugar"] + ' Number: ' + df_geo["counts"].astype(str)
		scl = [ [0,"rgb(255,255,0)"],[0.35,"rgb(255,215,0)"],[0.5,"rgb(245,222,179)"],\
    [0.6,"rgb(255,250,205)"],[0.7,"rgb(250,250,210)"],[1,"rgb(255,255,224)"] ]
		context["geo_lat"] = list(df_geo["Y(punto)"])
		context["geo_lon"] = list(df_geo["X(punto)"])
		context["geo_text"] = list(df_geo["text"])
		context["geo_counts"] = list(df_geo['counts'])
		context["geo_colorscale"] = scl
		context["geo_cmax"] = df_geo['counts'].max()
		context["center_lon"] = (df_geo["X(punto)"].min() + df_geo["X(punto)"].max())/2
		context["center_lat"] = (df_geo["Y(punto)"].min() + df_geo["Y(punto)"].max())/2
		data_geo = [ dict(
			type = 'scattergeo',
			#locationmode = 'ISO-3',
			#locations = list('GTM'),
			mode = 'markers',
			lat = list(df_geo["Y(punto)"]),
			lon = list(df_geo["X(punto)"]),
			text = list(df_geo["text"]),
			#textposition = ['top right', 'top left', 'top center', 'bottom right', 'top right', 'bottom left', 'top left', 'top center', 'bottom right', 'top left', 'top right', 'bottom right', 'top center', 'top right', 'top right'],
			marker = dict(
				size = 8, 
				opacity = 0.8,
				reversescale = True,
				autocolorscale = False,
				symbol = 'square',
				line = dict(
					width=1,
					color='rgba(102, 102, 102)'),
				colorscale = scl,
				cmin = 1,
				color = df_geo['counts'],
				cmax = df_geo['counts'].max(),
				colorbar=dict(
				title="Number of People")
			#	size = 7,
			#	opacity = 0.8,
			#	line = dict(width = 1),
			#	color = ['#bebada', '#fdb462', '#fb8072', '#d9d9d9', '#bc80bd', '#bebada', '#fdb462', '#fb8072', '#d9d9d9', '#bc80bd', '#bebada', '#fdb462', '#fb8072', '#d9d9d9', '#bc80bd']
			)


		)]
		#print(data_geo)
		layout_geo = dict(
			title = 'Missing People Locations',
			geo = dict(
				scope='north america',
				lonaxis = dict(range= [df_geo["X(punto)"].min()-1, df_geo["X(punto)"].max()+1]),
				lataxis = dict(range = [df_geo["Y(punto)"].min()-1, df_geo["Y(punto)"].max()+1]),
				showland = True,
				landcolor = "rgb(250, 250, 250)",
				subunitcolor = "rgb(217, 217, 217)",
				countrycolor = "rgb(217, 217, 217)",
				countrywidth = 0.5,
				subunitwidth = 0.5

			),
			width = 800,
			height = 600

		)
		context['data_geo'] = data_geo
		context['laytout_geo'] = layout_geo		
		fig_geo = dict(data=data_geo, layout=layout_geo)
		div_geo = opy.plot(fig_geo, auto_open=False, include_plotlyjs=True, output_type='div')
		df_age = pd.read_sql(
                """
                SELECT edad_en_el_momento
                FROM gam_app_persona
                """, con=conn)
		df_age = df_age.dropna()
		ll = list(df_age["edad_en_el_momento"])
		#print(ll)
		lis = []
		counts = []
		for i in ll:
			try:
			#except ValueError:
				if int(i.split(' ')[0]):
					lis.append(i.split(" ")[0])
			except ValueError:
				continue
		se = set(lis)
		sel = list(se)
		for i in sel:
			counts.append(lis.count(i))
		sell = list(map(int, sel))
		context['sell'] = sell
		context['count'] = counts
		trace = go.Scatter(
			x = sel,
			y = counts,
			mode = 'markers')
		layout = {"title": "Age vs Missing Numbers",
			"xaxis": {"title": "Age", },
			"yaxis": {"title": "Number of Missing People"}, 'width': 800, 'height': 600}
		figg = dict(data=[trace], layout=layout)
		div_age = opy.plot(figg, auto_open=False, output_type='div')
		df_gender = pd.read_sql(
		"""
		SELECT género
		FROM gam_app_persona
		"""
		, con=conn)
		df_gender = df_gender.dropna()
		ll = list(df_gender['género'])
		#print(ll)
		dd = {'masculino': 0, 'femenino': 0}
		for i in ll:
			if i.lower() == 'masculino' or i.lower() == 'm' or i.lower() == 'hombre':
				dd['masculino'] += 1
			elif i != '':
				dd['femenino'] += 1
		labels = ['Masculino', 'Femenino']
		values = [dd['masculino'], dd['femenino']]
		context['gender_data'] = [{'labels': labels, 'values': values, 'type': 'pie', 'marker': {'colors': ['rgb(255,236,0)', 'rgb(126,126,126)']}}]
#		context['gender_layout'] = {'title': 'Gender vs Missing People',
 #              'showlegend': true}
		fig = {
			'data': [{'labels': labels, 'values': values, 'type': 'pie', 'marker': {'colors': ['rgb(255,236,0)', 'rgb(126,126,126)']}}],
			'layout': {'title': 'Gender vs Missing People',
               'showlegend': True, 'width': 800, 'height': 600}

		}
		
		#tracess = go.Pie(labels=labels, values=values)
		#div_gender = opy.plot([tracess], auto_open=False, output_type='div')
		div_gender = opy.plot(fig, auto_open=False, output_type='div')
		#div_g, plotly_js = div_gender.split('<script type="text/javascript">')
		#my_js = '''
		#window.onresize = function() {
  #Plotly.relayout('{div_id}', {
   # width: 0.9 * window.innerWidth,
    #height: 0.9 * window.innerHeight
  #})
#}

#'''.format(div_id = div_g[9:45])
#		front, back = plotly_js.split('<\script>')
#		new_js = front + my_js + back
#		context['div_g'] = div_g
#		context['gender_js'] = new_js
		df_profession = pd.read_sql(
                """
                SELECT profesión
                FROM gam_app_persona
                """
                , con=conn)
		df_profession = df_profession.dropna()
		li = list(df_profession['profesión'])
		li = list(filter(lambda a: a != '', li))
		#print(li)
		se = list(set(li))
		cou = []
		for i in se:
			cou.append(li.count(i))
		se = list(map(str, se))
		context['se'] = se
		context['cou'] = cou
		layout = {"title": "Profession vs Missing Numbers",
			"yaxis": {"title": "Number Missing", },
			"xaxis": {"title": "Profession"}, 'width':800, 'height': 600}
		fig = go.Scatter(x=se, y = cou, line = dict(color = ('rgb(255,236,0)'),width = 4))
		context['data_pro'] = [fig]
		context['layout_pro'] = layout
		figg = dict(data=[fig], layout=layout)
		div_pro = opy.plot(figg, auto_open=False, output_type='div')
		context['graph'] = div
		context['geo'] = div_geo
		context['age'] = div_age
		context['gender'] = div_gender
		context['pro'] = div_pro
		return context

if __name__ == '__main__':
    app.run_server(debug=True, host='192.241.128.56', port=8000)
