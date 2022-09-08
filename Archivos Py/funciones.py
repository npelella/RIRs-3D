import pathlib

import scipy as sp
import re
from scipy.fft import fft, ifft
import numpy as np
import mplcursors
import matplotlib.pyplot as plt
import soundfile as sf
import os
from scipy.signal import kaiserord, firwin, lfilter

np.seterr(divide='ignore', invalid='ignore')


#Realiza la conversión de formato A a B de los archivos Ambisonic.
#Utiliza la función filtroConversor para aplicar el filtro de corrección espacial.
def conversorAtoB(archivos_audio,formatoA):

    archivos_audio.sort()
    valores_normalizados = []
    mediciones = []
    valores_nonorm = []
    fs = 0

    # Se obtienen los datos de los archivos
    for archivo in archivos_audio:
        data, fs = sf.read(archivo, dtype='int32')
        valores_nonorm.append(data)

    maxW = max(valores_nonorm[0])
    maxX = max(valores_nonorm[1])
    maxY = max(valores_nonorm[2])
    maxZ = max(valores_nonorm[3])
    maxCompleto = max([maxW, maxX, maxY, maxZ])

    for i in range(len(valores_nonorm)):
        valores_normalizados.append(valores_nonorm[i] / maxCompleto)

    for i in range(0, len(valores_normalizados), 4):
       mediciones.append(valores_normalizados[i:i + 4])

    #Si los archivos son formato A hace la conversión y aplica el filtro
    if(formatoA):

        for i in range(len(mediciones)):

            bld= mediciones[i][0]
            bru= mediciones[i][1]
            flu = mediciones[i][2]
            frd = mediciones[i][3]

            mediciones[i][0] = flu+frd+bld+bru
            mediciones[i][1] = flu+frd-bld-bru
            mediciones[i][2] = flu-frd+bld-bru
            mediciones[i][3] = flu-frd-bld+bru

        mediciones=filtradoConversor(mediciones,fs)

    #Se devuelve la frecuencia de muestreo y un array con todos los datos de la señal.
    return fs,mediciones

#Selecciona la porción de la señal que podría represetar el sonido directo como el primer mínimo
#despues del primer máximo
def sonidoDirecto(senales,fs):
    sonidos_directos=[]

    for medicion in senales:
        comienzo_sonido_directo=np.argmax(medicion[0]) #Se encuntra la posición el máximo
        fin_sonido_directo=np.argmin(medicion[0][comienzo_sonido_directo:]) #Se encuentra la posición del mínimo
        sonido_directo=((fin_sonido_directo+comienzo_sonido_directo)/fs)*1000 #Se pasa a ms

        sonidos_directos.append(sonido_directo)

    return sonidos_directos

#Filtro de corrección para la conversión A to B.
def filtradoConversor(senales, fs):

    c = 340
    r = 0.01
    tao = r / c
    mediciones_filtradas = []
    for medicion in senales:
        senales_filtradas = []
        for i, canal in enumerate(medicion):
            N = len(canal)
            deltaf = fs / N
            f = np.arange(0, fs / 2, deltaf)  # freq vector con pasos deltaf
            w = 2 * np.pi * f

            if N % 2 != 0:
                canal.append(0)

            # fft signal
            signal_fft = (sp.fft.fft(canal))

            # filtro w fft
            fw_ = (1 + 1j * w * tao - 0.3333 * w ** 2 * tao ** 2) / (1 + 0.3333 * 1j * w * tao)
            fw_1 = np.flip(fw_)
            fw = np.concatenate((fw_, fw_1))

            # filtro xyz  fft
            f_xyz = np.sqrt(6) * ((1 + (0.3333 * 1j * w * tao) - (0.3333 * w ** 2 * tao ** 2)) / (1 + (0.3333 * 1j * w * tao)))
            f_1 = np.flip(f_xyz)
            f_xyz = np.concatenate((f_xyz, f_1))

            if i==0:
                # filtrado
                w_filt = signal_fft * fw
                s_filtered = np.real(sp.fft.ifft(w_filt))
                s_filtered = (s_filtered) / max(s_filtered)

            else:
                # filtrado
                xyz_filt = signal_fft * f_xyz
                s_filtered = np.real(sp.fft.ifft(xyz_filt))
                s_filtered = (s_filtered) / max(s_filtered)

            senales_filtradas.append(s_filtered)
        mediciones_filtradas.append(senales_filtradas)

    return mediciones_filtradas

