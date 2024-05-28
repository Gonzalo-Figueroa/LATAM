def q3_time(file_path: str) -> List[Tuple[str, int]]:
    """
    Extrae y cuenta las menciones más frecuentes en los tweets.
    Optimiza el tiempo de ejecución utilizando operaciones eficientes con pandas.

    Args:
    file_path (str): Ruta al archivo JSON de tweets.

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

        # Crear un DataFrame de pandas con las menciones
        mentions_df = pd.DataFrame(mentions_list, columns=['username'])

        # Contar las menciones por usuario
        mention_counts = mentions_df['username'].value_counts().reset_index()
        mention_counts.columns = ['username', 'count']

        # Obtener los 10 usuarios más mencionados
        top_mentions = mention_counts.head(10)

        # Convertir el DataFrame de top menciones a una lista de tuplas
        top_mentions_list = list(top_mentions.itertuples(index=False, name=None))

        return top_mentions_list

    except Exception as e:
        print(f"Error al procesar el archivo JSON: {e}")
        return []
