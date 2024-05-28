def q3_memory(file_path: str, chunk_size: int = 10000) -> List[Tuple[str, int]]:
    """
    Extrae y cuenta las menciones más frecuentes en los tweets.
    Optimiza el uso de memoria utilizando operaciones eficientes con pandas y procesamiento por chunks.

    Args:
    file_path (str): Ruta al archivo JSON de tweets.
    chunk_size (int): Tamaño del chunk para procesamiento de datos.

    Returns:
    List[Tuple[str, int]]: Lista de tuplas con los usuarios y la frecuencia de menciones.
    """
    try:
        # Leer los datos con Spark
        df_spark = spark.read.json(file_path)
        
        # Convertir a pandas
        df = df_spark.select("mentionedUsers").toPandas()

        # Inicializar una lista para almacenar las menciones
        mentions_list = []

        # Recorrer todos los registros de 'mentionedUsers'
        for index, row in df.iterrows():
            mentioned_users = row['mentionedUsers']
            if mentioned_users:
                for user in mentioned_users:
                    mentions_list.append(user['username'])

        # Crear un DataFrame vacío para acumular resultados
        all_mentions_df = pd.DataFrame(columns=['username'])

        # Procesar la lista de menciones por chunks
        for chunk in chunk_list(mentions_list, chunk_size):
            chunk_df = pd.DataFrame(chunk, columns=['username'])
            chunk_df['username'] = chunk_df['username'].astype('category')
            
            # Contar las menciones por usuario en el chunk
            chunk_mention_counts = chunk_df['username'].value_counts().reset_index()
            chunk_mention_counts.columns = ['username', 'count']
            
            # Agregar los resultados al DataFrame acumulativo
            all_mentions_df = pd.concat([all_mentions_df, chunk_mention_counts], ignore_index=True)
        
        # Agrupar y sumar los conteos finales
        final_mention_counts = all_mentions_df.groupby('username')['count'].sum().reset_index()
        
        # Obtener los 10 usuarios más mencionados
        top_mentions = final_mention_counts.nlargest(10, 'count')

        # Convertir el DataFrame de top menciones a una lista de tuplas
        top_mentions_list = list(top_mentions.itertuples(index=False, name=None))

        return top_mentions_list

    except Exception as e:
        print(f"Error al procesar el archivo JSON: {e}")
        return []
