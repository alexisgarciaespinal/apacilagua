from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import os
import pytz

app = Flask(__name__)

# Obtener la clave secreta desde las variables de entorno
app.secret_key = os.getenv('SECRET_KEY')
# Configurar conexión a MongoDB usando variable de entorno
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)



# Configurar conexión a MongoDB
#app.secret_key = '0e01e4bcf2960bdb6aafeac4cded07b5f0bb809d8e1ff7e9'
#client = MongoClient('mongodb://localhost:27017/')
#client = MongoClient('mongodb+srv://alexisgarcia51:LC9CEnmshqJUu6UH@temporada2324.lug6z.mongodb.net/?retryWrites=true&w=majority&appName=temporada2324')
#                      mongodb+srv://alexisgarcia51:<db_password>@temporada2324.lug6z.mongodb.net/?retryWrites=true&w=majority&appName=temporada2324
db = client['apacilagua']
lotes_collection = db['lotes']
form_data_collection = db['form_data']
personal_data_collection = db['personal_data']
estimaciones_data_collection = db['estimaciones_data'] #####aqui

# Leer datos del archivo Excel y cargar a MongoDB si no se han cargado antes
if lotes_collection.count_documents({}) == 0:
    df = pd.read_excel('lotes.xlsx')
    lotes_collection.insert_many(df.to_dict(orient='records'))

# Función para guardar datos en un archivo CSV (comentada para uso futuro)
# def save_to_csv(data, filename):
#     file_exists = os.path.isfile(filename)
#     df = pd.DataFrame([data])
#     df.to_csv(filename, mode='a', header=not file_exists, index=False)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')



@app.route('/datos', methods=['GET', 'POST'])
def datos():
    if request.method == 'POST':
        lote = request.form.get('lote')
        valvula = request.form.get('valvula')
        ciclo = request.form.get('ciclo')
        edad = request.form.get('edad')
        muestra = request.form.get('muestra') #puede ser lista vacia
        tamano = request.form.get('tamano')
        hojas = request.form.get('hojas')
        guias = request.form.get('guias')
        entrenudo = request.form.get('entrenudo')
        tensiometroa = request.form.get('tensiometroa')
        tensiometrob = request.form.get('tensiometrob')
        observaciones = request.form.get('observaciones', '')  # lista vacia
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        try:
            ciclo = int(ciclo)
            edad = int(edad)

            #para que muestra sea opcional y de valor null
            if tensiometrob:
                tensiometrob = float(tensiometrob)
            else:tensiometrob = None

            if tensiometroa:
                tensiometroa = float(tensiometroa)
            else:
                tensiometroa = None

            if hojas:
                hojas = int(hojas)
            else:
                hojas = None
            
            if guias:
                guias = int(guias)
            else:
                guias = None
            
            if entrenudo:
                entrenudo = int(entrenudo)
            else:
                entrenudo = None

            if muestra:
                muestra = int(muestra)
            else:
                muestra = None

            if tamano:
                tamano = int(tamano)
            else:
                tamano = None
        
        except ValueError:
            flash('Revisar los campos con los valores', 'error')
            return redirect(url_for('datos'))

        # Validación de campos obligatorios
        if not (lote and valvula and ciclo and edad):
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
            'Valvula': valvula,
            'Ciclo': ciclo,
            'Edad_cultivo': edad,
            'Muestra': muestra,
            'Tamaño_Muestra': tamano,
            'Hojas_dia': hojas,
            'Guias': guias,
            'Entrenudos': entrenudo,
            'Tensiometro_12': tensiometroa,
            'Tensiometro_24': tensiometrob,
            'Observaciones': observaciones,
            'Latitud': latitude,
            'Longitud': longitude
        }

        try:
            # Guardar en MongoDB
            form_data_collection.insert_one(data)

            # Guardar en CSV (comentado para uso futuro)
            # save_to_csv(data, 'form_data.csv')

            flash('Datos guardados correctamente', 'success')
        except Exception as e:
            flash(f'Error al guardar los datos: {e}', 'error')

        return redirect(url_for('datos'))

    return render_template('datos.html')