#Se recorta la sañel a partir de donde comienza el sonido directo.
def recortarSenal(senales):
    mediciones_recortadas=[]
    for medicion in senales:
        canales_recortado=[]
        maximo_canal=np.argmax(medicion, axis=1 ) #Se encuentra la posición del máximo de los 4 canales
        maximo_total=np.min(maximo_canal) #Se utiliza el máximo más "temprano".
        for canal in medicion:

            canal_recortado=canal[maximo_total:] #Se recortan todas las señales a partir de este máximo
            canales_recortado.append(canal_recortado)
        mediciones_recortadas.append(canales_recortado)
    return mediciones_recortadas

#Se aplica un filtro pasa bajos a las señales a partir de los 5KHz
def filtroPB(senales, fs):
    rate_nyquist=fs/2
    transicion=5/rate_nyquist
    ripple_db=60
    N, beta= kaiserord(ripple_db, transicion)
    taps= firwin(N,5000/rate_nyquist, window=('kaiser',beta)) #Se crea el filtro
    mediciones_filtradas=[]
    for medicion in senales:
        mediciones_filtradas.append(lfilter(taps,1,medicion)) #Se aplica a las señales

    return mediciones_filtradas

#Ventaneo de la señal teniendo en cuenta el tipo de solapamiento que se eligió
def ventaneoSenal(senales,muestras_ventana, solapamiento):

    cantidad_ventanas=0
    medicion_ventaneada = []
    segmentos_canal=[]
    for canal in senales:
        canal_ventaneado=[]
        if (len(canal)%muestras_ventana)!=0:   #Se agregan muestras para obtener ventanas enteras
            canal=np.pad(canal, (0, muestras_ventana-len(canal)%muestras_ventana), 'constant')
        if solapamiento==0:   #Sin solapamiento
            cantidad_ventanas = int(len(canal) / muestras_ventana)
            segmentos_canal=np.split(canal, cantidad_ventanas)
        if solapamiento==1:   #25% Solapamiento
            cantidad_ventanas= int(np.ceil(4 * (int(len(canal) / muestras_ventana))/3 - 1))
            segmentos_canal= [canal[i : i + muestras_ventana] for i in range(0, len(canal), int(muestras_ventana / 4))]
        if solapamiento == 2:   #50% Solapamiento
            cantidad_ventanas = 2 * (int(len(canal) / muestras_ventana)) - 1
            segmentos_canal = [canal[i: i + muestras_ventana] for i in
                                   range(0, len(canal), int(muestras_ventana / 2))]
        for i in range(0, cantidad_ventanas):
            canal_ventaneado.append(segmentos_canal[i])
        medicion_ventaneada.append(canal_ventaneado)

    return cantidad_ventanas,medicion_ventaneada

#Se calculan los valores de intensidad, así como las coordenadas esféricas de la parte de la señal que representa
# las reflexiones
def intensidadModoDirecto(senales, sonido_directo, muestras_ventana, solapamiento):
    directorX_refelxiones = []
    directorY_refelxiones = []
    directorZ_refelxiones = []
    radio_reflexiones = []
    azymuth_reflexiones = []
    elevation_reflexiones = []
    parametros_senales=[]
    reflexiones_senial=[]
    cantidad_ventanas=0
    for medicion in senales:
        for i, canal in enumerate(medicion):
            reflexiones_senial.append(medicion[i][sonido_directo+1:])
        cantidad_ventanas,medicion_ventaneada=ventaneoSenal(reflexiones_senial, muestras_ventana, solapamiento) #Se aplica ventaneo
        medicion_ventaneada = np.asarray(medicion_ventaneada)
        for j in range(0, cantidad_ventanas):
            #Calculo de vectores de intensidad
            intensidadX_refelxion=np.mean([x * y for x, y in zip(medicion_ventaneada[0][j], medicion_ventaneada[1][j])])
            intensidadY_refelxion=np.mean([x * y for x, y in zip(medicion_ventaneada[0][j], medicion_ventaneada[2][j])])
            intensidadZ_refelxion=np.mean([x * y for x, y in zip(medicion_ventaneada[0][j], medicion_ventaneada[3][j])])
            modulo_intensidad_medicion=np.sqrt(intensidadX_refelxion**2+intensidadY_refelxion**2+intensidadZ_refelxion**2)
            #energia_medicion=np.mean((medicion_ventaneada[0][j]**2+medicion_ventaneada[1][j]**2+medicion_ventaneada[2][j]
            #                  **2+medicion_ventaneada[3][j]**2)/c)
            #Calculo de coordenadas esféricas
            radio_reflexiones.append(modulo_intensidad_medicion)
            azymuth_reflexiones.append(np.arctan(intensidadY_refelxion/intensidadX_refelxion))
            elevation_reflexiones.append(np.arccos(intensidadZ_refelxion/modulo_intensidad_medicion))
            #Calculo de vectores directores
            directorX_refelxiones.append(intensidadX_refelxion/modulo_intensidad_medicion)
            directorY_refelxiones.append(intensidadY_refelxion / modulo_intensidad_medicion)
            directorZ_refelxiones.append(intensidadZ_refelxion / modulo_intensidad_medicion)
        parametros_senales.append([directorX_refelxiones, directorY_refelxiones, directorZ_refelxiones,
                                   radio_reflexiones, azymuth_reflexiones, elevation_reflexiones])

    return parametros_senales, cantidad_ventanas

