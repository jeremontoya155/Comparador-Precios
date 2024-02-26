from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

app = Flask(__name__)

# Función para obtener productos y precios de Farmacia Líder
def obtener_productos_farmacia_lider(num_paginas=15):
    resultados_farmacia_lider = []

    urls_farmacia_lider = [
        "https://farmaciaslider.com.ar/10-dermocosmetica",
        "https://farmaciaslider.com.ar/12-cuidado-e-higiene-personal",
        "https://farmaciaslider.com.ar/21-perfumes-y-fragancias",
        "https://farmaciaslider.com.ar/14-maquillaje",
        "https://farmaciaslider.com.ar/70-nutricion"
    ]

    for url_categoria in urls_farmacia_lider:
        for pagina in range(1, num_paginas + 1):
            url_pagina = f"{url_categoria}?page={pagina}"
            response_pagina = requests.get(url_pagina)

            if response_pagina.status_code == 200:
                soup_pagina = BeautifulSoup(response_pagina.text, 'html.parser')
                productos = soup_pagina.find_all('h3', class_='h3 product-title')
                precios = soup_pagina.find_all('span', class_='product-price')

                for producto, precio in zip(productos, precios):
                    nombre_producto = producto.text.strip()
                    precio_producto = precio.text.strip()
                    resultados_farmacia_lider.append([nombre_producto, precio_producto])

    return resultados_farmacia_lider

# Función para obtener productos de Farmacia General Paz
def obtener_productos_farmacia_general_paz(num_paginas=50):
    resultados_farmacia_general_paz = []

    urls_farmacia_general_paz = [
        "https://www.farmaciageneralpaz.com/shop/dermocosmetica-PC1155",
        "https://www.farmaciageneralpaz.com/shop/perfumes-PC1156",
        "https://www.farmaciageneralpaz.com/shop/maquillajes",
        "https://www.farmaciageneralpaz.com/shop/cuidado-personal-PC8877"
    ]

    for url_categoria in urls_farmacia_general_paz:
        for pagina in range(1, num_paginas + 1):
            url_pagina = f"{url_categoria}?pagina={pagina}"
            response_pagina = requests.get(url_pagina)

            if response_pagina.status_code == 200:
                soup_pagina = BeautifulSoup(response_pagina.text, 'html.parser')
                nombres_productos_pagina = soup_pagina.find_all('h3', class_='kw-details-title')
                precios_pagina = soup_pagina.find_all('span', class_='amount')

                for nombre, precio in zip(nombres_productos_pagina, precios_pagina):
                    nombre_producto = nombre.find('span', class_='child-top').get_text().strip()
                    precio_producto = precio.get_text().strip()
                    resultados_farmacia_general_paz.append([nombre_producto, precio_producto])

    return resultados_farmacia_general_paz


# Función para obtener productos y precios de Ferniplast
def obtener_productos_ferniplast():
    resultados_ferniplast = []

    url_ferniplast = "https://www.ferniplast.com/perfumeria/ofertas?initialMap=productClusterIds&initialQuery=140&map=category-1,productclusternames&page={}"

    pagina = 1
    while True:
        url_pagina = url_ferniplast.format(pagina)
        response_pagina = requests.get(url_pagina)

        if response_pagina.status_code == 200:
            soup_pagina = BeautifulSoup(response_pagina.text, 'html.parser')
            nombres_productos = soup_pagina.find_all('span', class_='vtex-product-summary-2-x-productBrand')
            precios = soup_pagina.find_all('span', class_='vtex-product-summary-2-x-currencyInteger')

            if len(nombres_productos) == 0:
                break  # No hay más páginas

            for nombre, precio in zip(nombres_productos, precios):
                nombre_producto = nombre.text.strip()
                precio_producto = precio.text.strip()
                resultados_ferniplast.append([nombre_producto, precio_producto])

            pagina += 1
        else:
            break  # Error al cargar la página

    return resultados_ferniplast

# Función para obtener productos de Super Mami
def obtener_productos_super_mami(num_paginas=65):
    resultados_super_mami = []

    for pagina in range(1, num_paginas + 1):
        url_pagina = f"https://www.dinoonline.com.ar/super/categoria/supermami-perfumeria/_/N-146amvi?No={pagina * 36}&Nrpp=36"
        response_pagina = requests.get(url_pagina)

        if response_pagina.status_code == 200:
            soup_pagina = BeautifulSoup(response_pagina.text, 'html.parser')
            nombres_productos_pagina = soup_pagina.find_all('div', class_='description limitRow tooltipHere')
            precios_pagina = soup_pagina.find_all('div', class_='precio-unidad')

            for nombre, precio in zip(nombres_productos_pagina, precios_pagina):
                nombre_producto = nombre.get_text().strip()
                precio_producto = precio.find('span').get_text().strip()
                resultados_super_mami.append([nombre_producto, precio_producto])

    return resultados_super_mami

# Función para exportar resultados a un archivo Excel
def exportar_a_excel(resultados, nombre_archivo):
    if resultados:
        with pd.ExcelWriter(nombre_archivo, engine='openpyxl') as writer:
            for origen, data in resultados.items():
                df = pd.DataFrame(data, columns=["Nombre del Producto", "Precio"])
                df['Origen'] = origen  # Agregar una columna 'Origen' con el nombre del origen
                df.to_excel(writer, sheet_name=origen, index=False)
            
            # Agregar una hoja adicional con todos los productos y su origen
            df_all = pd.concat([pd.DataFrame(data, columns=["Nombre del Producto", "Precio"]).assign(Origen=origen) for origen, data in resultados.items()], ignore_index=True)
            df_all.to_excel(writer, sheet_name='Todos los Productos', index=False)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para realizar el scraping y descargar los resultados
@app.route('/scrape', methods=['POST'])
def scrape():
    resultados = {}
    if request.form.get('farmacia_lider'):
        resultados['Farmacia Líder'] = obtener_productos_farmacia_lider(int(request.form.get('num_paginas')))
    if request.form.get('farmacia_general_paz'):
        resultados['Farmacia General Paz'] = obtener_productos_farmacia_general_paz(int(request.form.get('num_paginas')))
    if request.form.get('super_mami'):
        resultados['Super Mami'] = obtener_productos_super_mami(int(request.form.get('num_paginas')))
    if request.form.get('ferniplast'):
        resultados['Ferniplast'] = obtener_productos_ferniplast()     
    
    nombre_archivo = "resultados.xlsx"
    exportar_a_excel(resultados, nombre_archivo)
    return send_file(nombre_archivo, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