@app.route('/estimaciones', methods=['GET', 'POST'])
def estimaciones():
    if request.method == 'POST':
        lote = request.form.get('lote')
        valvula = request.form.get('valvula')
        ciclo = request.form.get('ciclo')
        edad = request.form.get('edad')
        muestra = request.form.get('muestra') #puede ser lista vacia
        tamano = request.form.get('tamano')
        floresf = request.form.get('floresf')
        floresm = request.form.get('floresm')
        tensiometroa = request.form.get('tensiometroa')
        tensiometrob = request.form.get('tensiometrob')
        observaciones = request.form.get('observaciones', '')  # lista vacia
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        try:
            ciclo = int(ciclo)
            edad = int(edad)

            #para que muestra sea opcional y de valor null
            if tensiometrob:
                tensiometrob = float(tensiometrob)
            else:tensiometrob = None

            if tensiometroa:
                tensiometroa = float(tensiometroa)
            else:
                tensiometroa = None

            if floresf:
                floresf = int(floresf)
            else:
                floresf = None
            
            if floresm:
                floresm = int(floresm)
            else:
                floresm = None

            if muestra:
                muestra = int(muestra)
            else:
                muestra = None

            if tamano:
                tamano = int(tamano)
            else:
                tamano = None
        
        except ValueError:
            flash('Revisar los campos con los valores', 'error')
            return redirect(url_for('estimaciones'))

        # Validación de campos obligatorios
        if not (lote and valvula and ciclo and edad):
            flash('Todos los campos obligatorios deben ser completados', 'error')
            return redirect(url_for('estimaciones'))
        



        # Datos a guardar
        data = {
            'Fecha/Hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Lote': lote,
            'Valvula': valvula,
            'Ciclo': ciclo,
            'Edad_cultivo': edad,
            'Muestra': muestra,
            'Tamaño_Muestra': tamano,
            'Flores_Femeninas': floresf,
            'Flores_Masculinas': floresm,
            'Tensiometro_12': tensiometroa,
            'Tensiometro_24': tensiometrob,
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

    return render_template('estimaciones.html')


@app.route('/ingreso_personal', methods=['GET', 'POST'])
def ingreso_personal():
    if request.method == 'POST':
        lote = request.form.get('lote')
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

        if not (lote and valvula and area and labor and encargado and personaplan and personareal):
            flash('Todos los campos son obligatorios', 'error')
            return redirect(url_for('ingreso_personal'))

        # Datos a guardar
        data = {
            'Fecha/Hora': fecha_local.strftime("%Y-%m-%d %H:%M:%S"),
            'Lote': lote,
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

@app.route('/api/valvulas', methods=['GET'])
def get_valvulas():
    lote = request.args.get('lote')
    filtered_df = pd.DataFrame(list(lotes_collection.find({'Lote': lote})))
    valvulas = filtered_df['Valvula'].unique().tolist()
    return jsonify(valvulas)

@app.route('/api/area', methods=['GET'])
def get_area():
    valvula = request.args.get('valvula')
    if not valvula:
        return jsonify({"error": "No se proporcionó la válvula."}), 400

    try:
        valvula = int(valvula)
    except ValueError:
        return jsonify({"error": "La válvula proporcionada no es válida."}), 400

    filtered_df = pd.DataFrame(list(lotes_collection.find({'Valvula': valvula})))
    areas = filtered_df['Area_mz'].dropna().unique().tolist()
    areas_dict = [{'Area_mz': round(area, 2)} for area in areas]

    return jsonify(areas_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


##app.run(host='0.0.0.0', port=5000, debug=True) para varios dispoistivos 
##app.run(debug=True) de forma local 
#http://127.0.0.1:5000/api/valvulas?lote=2004-020

#LC9CEnmshqJUu6UH: contraseña
#alexisgarcia51: usuario
#python -m pip install "pymongo[srv]" 
#mongodb+srv://alexisgarcia51:LC9CEnmshqJUu6UH@temporada2324.lug6z.mongodb.net/?retryWrites=true&w=majority&appName=temporada2324
#fly.io
#vercel
#netlify
#render
#railway