#Se calculan los valores de intensidad, así como las coordenadas esféricas de la parte de la señal que representa
# el sonido directo
def intensidadSonidoDirecto(senales,sonido_directo):

    directorX_sonido_directo = []
    directorY_sonido_directo = []
    directorZ_sonido_directo = []
    radio_sonido_directo=[]
    azymuth_sonido_directo = []
    elevation_sonido_directo = []
    parametros_sonido_directo = []
    sonido_directo_senial=[]
    for medicion in senales:
        for i, canal in enumerate(medicion):
            sonido_directo_senial.append(medicion[i][:sonido_directo])
        # Calculo de vectores de intensidad
        intensidadX_sd=np.mean([x * y for x, y in zip(sonido_directo_senial[0], sonido_directo_senial[1])])
        intensidadY_sd=np.mean([x * y for x, y in zip(sonido_directo_senial[0], sonido_directo_senial[2])])
        intensidadZ_sd=np.mean([x * y for x, y in zip(sonido_directo_senial[0], sonido_directo_senial[3])])
        modulo_intensidad_medicion = np.sqrt(intensidadX_sd ** 2 + intensidadY_sd ** 2 + intensidadZ_sd ** 2)
        #energia_medicion = sum((sonido_directo_senial[0] ** 2 + sonido_directo_senial[1] ** 2
        #                        + sonido_directo_senial[2] ** 2 + sonido_directo_senial[3] ** 2) / c)
        # Calculo de coordenadas esféricas
        radio_sonido_directo.append(modulo_intensidad_medicion)
        azymuth_sonido_directo.append(np.arctan(intensidadY_sd / intensidadX_sd))
        elevation_sonido_directo.append(np.arccos(intensidadZ_sd / modulo_intensidad_medicion))
        # Calculo de vectores directores
        directorX_sonido_directo.append(intensidadX_sd / modulo_intensidad_medicion)
        directorY_sonido_directo.append(intensidadY_sd / modulo_intensidad_medicion)
        directorZ_sonido_directo.append(intensidadZ_sd / modulo_intensidad_medicion)


    parametros_sonido_directo.append([directorX_sonido_directo, directorY_sonido_directo, directorZ_sonido_directo,
                                   radio_sonido_directo, azymuth_sonido_directo, elevation_sonido_directo])


    return parametros_sonido_directo

#Se concatenan las ventanas de los parámetros de las reflexiones y el sonido directo
def concatenar(sonido_directo, reflexiones):

    medicion_completo=[]
    for i,medicion in enumerate(reflexiones):
        directorXCompleto = sonido_directo[i][0] + medicion[0]
        directorYCompleto = sonido_directo[i][1] + medicion[1]
        directorZCompleto = sonido_directo[i][2] + medicion[2]
        radioCompleto = sonido_directo[i][3] + medicion[3]
        asimuthCompleto = sonido_directo[i][4] + medicion[4]
        elevacionCompleto = sonido_directo[i][5] + medicion[5]

        vectorCompleto = [directorXCompleto, directorYCompleto, directorZCompleto,
                          radioCompleto, asimuthCompleto, elevacionCompleto]
        medicion_completo.append(vectorCompleto)

    return medicion_completo

