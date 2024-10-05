from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, get_flashed_messages
from pymongo import MongoClient
from functools import wraps ###M1
from flask import session ###M1
from bson import ObjectId
from datetime import datetime
import pandas as pd
import os
import pytz

app = Flask(__name__)

# Obtener la clave secreta desde las variables de entorno
#app.secret_key = os.getenv('SECRET_KEY')

# Configurar conexión a MongoDB usando variable de entorno
#mongo_uri = os.getenv('MONGO_URI')
#client = MongoClient(mongo_uri)


# Configurar conexión a MongoDB
app.secret_key = '0e01e4bcf2960bdb6aafeac4cded07b5f0bb809d8e1ff7e9'
#client = MongoClient('mongodb://localhost:27017/')
client = MongoClient('mongodb+srv://alexisgarcia:Percha84@temporada2324.lug6z.mongodb.net/?retryWrites=true&w=majority&appName=temporada2324')
#                      mongodb+srv://alexisgarcia51:<db_password>@temporada2324.lug6z.mongodb.net/?retryWrites=true&w=majority&appName=temporada2324
db = client['apacilagua']
lotes_collection = db['lotes']
form_data_collection = db['form_data']
personal_data_collection = db['personal_data']
estimaciones_data_collection = db['estimaciones_data'] #####aqui
pulverizaciones_data_collection = db['pulverizaciones_data'] #####aqui
coleccion_variedades = db['datos_maestros']

# Leer datos del archivo Excel y cargar a MongoDB si no se han cargado antes
if lotes_collection.count_documents({}) == 0:
    df = pd.read_excel('lotes.xlsx')
    
    # Convertir los campos 'Turno' y 'Válvula' a cadenas
    if 'Turno' in df.columns:
        df['Turno'] = df['Turno'].astype(str)
    if 'Valvula' in df.columns:
        df['Valvula'] = df['Valvula'].astype(str)
    
    # Insertar documentos en MongoDB
    lotes_collection.insert_many(df.to_dict(orient='records'))

# Actualizar los documentos para asegurar que 'Turno' y 'Válvula' sean cadenas
for document in lotes_collection.find():
    turnos_str = str(document.get('Turno', ''))
    valvula_str = str(document.get('Valvula', ''))  # Convertir Válvula a cadena
    
    # Actualizar el documento
    lotes_collection.update_one(
        {'_id': document['_id']}, 
        {'$set': {'Turno': turnos_str, 'Valvula': valvula_str}}
    )



# Función para guardar datos en un archivo CSV (comentada para uso futuro)
# def save_to_csv(data, filename):
#     file_exists = os.path.isfile(filename)
#     df = pd.DataFrame([data])
#     df.to_csv(filename, mode='a', header=not file_exists, index=False)

