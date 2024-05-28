def q2_memory(file_path: str) -> List[Tuple[str, int]]:
    """
    Extrae y cuenta los emojis más frecuentes en los contenidos de tweets.
    Optimiza el uso de memoria procesando los datos en lotes pequeños.

    Args:
    file_path (str): Ruta al archivo JSON de tweets.

    Returns:
    List[Tuple[str, int]]: Lista de tuplas con los emojis y su frecuencia.
    """
    try:
        # Leer los datos con Spark y agregar una columna de id para particionar los datos
        df_spark = spark.read.json(file_path).withColumn("id", monotonically_increasing_id())

        # Inicializar diccionario de emojis
        diccionario_emojis = {}

        # Definir el tamaño del lote
        batch_size = 10000

        # Contar el número total de filas
        total_rows = df_spark.count()

        # Función para extraer emojis y actualizar el diccionario
        def extraer_emojis(texto, diccionario):
            for caracter in texto:
                if emoji.is_emoji(caracter):
                    diccionario[caracter] = diccionario.get(caracter, 0) + 1
            return diccionario

        for start in range(0, total_rows, batch_size):
            # Filtrar los datos por lotes usando el número de fila
            df_batch_spark = df_spark.filter((col("id") >= start) & (col("id") < start + batch_size))
            df_batch = df_batch_spark.select("content").toPandas()
            
            # Aplicar la función de extracción de emojis a cada contenido de tweet
            for content in df_batch['content']:
                diccionario_emojis = extraer_emojis(content, diccionario_emojis)

        # Limpiar el diccionario de caracteres no deseados
        caracteres_no_deseados = ['🏻', '🏽']
        for caracter in caracteres_no_deseados:
            diccionario_emojis.pop(caracter, None)

        # Convertir diccionario a DataFrame y asegurarse de que la columna 'count' sea de tipo int
        df_emojis = pd.DataFrame(diccionario_emojis.items(), columns=['emoji', 'count'])
        df_emojis['count'] = df_emojis['count'].astype(int)
        
        # Ordenar y obtener los top 10 emojis
        top_10_emojis = df_emojis.nlargest(10, 'count')

        return list(top_10_emojis.itertuples(index=False, name=None))

    except Exception as e:
        print(f"Error al procesar el archivo JSON: {e}")
        return []

