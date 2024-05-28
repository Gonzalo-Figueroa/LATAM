def q2_time(file_path: str) -> List[Tuple[str, int]]:
    """
    Extrae y cuenta los emojis más frecuentes en los contenidos de tweets.
    Optimiza el tiempo de ejecución utilizando operaciones eficientes con pandas.

    Args:
    file_path (str): Ruta al archivo JSON de tweets.

    Returns:
    List[Tuple[str, int]]: Lista de tuplas con los emojis y su frecuencia.
    """
    try:
        # Leer los datos con Spark
        df_spark = spark.read.json(file_path)
        
        # Convertir a pandas
        df = df_spark.select("content").toPandas()

        # Inicializar diccionario de emojis
        diccionario_emojis = {}

        # Función para extraer emojis y actualizar el diccionario
        def extraer_emojis(texto, diccionario):
            for caracter in texto:
                if emoji.is_emoji(caracter):
                    diccionario[caracter] = diccionario.get(caracter, 0) + 1
            return diccionario

        # Aplicar la función de extracción de emojis a cada contenido de tweet
        df['content'].apply(lambda x: extraer_emojis(x, diccionario_emojis))

        # Limpiar el diccionario de caracteres no deseados
        caracteres_no_deseados = ['🏻', '🏽']
        for caracter in caracteres_no_deseados:
            diccionario_emojis.pop(caracter, None)

        # Convertir diccionario a DataFrame y ordenar
        df_emojis = pd.DataFrame(diccionario_emojis.items(), columns=['emoji', 'count'])
        top_10_emojis = df_emojis.nlargest(10, 'count')

        return list(top_10_emojis.itertuples(index=False, name=None))

    except Exception as e:
        print(f"Error al procesar el archivo JSON: {e}")
        return []