#Se normalizan los vectores respecto al sonido directo y se pasan los valores a dB.
#Se eliminan los valores que no superen el threshold.
def normalizar(senales,threshold):

    medicion_normalizada=[]
    for medicion in senales:
        magnitud = medicion[3]
        directorX=medicion[0]
        directorY = medicion[1]
        directorZ = medicion[2]
        magnitud_normalizada=magnitud/magnitud[0] #Normalización respecto al sonido directo
        magnitud_db = 10 * np.log10(magnitud_normalizada) #Calculo de dB

        magnitud_dB_tabla=magnitud_db-max(magnitud_db) #Valores de magnitud que se mostraran en la tabla "Data"


        idx = magnitud_db >= threshold #Se ubican los valores que superan el threshold
        for i in range(len(idx)):
            if not idx[i]:
                magnitud_db[i] = 0 #Si no lo superan se cambia su magnitud a 0

        magnitud_dB_grafico=magnitud_db
        magnitud_db = magnitud_db - 2 * min(magnitud_db) #Se elevan las magnitudes para tener valores positivos

        magnitud_db_normalizada = magnitud_db / max(magnitud_db) #Se normalizan para tener resultados entre 1 y 0

        for i in range(1, len(magnitud_db_normalizada)):
            if magnitud_db_normalizada[i]==1:
                magnitud_db_normalizada[i]=0 #A todas las magnitudes que no superaron el umbral se les da un valor de 0

        #Se calculan los vectores resultantes a graficar
        intensidadX=directorX*magnitud_db_normalizada
        intensidadY=directorY*magnitud_db_normalizada
        intensidadZ=directorZ*magnitud_db_normalizada

        medicion_normalizada.append([intensidadX, intensidadY, intensidadZ, magnitud_dB_grafico, magnitud_dB_tabla])

    return medicion_normalizada


"""def polaraCartesiano(senales):
    coordenadas_cartesinas=[]
    x=[]
    y=[]
    z=[]
    for canal in senales:
        for index in np.arange(0,len(canal[0])):
            x.append(canal[0][index]*np.cos(canal[2][index])*np.sin(canal[1][index]))
            y.append(canal[0][index]*np.sin(canal[2][index])*np.sin(canal[1][index]))
            z.append(canal[0][index]*np.cos(canal[1][index]))

        coordenadas_cartesinas.append([x, y, z])

    return coordenadas_cartesinas"""


def make_float(num):
    num = num.replace(' ','').replace(',','.').replace("−", "-")
    return float(num)

#Se realiza el ploteo del Hedgehog
def ploteo3d(senales, largo_reflexiones, sonido_directo, W, H):
    plot=[]
    for medicion in senales:
        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(W * px, H * px))
        ax = fig.add_subplot(111, projection='3d')
        reflexiones_x = medicion[0][1:]
        reflexiones_y = medicion[1][1:]
        reflexiones_z = medicion[2][1:]

        sonido_directo_x = medicion[0][0]
        sonido_directo_y = medicion[1][0]
        sonido_directo_z = medicion[2][0]

        magnitud_db=medicion[3]
        #Funcion para graficar lineas desde el origen hasta los puntos de intensidad de las refelxiones en el espacio
        def make_dashedLines_reflexiones(x, y, z, ax):
            for i in range(len(x)):
                x_val, y_val, z_val = x[i], y[i], z[i]

                ax.plot([0, x_val], [0, y_val], zs=[0, z_val], color=img.to_rgba(c[i]), linewidth=2)

        #Funcion para graficar lineas desde el origen hasta los puntos de intensidad del sonido directo en el espacio
        #Se diferencia para poder aplicarle color rojo y una linea más gruesa
        def make_dashedLines_sonido_directo(x, y, z, ax):

            ax.plot([0, x], [0, y], zs=[0, z], color='r', linewidth=5)

        c = np.linspace((sonido_directo/1000), (sonido_directo/1000)+largo_reflexiones, len(reflexiones_x))

        #Se grafican los puntos en el espacio de las intensidades de las reflexiones y el sonido directo
        img = ax.scatter(reflexiones_x, reflexiones_y, reflexiones_z, c=c, marker=".", linewidths=1, cmap=plt.hsv())
        ax.scatter(sonido_directo_x, sonido_directo_y, sonido_directo_z, c='r', marker=".", linewidths=3)
        cursor = mplcursors.cursor(img, hover=True)

        #Función para mostrar un cartel con los valores de intensidad correspondiente cuando se hace click en una espina
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            'Intensidad(dB): {:.1f}'
                .format(magnitud_db[sel.target.index])))

        """ @cursor.connect("add")"""
        def on_add(sel):
            artist = sel.artist
            ann = sel.annotation
            coordenadas=re.split(",? +", artist.axes.format_coord(*sel.target))
            x = coordenadas[0][2:]
            x=make_float(x)
            y = coordenadas[1][2:]
            y=make_float(y)
            z = coordenadas[2][2:]
            z=make_float(z)
            intensidad=np.sqrt(x**2+y**2+z**2)
            ann.set_text("{}\nIntensidad:={:.3g}".format(
                ann.get_text(), intensidad))

        make_dashedLines_reflexiones(reflexiones_x, reflexiones_y, reflexiones_z, ax)
        make_dashedLines_sonido_directo(sonido_directo_x, sonido_directo_y, sonido_directo_z, ax)

        #Barra con código de colores que representa en que tiempo se dió cada espina graficada
        cbar = fig.colorbar(img)
        cbar.set_label("Tiempo[s]")

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plot.append(fig)

    return plot


