import wx.xrc
import wx.dataview
import os
import funciones
import numpy as np
import csv
import xlsxwriter
from PIL import Image
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage, AnnotationBbox)
import scipy.ndimage
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
import matplotlib.pyplot as plt
import errno

#Crea una carpeta temporal para guardar algunos gráficos
try:
	os.mkdir('temp')
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

###########################################################################
## Se crea la GUI a partir de wxPython
###########################################################################

class MyFrame1(wx.Frame):

	def __init__(self, parent):
		wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"3D-RiR", pos=wx.DefaultPosition, size=wx.Size(1200, 630),
						  style=wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.TAB_TRAVERSAL)

		self.SetSizeHints(wx.Size(1200, 630), wx.DefaultSize)
		self.currentDirectory=os.getcwd()
		self.m_menubar1 = wx.MenuBar(0)
		self.m_menu1 = wx.Menu()

		self.m_menu11 = wx.Menu()
		self.m_menuItem5 = wx.MenuItem(self.m_menu11, wx.ID_ANY, u"Archivo Formato A", wx.EmptyString, wx.ITEM_NORMAL)
		self.m_menu11.Append(self.m_menuItem5)

		self.m_menuItem6 = wx.MenuItem(self.m_menu11, wx.ID_ANY, u"Archivo Formato B", wx.EmptyString, wx.ITEM_NORMAL)
		self.m_menu11.Append(self.m_menuItem6)

		self.m_menuItem81 = wx.MenuItem(self.m_menu11, wx.ID_ANY, u"Imagen de Planta", wx.EmptyString, wx.ITEM_NORMAL)
		self.m_menu11.Append(self.m_menuItem81)

		self.m_menu1.AppendSubMenu(self.m_menu11, u"Importar...")

		self.m_menu31 = wx.Menu()
		self.m_menuItem8 = wx.MenuItem(self.m_menu31, wx.ID_ANY, u"Excel(.xlsx)", wx.EmptyString, wx.ITEM_NORMAL)
		self.m_menu31.Append(self.m_menuItem8)

		self.m_menuItem9 = wx.MenuItem(self.m_menu31, wx.ID_ANY, u"CSV(.csv)", wx.EmptyString, wx.ITEM_NORMAL)
		self.m_menu31.Append(self.m_menuItem9)

		self.m_menu1.AppendSubMenu(self.m_menu31, u"Exportar...")

		self.m_menu1.AppendSeparator()

		self.m_menuItem4 = wx.MenuItem(self.m_menu1, wx.ID_ANY, u"Salir" + u"\t" + u"Ctrl+E", wx.EmptyString,
									   wx.ITEM_NORMAL)
		self.m_menu1.Append(self.m_menuItem4)

		self.m_menubar1.Append(self.m_menu1, u"Archivo")

		self.SetMenuBar(self.m_menubar1)

		bSizer2 = wx.BoxSizer(wx.VERTICAL)

		self.m_panel17 = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		self.m_panel17.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))

		bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

		bSizer9 = wx.BoxSizer(wx.VERTICAL)

		bSizer10 = wx.BoxSizer(wx.VERTICAL)

		sbSizer4 = wx.StaticBoxSizer(wx.StaticBox(self.m_panel17, wx.ID_ANY, u"Edición de audio"), wx.VERTICAL)

		bSizer17 = wx.BoxSizer(wx.HORIZONTAL)

		self.m_staticText5 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"Tamaño de ventana(ms)",
										   wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_staticText5.Wrap(-1)
		bSizer17.Add(self.m_staticText5, 1, wx.ALL, 5)

		self.m_textCtrl1 = wx.TextCtrl(sbSizer4.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
									   wx.DefaultSize, 0)
		bSizer17.Add(self.m_textCtrl1, 1, wx.ALL, 5)

		sbSizer4.Add(bSizer17, 1, wx.ALL | wx.EXPAND, 5)

		bSizer19 = wx.BoxSizer(wx.HORIZONTAL)

		self.m_staticText1 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"Sonido directo(ms)",
										   wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_staticText1.Wrap(-1)
		bSizer19.Add(self.m_staticText1, 1, wx.ALL, 5)

		self.m_textCtrl2 = wx.TextCtrl(sbSizer4.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
									   wx.DefaultSize, 0)
		bSizer19.Add(self.m_textCtrl2, 1, wx.ALL, 5)

		sbSizer4.Add(bSizer19, 1, wx.ALL | wx.EXPAND, 5)

		bSizer11 = wx.BoxSizer(wx.HORIZONTAL)

		self.m_staticText3 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"Solapamiento", wx.DefaultPosition,
										   wx.DefaultSize, 0)
		self.m_staticText3.Wrap(-1)
		bSizer11.Add(self.m_staticText3, 1, wx.ALL, 5)

		m_choice2Choices = [u"Ninguno", u"25%", u"50%"]
		self.m_choice2 = wx.Choice(sbSizer4.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
								   m_choice2Choices, 0)
		self.m_choice2.SetSelection(0)
		bSizer11.Add(self.m_choice2, 1, wx.ALL, 5)

		sbSizer4.Add(bSizer11, 1, wx.ALL | wx.EXPAND, 5)

		bSizer12 = wx.BoxSizer(wx.HORIZONTAL)

		self.m_staticText4 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"Filtro pasa bajo", wx.DefaultPosition,
										   wx.DefaultSize, 0)
		self.m_staticText4.Wrap(-1)
		bSizer12.Add(self.m_staticText4, 2, wx.ALL, 5)

		self.m_radioBtn1 = wx.RadioButton(sbSizer4.GetStaticBox(), wx.ID_ANY, u"Si", wx.DefaultPosition, wx.DefaultSize,
										  0)
		bSizer12.Add(self.m_radioBtn1, 1, wx.ALL, 5)

		self.m_radioBtn2 = wx.RadioButton(sbSizer4.GetStaticBox(), wx.ID_ANY, u"No", wx.DefaultPosition, wx.DefaultSize,
										  0)
		self.m_radioBtn2.SetValue(True)
		bSizer12.Add(self.m_radioBtn2, 1, wx.ALL, 5)

		sbSizer4.Add(bSizer12, 1, wx.ALL | wx.EXPAND, 5)

		bSizer13 = wx.BoxSizer(wx.HORIZONTAL)

		self.m_staticText51 = wx.StaticText(sbSizer4.GetStaticBox(), wx.ID_ANY, u"Threshold", wx.DefaultPosition,
											wx.DefaultSize, 0)
		self.m_staticText51.Wrap(-1)
		bSizer13.Add(self.m_staticText51, 1, wx.ALL, 5)

		m_choice3Choices = [u"-5dB", u"-10dB", u"-20dB", u"-30dB", u"-40dB", u"-50dB", u"-60dB"]
		self.m_choice3 = wx.Choice(sbSizer4.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
								   m_choice3Choices, 0)
		self.m_choice3.SetSelection(6)
		bSizer13.Add(self.m_choice3, 1, wx.ALL, 5)

		sbSizer4.Add(bSizer13, 1, wx.ALL | wx.EXPAND, 5)

		m_choice6Choices = [u"Formato A", u"Formato B"]
		self.m_choice6 = wx.Choice(sbSizer4.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
								   m_choice6Choices, 0)
		self.m_choice6.SetSelection(0)
		self.m_choice6.Hide()

		sbSizer4.Add(self.m_choice6, 0, wx.ALL, 5)

		bSizer10.Add(sbSizer4, 0, wx.ALL | wx.EXPAND, 5)

		bSizer9.Add(bSizer10, 0, wx.EXPAND, 5)

		self.m_button6 = wx.Button(self.m_panel17, wx.ID_ANY, u"Calcular 3D RiR", wx.DefaultPosition, wx.Size(-1, -1),
								   0)
		self.m_button6.SetMinSize(wx.Size(-1, 40))
		self.m_button6.SetMaxSize(wx.Size(-1, 40))

		bSizer9.Add(self.m_button6, 0, wx.ALL | wx.EXPAND , 5)

		bSizer6.Add(bSizer9, 2, wx.EXPAND, 5)
		"""self.m_panel2 = wx.Panel(self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		bSizer3 = wx.BoxSizer(wx.VERTICAL)

		bSizer3.Add(self.m_dataViewListCtrl1, 2, wx.EXPAND, 5)

		gSizer5 = wx.GridSizer(2, 2, 5, 5)

		self.m_button1 = wx.Button(self.m_panel2, wx.ID_ANY, u"Seleccionar todo", wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_button1.SetDefault()
		gSizer5.Add(self.m_button1, 0, wx.ALL | wx.EXPAND, 5)

		self.m_button2 = wx.Button(self.m_panel2, wx.ID_ANY, u"Deseleccionar todo", wx.DefaultPosition, wx.DefaultSize,
								   0)
		gSizer5.Add(self.m_button2, 0, wx.ALL | wx.EXPAND, 5)

		self.m_button3 = wx.Button(self.m_panel2, wx.ID_ANY, u"Agregar Medicion", wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_button3.SetDefault()
		gSizer5.Add(self.m_button3, 0, wx.ALL | wx.EXPAND, 5)

		self.m_button4 = wx.Button(self.m_panel2, wx.ID_ANY, u"Borrar medicion", wx.DefaultPosition, wx.DefaultSize, 0)
		gSizer5.Add(self.m_button4, 0, wx.ALL | wx.EXPAND, 5)

		bSizer3.Add(gSizer5, 1, wx.EXPAND, 5)

		self.m_panel2.SetSizer(bSizer3)
		self.m_panel2.Layout()
		bSizer3.Fit(self.m_panel2)
		self.m_notebook2.AddPage(self.m_panel2, u"Lista de Mediciones", False)"""
		self.m_dataViewListCtrl1 = wx.dataview.DataViewListCtrl(self, wx.ID_ANY, wx.DefaultPosition,
																wx.Size(-1, -1), wx.dataview.DV_MULTIPLE)
		self.m_dataViewListCtrl1.Hide()
		self.m_dataViewListColumn2 = self.m_dataViewListCtrl1.AppendTextColumn(u"Mediciones")

		self.m_notebook1 = wx.Notebook(self.m_panel17, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_panel4 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		bSizer4 = wx.BoxSizer(wx.VERTICAL)

		self.m_notebook3 = wx.Notebook(self.m_panel4, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_panel7 = wx.Panel(self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		self.m_notebook3.AddPage(self.m_panel7, u"Presión Sonora", True)
		self.m_panel9 = wx.Panel(self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		self.m_notebook3.AddPage(self.m_panel9, u"Ventanas", False)
		self.m_panel12 = wx.Panel(self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		self.m_notebook3.AddPage(self.m_panel12, u"Vista de planta", False)
		bSizer_planta = wx.BoxSizer(wx.VERTICAL)
		fig, ax = plt.subplots()
		self.canvas_planta = FigureCanvas(self.m_panel12, -1, fig)
		self.canvas_planta.Hide()
		bSizer_planta.Add(self.canvas_planta, 1, wx.EXPAND | wx.ALL, 5)
		self.m_panel12.SetSizer(bSizer_planta)
		self.m_panel12.Layout()
		bSizer_planta.Fit(self.m_panel12)
		self.m_panel13 = wx.Panel(self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		bSizer5 = wx.BoxSizer(wx.VERTICAL)

		self.m_dataViewListCtrl2 = wx.dataview.DataViewListCtrl(self.m_panel13, wx.ID_ANY, wx.DefaultPosition,
																wx.DefaultSize,
																wx.dataview.DV_HORIZ_RULES | wx.dataview.DV_ROW_LINES | wx.dataview.DV_SINGLE | wx.dataview.DV_VARIABLE_LINE_HEIGHT | wx.dataview.DV_VERT_RULES | wx.VSCROLL)


		self.m_dataViewListColumn1 = self.m_dataViewListCtrl2.AppendTextColumn(u"N°")
		self.m_dataViewListColumn2 = self.m_dataViewListCtrl2.AppendTextColumn(u"Tiempo(ms)")
		self.m_dataViewListColumn3 = self.m_dataViewListCtrl2.AppendTextColumn(u"Magnitud(dB)")
		self.m_dataViewListColumn4 = self.m_dataViewListCtrl2.AppendTextColumn(u"Azimuth(°)")
		self.m_dataViewListColumn5 = self.m_dataViewListCtrl2.AppendTextColumn(u"Elevación(°)")
		bSizer5.Add(self.m_dataViewListCtrl2, 1, wx.ALL | wx.EXPAND , 5)

		self.m_panel13.SetSizer(bSizer5)
		self.m_panel13.Layout()
		bSizer5.Fit(self.m_panel13)
		self.m_notebook3.AddPage(self.m_panel13, u"Data", False)

		bSizer4.Add(self.m_notebook3, 1, wx.EXPAND | wx.ALL, 5)

		self.m_panel4.SetSizer(bSizer4)
		self.m_panel4.Layout()
		bSizer4.Fit(self.m_panel4)
		self.m_notebook1.AddPage(self.m_panel4, u"Parámetros", True)
		self.m_panel5 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		bSizer14 = wx.BoxSizer(wx.VERTICAL)

		bSizer15 = wx.BoxSizer(wx.VERTICAL)

		self.m_panel171 = wx.Panel(self.m_panel5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
		bSizer29 = wx.BoxSizer(wx.VERTICAL)

		fig, ax = plt.subplots()
		self.canvas2d = FigureCanvas(self.m_panel171, -1, fig)
		self.toolbar2d = NavToolbar(self.canvas2d)

		self.canvas2d.Hide()
		self.toolbar2d.Hide()

		bSizer29.Add(self.toolbar2d, flag=wx.GROW, proportion=0)
		bSizer29.Add(self.canvas2d, flag=wx.GROW, proportion=1)

		self.m_panel171.SetSizerAndFit(bSizer29)

		bSizer15.Add( self.m_panel171, 1, wx.EXPAND |wx.ALL, 5 )

		bSizer14.Add(bSizer15, 1, wx.EXPAND, 5)

		bSizer16 = wx.BoxSizer(wx.HORIZONTAL)

		sbSizer3 = wx.StaticBoxSizer(wx.StaticBox(self.m_panel5, wx.ID_ANY, u"Parámetros medición"), wx.VERTICAL)

		bSizer171 = wx.BoxSizer(wx.HORIZONTAL)

		self.m_staticText10 = wx.StaticText(sbSizer3.GetStaticBox(), wx.ID_ANY, u"Escala de medición (<1)",
											wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_staticText10.Wrap(-1)
		bSizer171.Add(self.m_staticText10, 1, wx.ALL, 5)

		self.m_textCtrl3 = wx.TextCtrl(sbSizer3.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
									   wx.DefaultSize, 0)
		bSizer171.Add(self.m_textCtrl3, 0, wx.ALL, 5)
		self.m_staticline2 = wx.StaticLine(sbSizer3.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
										   wx.LI_HORIZONTAL | wx.LI_VERTICAL)
		bSizer171.Add(self.m_staticline2, 0, wx.EXPAND | wx.ALL, 5)

		self.m_staticText11 = wx.StaticText(sbSizer3.GetStaticBox(), wx.ID_ANY, u"Ángulo de medición (°)",
											wx.DefaultPosition, wx.DefaultSize, 0)
		self.m_staticText11.Wrap(-1)
		bSizer171.Add(self.m_staticText11, 1, wx.ALL, 5)

		self.m_textCtrl4 = wx.TextCtrl(sbSizer3.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
									   wx.DefaultSize, 0)
		bSizer171.Add(self.m_textCtrl4, 0, wx.ALL, 5)

		self.m_staticline3 = wx.StaticLine(sbSizer3.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
										   wx.LI_HORIZONTAL | wx.LI_VERTICAL)
		bSizer171.Add(self.m_staticline3, 0, wx.EXPAND | wx.ALL, 5)

		self.m_button61 = wx.Button(sbSizer3.GetStaticBox(), wx.ID_ANY, u"Actualizar", wx.DefaultPosition,
									wx.DefaultSize, 0)
		bSizer171.Add(self.m_button61, 1, wx.ALL, 5)

		sbSizer3.Add(bSizer171, 1, wx.EXPAND, 5)

		bSizer16.Add(sbSizer3, 1, wx.ALL | wx.EXPAND, 5)

		bSizer14.Add(bSizer16, 0, wx.EXPAND, 5)

		self.m_panel5.SetSizer(bSizer14)
		self.m_panel5.Layout()
		bSizer14.Fit(self.m_panel5)
		self.m_notebook1.AddPage(self.m_panel5, u"Vista 2D", False)


		self.m_panel6 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)


		self.m_notebook1.AddPage(self.m_panel6, u"Vista 3D", False)

		bSizer6.Add(self.m_notebook1, 5, wx.EXPAND, 5)

		self.m_panel17.SetSizer(bSizer6)
		self.m_panel17.Layout()
		bSizer6.Fit(self.m_panel17)
		bSizer2.Add(self.m_panel17, 1, wx.EXPAND, 5)

		self.SetSizer(bSizer2)
		self.Layout()
		self.canvas2d.d = 0
		self.canvas2d.x = 0
		self.canvas2d.y = 0
		self.Centre(wx.BOTH)

		self.importado=0

		# Connect Events

		self.Bind(wx.EVT_MENU, self.abrirImagen, id=self.m_menuItem81.GetId())
		self.Bind(wx.EVT_MENU, self.formatoA, id=self.m_menuItem5.GetId())
		self.Bind(wx.EVT_MENU, self.formatoB, id=self.m_menuItem6.GetId())
		self.Bind(wx.EVT_MENU, self.onClose, id=self.m_menuItem4.GetId())
		self.Bind(wx.EVT_MENU, self.exportar_csv, id=self.m_menuItem9.GetId())
		self.Bind(wx.EVT_MENU, self.exportar_excel, id=self.m_menuItem8.GetId())
		self.m_button6.Bind(wx.EVT_BUTTON, self.procesamientoSenales)
		self.m_button61.Bind(wx.EVT_BUTTON, self.actualizarPlot)
		self.canvas2d.figure.canvas.mpl_connect('motion_notify_event', self.onMotion)
		self.canvas2d.Bind(wx.EVT_LEFT_DOWN, self.MouseDown)
		self.canvas2d.Bind(wx.EVT_LEFT_UP, self.MouseUp)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.timer = wx.Timer(self.canvas2d)
		self.timer.Start(10)
		self.canvas2d.Bind(wx.EVT_TIMER, self.on_timer, self.timer)

	def __del__(self):
		pass

	# Función para seleccionar los 4 archivos correspondientes a los canales ambisonic.
	# Cada archivo debe tener el nombre del canal al final.
	def abrirArchivo(self, event):

		wildcard = "wav (*.wav)|*.wav|" \
				   "All files (*.*)|*.*"

		"""
		Create and show the Open FileDialog
		"""
		dlg = wx.FileDialog(
			self, message="Elegir archivos",
			defaultDir=self.currentDirectory,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR
		)
		paths=[]
		if dlg.ShowModal() == wx.ID_OK:
			paths = dlg.GetPaths()
			self.m_dataViewListCtrl1.DeleteAllItems()
			for i in range(len(paths)):
				self.m_dataViewListCtrl1.AppendItem([paths[i]])

			self.m_dataViewListCtrl1.SelectAll()

		dlg.Destroy()

		return len(paths)

	#Función que procesa la señal ambisonic en formato A

	def formatoA(self,event):

		archivos_audio=self.abrirArchivo(event)
		self.m_choice6.SetSelection(1)
		if archivos_audio>0:
			self.procesamientoSenales(event)

	#Función que procesa la señal ambisonic en formato B(no hace la conversión A-B)

	def formatoB(self,event):
		archivos_audio = self.abrirArchivo(event)
		self.m_choice6.SetSelection(0)

		if archivos_audio >0:

			self.procesamientoSenales(event)

	#Función que realiza tod el procsesamiento de las señales importadas
	#Llama a las siguientes funciones:
	#ConversorAtoB: Realiza la conversión de formato A a B
	#FiltroPB: Se aplica el filtro pasa-altos en 5KHz
	#RecortarSenal: Se recorta la señal desde el sonido directo
	#IntensidadModoDirecto: Realiza el cambio de presión a intensidad de las señales
	# y las ventanea a partir del tamaño de ventana elegida por el usuario
	#IntensidadSonidoDirecto: Realiza el cambio de presión a intensidad de la
	# la porción de señal que representa el sonido directo.
	#Concatenear: Concatena los valores de intensidad obtenidos para el sonido directo y las reflexiones.
	#Normalizar: Normaliza todos los vectores de intensidad respecto al de sonido directo.
	# Ploteo3D: Hace el ploteo 3D de la señal.
	# Ploteo2D: Hace el ploteo 2D de la señal.
	# Ploteo_presion: Hace el ploteo de la presión sonora del canal W con el límite del sonido directo marcado.
	# Ploteo_ventanas: Hace el ploteo de la presión sonora del canal W con los puntos donde se tomó cada ventana.

	def procesamientoSenales(self,event):

		formatoA=self.m_choice6.GetSelection()

		fs=0
		mediciones=[]
		senales=[self.m_dataViewListCtrl1.GetValue(i,0) for i in range(self.m_dataViewListCtrl1.GetItemCount())]

		try:
			fs, mediciones = funciones.conversorAtoB(senales,formatoA)
		except:
			wx.MessageDialog(
				None,
				('Seleccione los 4 archivos Ambisonic con formato: "nombrearchivo_Canal.wav'),
				('Error!'),
				wx.OK
			).ShowModal()

		seleccion_sonido_directo = self.m_textCtrl2.GetValue()

		if seleccion_sonido_directo=='':
			seleccion_sonido_directo=funciones.sonidoDirecto(mediciones,fs)
			seleccion_sonido_directo=seleccion_sonido_directo[0]
		seleccion_sonido_directo=float(seleccion_sonido_directo)

		tamanio_ventana = self.m_textCtrl1.GetValue()
		if tamanio_ventana == '':
			tamanio_ventana = seleccion_sonido_directo
		tamanio_ventana = float(tamanio_ventana)

		muestras_ventana=int((tamanio_ventana/1000)*fs)
		muestras_sonido_directo=int((seleccion_sonido_directo/1000)*fs)

		if not self.m_radioBtn2.GetValue():

			mediciones=funciones.filtroPB(mediciones, fs)

		mediciones_recortadas = funciones.recortarSenal(mediciones)

		solapamiento=self.m_choice2.GetSelection()
		parametros_reflexiones, cantidad_ventanas = funciones.intensidadModoDirecto(mediciones_recortadas, muestras_sonido_directo,
																 muestras_ventana, solapamiento)

		parametros_sonido_directo = funciones.intensidadSonidoDirecto(mediciones_recortadas, muestras_sonido_directo)

		parametros_completos=funciones.concatenar(parametros_sonido_directo,parametros_reflexiones)

		thresholds=[-5, -10, -20, -30, -40, -50, -60]
		threshold= thresholds[self.m_choice3.GetSelection()]

		parametros_normalizados=funciones.normalizar(parametros_completos, threshold)

		largo_senial_reflexiones = float(len(mediciones[0][0][muestras_sonido_directo:]) / fs)
		cantidad_ventanas = len(parametros_reflexiones[0][0])

		t = np.linspace(largo_senial_reflexiones / cantidad_ventanas, largo_senial_reflexiones +
						largo_senial_reflexiones / cantidad_ventanas, cantidad_ventanas)


		# Se muestran los datos obtenidos en la tabla de la pestaña "Data"
		self.m_dataViewListCtrl2.DeleteAllItems()
		self.m_dataViewListCtrl2.AppendItem(["Sonido Directo"
												, "{:.2f}".format(0)
												, "{:.1f}".format(parametros_normalizados[0][4][0])
												, "{:.1f}".format(parametros_sonido_directo[0][4][0]*180/np.pi)
												, "{:.1f}".format(parametros_sonido_directo[0][5][0]*180/np.pi)])
		for senales in parametros_reflexiones:
			for i in range(len(senales[0])):
				self.m_dataViewListCtrl2.AppendItem([str(i + 1)
														, "{:.2f}".format(t[i] * 1000)
														, "{:.1f}".format(parametros_normalizados[0][4][i+1])
														, "{:.1f}".format(senales[4][i]*180/np.pi)
														, "{:.1f}".format(senales[5][i]*180/np.pi)])

		W, H = self.m_panel6.GetSize()
		plot_3d=funciones.ploteo3d(parametros_normalizados, largo_senial_reflexiones, seleccion_sonido_directo, W, H)
		self.ploteo3d(plot_3d[0])

		funciones.ploteo2d(parametros_normalizados, largo_senial_reflexiones, seleccion_sonido_directo)
		if(self.importado):
			self.ploteo2d()

		W, H = self.m_panel7.GetSize()
		ploteo_presion = funciones.ploteo_presion(fs, mediciones_recortadas,seleccion_sonido_directo,W,H)
		self.ploteo_pre_son(ploteo_presion[0])

		ploteo_ventaneo = funciones.ploteo_ventanas(fs, mediciones_recortadas,tamanio_ventana, W, H)
		self.ploteo_vent(ploteo_ventaneo[0])

	#Función que le permite al usuario elegir una imagen de planta y la coloca en las pestañas
	# "Floor Plan" y "Vista 2D" de la GUI

	def abrirImagen(self, event):
		filepath=[]
		"""
			Browse for file
			"""
		wildcard = "JPEG files (*.jpg)|*.jpg"
		dialog = wx.FileDialog(
			self, message="Elegir archivos",
			defaultDir=self.currentDirectory,
			defaultFile="",
			wildcard=wildcard,
			style=wx.FD_OPEN)
		if dialog.ShowModal() == wx.ID_OK:
			filepath=dialog.GetPath()
		imagen_planta =Image.open(filepath)
		self.img_W, self.img_H=imagen_planta.size
		self.canvas2d.Show()
		self.importado=1
		self.toolbar2d.Show()
		ax=self.canvas2d.figure.get_axes()
		ax=ax[0]
		ax.imshow(imagen_planta)
		if not os.path.isdir('temp'):
			self.ploteo2d()
		self.canvas2d.draw()

		self.canvas_planta.Show()
		ax = self.canvas_planta.figure.get_axes()
		ax = ax[0]
		ax.imshow(imagen_planta)
		self.canvas_planta.draw()

		dialog.Destroy()

	#Función que cierra la GUI y borra la carpeta temporal

	def onClose(self, event):
		self.timer.Stop()
		self.Close()
		self.Destroy()




	#Función que llama a la figura con el ploteo 3D de la medición y la coloca en la
	# pestaña "Vista 3D" de la GUI


	def ploteo3d(self, figura):
		try:
			self.canvas3d.Destroy()
			self.toolbar.Destroy()
		except:
			pass
		self.canvas3d = FigureCanvas(self.m_panel6, -1, figura)
		self.toolbar = NavToolbar(self.canvas3d)


		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.toolbar, flag=wx.GROW, proportion=0)
		self.sizer.Add(self.canvas3d, flag=wx.GROW, proportion=1)
		self.m_panel6.SetSizerAndFit(self.sizer)

	# Función que llama a la figura con el ploteo de la presión sonora del canal W
	# de la medición con el sonido directo marcado y la coloca en la pestaña "Presión Sonora" de la GUI

	def ploteo_pre_son(self,figura):
		try:
			self.canvas_parametro.Destroy()

		except:
			pass

		self.canvas_parametro = FigureCanvas(self.m_panel7, -1, figura)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.canvas_parametro, flag=wx.GROW, proportion=1)
		self.m_panel7.SetSizer(self.sizer)

	# Función que llama a la figura con el ploteo de la presión sonora del canal W
	# de la medición con las ventanas marcadas y la coloca en la pestaña "Presión Sonora" de la GUI

	def ploteo_vent(self,figura):
		try:
			self.canvas_ventaneo.Destroy()

		except:
			pass

		self.canvas_ventaneo = FigureCanvas(self.m_panel9, -1, figura)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas_ventaneo, flag=wx.GROW, proportion=1)
		self.m_panel9.SetSizer(sizer)

	# Función que llama a la figura con el ploteo 2D de la medición y la coloca en la pestaña
	#"Vista 2D" de la GUI

	def ploteo2d(self):

		self.canvas2d.Show()
		self.toolbar2d.Show()
		self.imagen_2d = Image.open(self.currentDirectory+"/temp/ploteo2d.png")
		self.imagen_2d.thumbnail((int(self.img_W/2), int(self.img_H/2)), Image.NEAREST)
		ax = self.canvas2d.figure.get_axes()
		ax=ax[0]
		xy = [int(self.img_W/2), int(self.img_H/2)]
		self.imagebox = OffsetImage(self.imagen_2d, zoom=1)

		self.imagebox.image.axes = ax
		try:
			self.ab.remove()
		except:
			pass

		self.ab = AnnotationBbox(self.imagebox, xy,
							xybox=(0., 0.),
							xycoords='data',
							boxcoords="offset points",
							pad=0.1,
							frameon = False
							)


		ax.add_artist(self.ab)

		self.canvas2d.draw()

	#Función que actualiza el gráfico en 2D que se ve en la petaña "Vista 2D" de la GUI.
	#Se llama cada vez que el usuario cambia posición y escala de medición y presiona "Actualizar".
	#Las funciones subsiguientes sirven para moverl el gráfico sobre la imagen de planta con el mouse.

	def actualizarPlot(self,e):


		ratio=self.m_textCtrl3.GetValue()
		angulo=self.m_textCtrl4.GetValue()

		if ratio=='':
			ratio=self.imagebox.get_zoom()

		if angulo=='':
			angulo=0


		self.imagen_2d=scipy.ndimage.rotate(self.imagen_2d,float(angulo))
		self.imagebox.set_zoom(zoom=float(ratio))
		self.imagebox.set_data(self.imagen_2d)


		self.canvas2d.draw()

	def on_timer(self, event):

		if self.canvas2d.d == 1:
			self.ab.xy[0] = self.canvas2d.x
			self.ab.xy[1] = self.canvas2d.y
		else:
			pass

		self.canvas2d.draw()

	def onMotion(self, evt):
		if (self.canvas2d.d == 1):
			xdata = evt.xdata
			ydata = evt.ydata
			self.canvas2d.x = xdata
			self.canvas2d.y = ydata
		else:
			pass

	def MouseUp(self, e):
		self.canvas2d.d = 0

	def MouseDown(self, e):
		self.canvas2d.d = 1

	#Función para exportar a un archivo CSV los datos que se encuentran en la tabla de "Data" de la GUI

	def exportar_csv(self,e):
		wildcard = "csv (*.csv)|*.csv"

		dialog = wx.FileDialog(
			self, message="Elegir archivos",
			defaultDir=self.currentDirectory,
			defaultFile="Datos Medición",
			wildcard=wildcard,
			style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

		if dialog.ShowModal() == wx.ID_OK:
			paths = dialog.GetPath()

			with open(paths, mode='w', newline='') as data_espina:

				data = csv.writer(data_espina, delimiter = ',')
				filas=self.m_dataViewListCtrl2.GetItemCount()
				columnas=self.m_dataViewListCtrl2.GetColumnCount()

				data.writerow(['N° Ventana', 'Tiempo(ms)','Magnitud(dB)', 'Azimuth(°)', 'Elevación(°)'])
				for i in range(filas):
					datos_espina=[]
					for j in range(columnas):

						dato=self.m_dataViewListCtrl2.GetValue(i, j)
						datos_espina.append(dato)
					data.writerow(datos_espina)

		dialog.Destroy()

	#Función para exportar a un archivo Excel los datos que se encuentran en la tabla de "Data" de la GUI

	def exportar_excel(self,e):
		wildcard = "Excel (*.xlsx)|*.xlsx"

		dialog = wx.FileDialog(
			self, message="Elegir archivos",
			defaultDir=self.currentDirectory,
			defaultFile="Datos Medición",
			wildcard=wildcard,
			style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

		if dialog.ShowModal() == wx.ID_OK:
			paths = dialog.GetPath()

			workbook = xlsxwriter.Workbook(paths)
			worksheet = workbook.add_worksheet()


			filas = self.m_dataViewListCtrl2.GetItemCount()
			columnas = self.m_dataViewListCtrl2.GetColumnCount()

			worksheet.write_row('A1',['N°', 'Tiempo(ms)', 'Magnitud(dB)', 'Azimuth(°)', 'Elevación(°)'])
			for i in range(filas):
				for j in range(columnas):
					dato = self.m_dataViewListCtrl2.GetValue(i, j)
					worksheet.write(i+1,j,dato)
			workbook.close()
		dialog.Destroy()

class NavToolbar(NavigationToolbar):
# only display the buttons we need
	toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ('Home','Save')]