users_collection = db['users']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Buscar al usuario en la base de datos
        user = users_collection.find_one({'username': username, 'password': password})
        
        if user:
            session['username'] = username
            session['access'] = user['access']  # Almacenar permisos de acceso
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña inválidos. Por favor, intenta de nuevo.', 'danger')

    return render_template('login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Por favor, inicia sesión primero.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def access_required(required_access):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'access' not in session or required_access not in session['access']:
                flash('No tienes acceso a esta página.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper




@app.route('/logout')
def logout():
    session.pop('username', None)  # Elimina el nombre de usuario de la sesión
    #flash('Has cerrado sesión.', 'success')
    return redirect(url_for('login'))  # Redirige a la página de inicio de sesión

@app.route('/', methods=['GET', 'POST']) ####M1
def index():
    return render_template('index.html')


def login_required(f):  ######M1
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            #flash('Por favor, inicia sesión para acceder a esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/datos', methods=['GET', 'POST'])
@login_required ###M1
@access_required('datos')
def datos():
    if request.method == 'POST':
        # Obtener datos del formulario
        lote = request.form.get('lote')
        turno = request.form.get('turno')
        valvula = request.form.get('valvula')
        area = request.form.get('area')
        ciclo = request.form.get('ciclo')
        variedad = request.form.get('variedad')
        edad = request.form.get('edad')
        muestra = request.form.get('muestra')  # Puede ser lista vacía
        tamano = request.form.get('tamano')
        hojas = request.form.get('hojas')
        guias = request.form.get('guias')
        entrenudo = request.form.get('entrenudo')
        cegotero = request.form.get('cegotero')  # Agregando
        phgotero = request.form.get('phgotero')
        ceextractor = request.form.get('ceextractor')
        phextractor = request.form.get('phextractor')
        cesuelo = request.form.get('cesuelo')
        phsuelo = request.form.get('phsuelo')
        tensiometroa = request.form.get('tensiometroa')
        tensiometrob = request.form.get('tensiometrob')
        observaciones = request.form.get('observaciones', '')  # Lista vacía
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        try:
            # Conversión de tipos
            ciclo = int(ciclo)
            edad = int(edad)
            area = float(area)

            # Verificar que los campos son válidos y asignar valores
            cegotero = float(cegotero) if cegotero else None
            phgotero = float(phgotero) if phgotero else None
            ceextractor = float(ceextractor) if ceextractor else None
            phextractor = float(phextractor) if phextractor else None
            cesuelo = float(cesuelo) if cesuelo else None
            phsuelo = float(phsuelo) if phsuelo else None
            tensiometrob = float(tensiometrob) if tensiometrob else None
            tensiometroa = float(tensiometroa) if tensiometroa else None
            hojas = int(hojas) if hojas else None
            guias = float(guias) if guias else None
            entrenudo = float(entrenudo) if entrenudo else None
            muestra = int(muestra) if muestra else None
            tamano = int(tamano) if tamano else None

        except ValueError:
            flash('Revisar los campos con los valores', 'error')
            return redirect(url_for('datos'))

        # Validación de campos obligatorios
        if not (lote and valvula and turno and ciclo and variedad and edad and area):
            flash('Todos los campos obligatorios deben ser completados', 'error')
            return redirect(url_for('datos'))

        # Convertir la fecha/hora a la zona horaria local
        fecha_capturada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formato = "%Y-%m-%d %H:%M:%S"
        fecha_obj = datetime.strptime(fecha_capturada, formato)

        # Establecer la zona horaria UTC
        zona_utc = pytz.utc
        fecha_utc = zona_utc.localize(fecha_obj)

        # Convertir a la zona horaria local
        zona_local = pytz.timezone("America/Tegucigalpa")
        fecha_local = fecha_utc.astimezone(zona_local)

        # Datos a guardar
        data = {
            'Fecha/Hora': fecha_local.strftime("%Y-%m-%d %H:%M:%S"),
            'Lote': lote,
            'Turno': turno,
            'Valvula': valvula,
            'Area': area,
            'Ciclo': ciclo,
            'Variedad': variedad,
            'Edad_cultivo': edad,
            'Muestra': muestra,
            'Tamaño_Muestra': tamano,
            'Hojas_dia': hojas,
            'Guias': guias,
            'Entrenudos': entrenudo,
            'CE_gotero': cegotero,
            'PH_gotero': phgotero,
            'CE_extractor': ceextractor,
            'PH_extractor': phextractor,
            'CE_suelo': cesuelo,
            'PH_suelo': phsuelo,
            'Tensiometro_12': tensiometroa,
            'Tensiometro_24': tensiometrob,
            'Observaciones': observaciones,
            'Latitud': latitude,
            'Longitud': longitude
        }

        try:
            # Guardar en MongoDB
            form_data_collection.insert_one(data)
            flash('Datos guardados correctamente', 'success')
        except Exception as e:
            flash(f'Error al guardar los datos: {e}', 'error')

        return redirect(url_for('datos'))
    
        # Extraer las variedades de la colección 'datos_maestros'
    datos_maestros = coleccion_variedades.find_one({}, {"variedades": 1})
    variedades = datos_maestros['variedades'] if datos_maestros else []

    # Obtener ciclos desde la base de datos (usando el _id correcto)
    ciclos_maestros = coleccion_variedades.find_one({"_id": ObjectId("66fb5c12078436f9b540749b")}, {"ciclos": 1})
    ciclos = ciclos_maestros['ciclos'] if ciclos_maestros else []

    return render_template('datos.html',variedades=variedades, ciclos=ciclos)



@app.route('/estimaciones', methods=['GET', 'POST'])
@login_required ###M1
@access_required('estimaciones')
def estimaciones():
    if request.method == 'POST':
        lote = request.form.get('lote')
        turno = request.form.get('turno')
        valvula = request.form.get('valvula')
        area = request.form.get('area')
        ciclo = request.form.get('ciclo')
        variedad = request.form.get('variedad')
        edad = request.form.get('edad')
        muestra = request.form.get('muestra') #puede ser lista vacia
        tamano = request.form.get('tamano')
        floresf = request.form.get('floresf')
        floresm = request.form.get('floresm')
        pegafruto = request.form.get('pegafruto')
        curva_crecimiento = request.form.get('curva_crecimiento')
        planta_pegada = request.form.get('planta_pegada')
        total_plantas = request.form.get('total_plantas')
        observaciones = request.form.get('observaciones', '')  # lista vacia
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        try:
            ciclo = int(ciclo)
            edad = int(edad)
            area = float(area)

            #para que muestra sea opcional y de valor null
            if floresf:
                floresf = int(floresf)
            else:
                floresf = None
            
            if floresm:
                floresm = int(floresm)
            else:
                floresm = None

            if pegafruto:
                pegafruto = int(pegafruto)
            else:
                pegafruto = None

            if muestra:
                muestra = int(muestra)
            else:
                muestra = None

            if tamano:
                tamano = int(tamano)
            else:
                tamano = None

            if curva_crecimiento:
                curva_crecimiento= float(curva_crecimiento)
            else:
                curva_crecimiento = None   

            if planta_pegada:
                planta_pegada = int(planta_pegada)
            else:
                planta_pegada = None   

            if total_plantas:
                total_plantas = int(total_plantas)
            else:
                total_plantas = None   


        except ValueError:
            flash('Revisar los campos con los valores', 'error')
            return redirect(url_for('estimaciones'))

        # Validación de campos obligatorios
        if not (lote and turno and area and valvula and variedad and ciclo and edad):
            flash('Todos los campos obligatorios deben ser completados', 'error')
            return redirect(url_for('estimaciones'))
        

                # Convertir la fecha/hora a la zona horaria local
        fecha_capturada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formato = "%Y-%m-%d %H:%M:%S"
        fecha_obj = datetime.strptime(fecha_capturada, formato)
        
        # Establecer la zona horaria UTC
        zona_utc = pytz.utc
        fecha_utc = zona_utc.localize(fecha_obj)
        
        # Convertir a la zona horaria local
        zona_local = pytz.timezone("America/Tegucigalpa")
        fecha_local = fecha_utc.astimezone(zona_local)

        # Datos a guardar
        data = {
            'Fecha/Hora': fecha_local.strftime("%Y-%m-%d %H:%M:%S"),
            'Lote': lote,
            'Turno': turno,
            'Valvula': valvula,
            'Area': area,
            'Ciclo': ciclo,
            'Variedad': variedad,
            'Ciclo': ciclo,
            'Edad_cultivo': edad,
            'Muestra': muestra,
            'Tamaño_Muestra': tamano,
            'Flores_Femeninas': floresf,
            'Flores_Masculinas': floresm,
            'Pega_Fruto': pegafruto,
            'Curva_Crecimiento': curva_crecimiento,
            'Planta_Pegada': planta_pegada,
            'Total_Planta': total_plantas,
            'Observaciones': observaciones,
            'Latitud': latitude,
            'Longitud': longitude
        }

        try:
            # Guardar en MongoDB
            estimaciones_data_collection.insert_one(data)

            # Guardar en CSV (comentado para uso futuro)
            # save_to_csv(data, 'form_data.csv')

            flash('Datos guardados correctamente', 'success')
        except Exception as e:
            flash(f'Error al guardar los datos: {e}', 'error')

        return redirect(url_for('estimaciones'))
    
            # Extraer las variedades de la colección 'datos_maestros'
    datos_maestros = coleccion_variedades.find_one({}, {"variedades": 1})
    variedades = datos_maestros['variedades'] if datos_maestros else []

        # Obtener ciclos desde la base de datos (usando el _id correcto)
    ciclos_maestros = coleccion_variedades.find_one({"_id": ObjectId("66fb5c12078436f9b540749b")}, {"ciclos": 1})
    ciclos = ciclos_maestros['ciclos'] if ciclos_maestros else []

    return render_template('estimaciones.html', variedades=variedades, ciclos=ciclos)


@app.route('/pulverizaciones', methods=['GET', 'POST'])
@login_required ###M1
@access_required('pulverizaciones')
def pulverizaciones():
    if request.method == 'POST':
        lote = request.form.get('lote')
        turno = request.form.get('turno')
        valvula = request.form.get('valvula')
        area = request.form.get('area')
        ciclo = request.form.get('ciclo')
        variedad = request.form.get('variedad')
        edad = request.form.get('edad')
        bonada = request.form.get('bonada')
        equipo = request.form.get('equipo') 
        operario = request.form.get('operario')
        producto1 = request.form.get('producto1')
        producto2 = request.form.get('producto2')
        producto3 = request.form.get('producto3')
        producto4 = request.form.get('producto4')
        producto5 = request.form.get('producto5')
        ce = request.form.get('ce')
        ph = request.form.get('ph')
        temperatura = request.form.get('temperatura')
        velocidad = request.form.get('velocidad')
        observaciones = request.form.get('observaciones', '')  # lista vacia
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        try:
            ciclo = int(ciclo)
            edad = int(edad)
            area = float(area)
            operario = str(operario)

            #para que muestra sea opcional y de valor null
            ce = float(ce) if ce else None
            ph = float(ph) if ph else None
            bonada = int(bonada) if bonada else None
            producto1 = str(producto1) if producto1 else None
            producto2 = str(producto2) if producto2 else None
            producto3 = str(producto3) if producto3 else None
            producto4 = str(producto4) if producto4 else None
            producto5 = str(producto5) if producto5 else None
            temperatura = float(temperatura) if temperatura else None
            velocidad = float(velocidad) if velocidad else None
            equipo = str(equipo) if equipo else None

        except ValueError:
            flash('Revisar los campos con los valores', 'error')
            return redirect(url_for('pulverizaciones'))

        # Validación de campos obligatorios
        if not (lote and turno and area and valvula and variedad and ciclo and edad and operario):
            flash('Todos los campos obligatorios deben ser completados', 'error')
            return redirect(url_for('pulverizaciones'))
        

                # Convertir la fecha/hora a la zona horaria local
        fecha_capturada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formato = "%Y-%m-%d %H:%M:%S"
        fecha_obj = datetime.strptime(fecha_capturada, formato)
        
        # Establecer la zona horaria UTC
        zona_utc = pytz.utc
        fecha_utc = zona_utc.localize(fecha_obj)
        
        # Convertir a la zona horaria local
        zona_local = pytz.timezone("America/Tegucigalpa")
        fecha_local = fecha_utc.astimezone(zona_local)

        # Datos a guardar
        data = {
            'Fecha/Hora': fecha_local.strftime("%Y-%m-%d %H:%M:%S"),
            'Lote': lote,
            'Turno': turno,
            'Valvula': valvula,
            'Area': area,
            'Ciclo': ciclo,
            'Variedad': variedad,
            'Ciclo': ciclo,
            'Edad_cultivo': edad,
            'Bonada': bonada,
            'Operario': operario,
            'Producto1': producto1,
            'Producto2': producto2,
            'Producto3': producto3,
            'Producto4': producto4,
            'Producto5': producto5,
            'CE': ce,
            'PH': ph,
            'Temperatura': temperatura,
            'Velocidad_viento': velocidad,
            'Equipo': equipo,
            'Observaciones': observaciones,
            'Latitud': latitude,
            'Longitud': longitude
        }

        try:
            # Guardar en MongoDB
            pulverizaciones_data_collection.insert_one(data)

            # Guardar en CSV (comentado para uso futuro)
            # save_to_csv(data, 'form_data.csv')

            flash('Datos guardados correctamente', 'success')
        except Exception as e:
            flash(f'Error al guardar los datos: {e}', 'error')

        return redirect(url_for('pulverizaciones'))
                # Extraer las variedades de la colección 'datos_maestros'
    datos_maestros = coleccion_variedades.find_one({}, {"variedades": 1})
    variedades = datos_maestros['variedades'] if datos_maestros else []

        # Obtener ciclos desde la base de datos (usando el _id correcto)
    ciclos_maestros = coleccion_variedades.find_one({"_id": ObjectId("66fb5c12078436f9b540749b")}, {"ciclos": 1})
    ciclos = ciclos_maestros['ciclos'] if ciclos_maestros else []


    return render_template('pulverizaciones.html', variedades=variedades, ciclos=ciclos)

@app.route('/ingreso_personal', methods=['GET', 'POST'])
@login_required ###M1
@access_required('ingreso_personal') 
def ingreso_personal():
    if request.method == 'POST':
        lote = request.form.get('lote')
        turno = request.form.get('turno')
        valvula = request.form.get('valvula')
        area = request.form.get('area')
        labor = request.form.get('labor')
        personaplan = request.form.get('personaplan')
        personareal = request.form.get('personareal')
        encargado = request.form.get('encargado')

        # Convertir la fecha/hora a la zona horaria local
        fecha_capturada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formato = "%Y-%m-%d %H:%M:%S"
        fecha_obj = datetime.strptime(fecha_capturada, formato)

        # Establecer la zona horaria UTC
        zona_utc = pytz.utc
        fecha_utc = zona_utc.localize(fecha_obj)

        # Convertir a la zona horaria local
        zona_local = pytz.timezone("America/Tegucigalpa")
        fecha_local = fecha_utc.astimezone(zona_local)

        try:
            # Convertir personaplan a float (permite enteros y decimales)
            personaplan = float(personaplan)
            personareal = float(personareal)
            area = float(area)
        except ValueError:
            flash('Uno o más campos numéricos no tienen un formato válido', 'error')
            return redirect(url_for('ingreso_personal'))

        if not (lote and turno and valvula and area and labor and encargado and personaplan and personareal):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('ingreso_personal'))

        # Datos a guardar
        data = {
            'Fecha/Hora': fecha_local.strftime("%Y-%m-%d %H:%M:%S"),
            'Lote': lote,
            'Turno': turno,
            'Valvula': valvula,
            'Area': area,
            'Labor': labor,
            'Encargado': encargado,
            'PersonaPlan': personaplan,
            'PersonaReal': personareal
        }

        try:
            # Guardar en MongoDB
            personal_data_collection.insert_one(data)

            # Guardar en CSV (comentado para uso futuro)
            # save_to_csv(data, 'personal_data.csv')

            flash('Datos guardados correctamente', 'success')
        except Exception as e:
            flash(f'Error al guardar los datos: {e}', 'error')

        return redirect(url_for('ingreso_personal'))
    return render_template('ingreso_personal.html')


@app.route('/api/lotes', methods=['GET'])
def get_lotes():
    lotes = lotes_collection.distinct('Lote')
    return jsonify(lotes)

@app.route('/api/turnos', methods=['GET'])
def get_turnos():
    lote = request.args.get('lote')
    if not lote:
        return jsonify({"error": "No se proporcionó el lote."}), 400
    
    # Filtramos los documentos en función del Lote
    filtered_df = pd.DataFrame(list(lotes_collection.find({'Lote': lote})))
    
    # Obtenemos los turnos únicos
    turnos = filtered_df['Turno'].astype(str).unique().tolist()  # Asegúrate de que todo sea tratado como string
    
    return jsonify(turnos)


@app.route('/api/valvulas', methods=['GET'])
def get_valvulas():
    lote = request.args.get('lote')
    turno = request.args.get('turno')
    
    if not lote or not turno:
        return jsonify({"error": "No se proporcionó el lote o el turno."}), 400
    
    # Filtramos en función de Lote y Turno
    filtered_df = pd.DataFrame(list(lotes_collection.find({
        'Lote': lote,
        'Turno': turno 
    })))
    
    # Obtenemos las válvulas únicas
    valvulas = filtered_df['Valvula'].unique().tolist()
    
    return jsonify(valvulas)


@app.route('/api/area', methods=['GET'])
def get_area():
    lote = request.args.get('lote')
    turno = request.args.get('turno')
    valvula = request.args.get('valvula')
    
    # Verificamos si se proporcionan todos los parámetros
    if not lote or not turno or not valvula:
        return jsonify({"error": "No se proporcionó el lote, turno o válvula."}), 400
    
    try:
        valvula = str(valvula)  # Asegúrate de convertir valvula a string
    except ValueError:
        return jsonify({"error": "La válvula proporcionada no es válida."}), 400
    
    # Filtramos los documentos en la colección
    filtered_documents = list(lotes_collection.find({
        'Lote': lote,
        'Turno': turno,
        'Valvula': valvula
    }))

    # Verificamos si hay resultados
    if not filtered_documents:
        return jsonify({"error": "No se encontraron resultados con los filtros proporcionados."}), 404
    
    # Convertimos los documentos filtrados en un DataFrame de pandas
    filtered_df = pd.DataFrame(filtered_documents)
    
    # Obtenemos las áreas únicas y las redondeamos
    areas = filtered_df['Area_mz'].dropna().unique().tolist()
    areas_dict = [{'Area_mz': round(area, 2)} for area in areas]

    return jsonify(areas_dict)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)