#Se plotea el gráfico 2D que se ubicará sobre la imagen de planta. Mismos pasos que en la función anterior.
def ploteo2d(senales, largo_reflexiones, sonido_directo):
    plot = []
    for medicion in senales:
        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(300 * px, 300 * px),dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        reflexiones_x = medicion[0][1:]
        reflexiones_y = medicion[1][1:]
        reflexiones_z = medicion[2][1:]

        sonido_directo_x = medicion[0][0]
        sonido_directo_y = medicion[1][0]
        sonido_directo_z = medicion[2][0]

        def make_dashedLines_reflexiones(x, y, z, ax):
            for i in range(len(x)):
                x_val, y_val, z_val = x[i], y[i], z[i]


                ax.plot([0, x_val], [0, y_val], zs=[0, z_val], color=img.to_rgba(c[i]), linewidth=2)

        def make_dashedLines_sonido_directo(x, y, z, ax):

            ax.plot([0, x], [0, y], zs=[0, z], color='r', linewidth=5)

        c = np.linspace((sonido_directo / 1000), (sonido_directo / 1000) + largo_reflexiones, len(reflexiones_x))

        img = ax.scatter(reflexiones_x, reflexiones_y, reflexiones_z, c=c, marker=".", linewidths=1, cmap=plt.hsv())
        ax.scatter(sonido_directo_x, sonido_directo_y, sonido_directo_z, c='r', marker=".", linewidths=1)

        make_dashedLines_reflexiones(reflexiones_x, reflexiones_y, reflexiones_z, ax)
        make_dashedLines_sonido_directo(sonido_directo_x, sonido_directo_y, sonido_directo_z, ax)
        #Se aplican parámetros para graficar unicamente lo que queremos guardar en la imagen y se toma una vista
        # desde arriba
        ax.view_init(azim=0, elev=90)
        ax.set_facecolor(color="w")
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_zlabel('')
        # Hide grid lines
        ax.grid(False)
        plt.axis('off')
        # Hide axes ticks
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])
        # make the panes transparent
        ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        plt.tick_params(bottom=False)
        plt.tight_layout()
        plot.append(fig)
        #Se guarda imagen en carpeta temporal
        cwd=str(pathlib.Path(__file__).parent.resolve())
        fig.savefig(cwd+"/temp/ploteo2d.png", format='png', transparent=True)


#Se plotea la presión del canal W junto con la detección del sonido directo
def ploteo_presion(fs, senales,sonido_directo, W, H):
    figs=[]
    for medicion in senales:
        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(W * px, H * px))
        ax = fig.add_subplot(111)
        canal_w=medicion[0]
        sonido_directo=float(sonido_directo)/1000
        x = np.linspace(0, len(canal_w) / fs, len(canal_w))
        ax.plot(x, canal_w, label='Presión sonora Canal W')
        ax.axvline(x=sonido_directo, color='r',label='Sonido Directo')
        ax.set_ylabel('Magnitud')
        ax.set_xlabel('Tiempo(S)')
        ax.legend()
        plt.tight_layout()

        figs.append(fig)

    return figs


#Se plotea la presión del canal W junto con las ventanas
def ploteo_ventanas(fs, senales,ventanas, W, H):
    figs=[]
    for medicion in senales:
        px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
        fig = plt.figure(figsize=(W * px, H * px))
        ax = fig.add_subplot(111)
        canal_w=medicion[0]
        ventana=ventanas/1000
        marcadores=np.arange(0, len(canal_w),int(ventana*fs))
        x = np.linspace(0, len(canal_w) / fs, len(canal_w))
        ax.plot(x, canal_w, '-d',label="Ventanas", mfc='red', mec='k', markevery=marcadores)
        ax.set_ylabel('Magnitud')
        ax.set_xlabel('Tiempo(S)')
        ax.legend()
        plt.tight_layout()

        figs.append(fig)

    return figs