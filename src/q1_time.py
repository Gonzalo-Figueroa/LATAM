def q1_time(file_path: str) -> List[Tuple[datetime.date, str]]:
    """
    Procesa un archivo JSON de tweets, agrupando por fecha y usuario,
    y retorna una lista de las fechas con más tweets y el usuario más activo en cada fecha.

    Args:
    file_path (str): Ruta al archivo JSON de tweets.

    Returns:
    List[Tuple[datetime.date, str]]: Lista de tuplas que contienen la fecha y el usuario más activo en esa fecha.
    """
    try:
        # Leer el archivo JSON con Spark
        df_spark = spark.read.json(file_path)
        
        # Convertir a un DataFrame de pandas
        df = df_spark.select("date", "user.username").toPandas()
        
        # Convertir la columna de fechas a tipo datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['tweet_date'] = df['date'].dt.date
        
        # Filtrar filas con fechas no convertibles
        df = df.dropna(subset=['date'])
        
        # Agrupar por fecha y contar los tweets por fecha
        df_fechas_agrupadas = df.groupby('tweet_date').size().reset_index(name='count')
        df_fechas_agrupadas = df_fechas_agrupadas.sort_values(by='count', ascending=False).head(10)
        
        # Inicializar lista para almacenar resultados
        result = []

        for _, row in df_fechas_agrupadas.iterrows():
            fecha = row['tweet_date']
            
            # Agrupar por usuario y contar los tweets, filtrando por la fecha de la iteración
            user_counts = df[df['tweet_date'] == fecha] \
                                 .groupby('username').size().reset_index(name='count') \
                                 .sort_values(by='count', ascending=False).head(1)
            
            # Obtener el usuario con más tweets en esa fecha
            if not user_counts.empty:
                top_user = user_counts.iloc[0]
                result.append((fecha, top_user['username']))
            else:
                result.append((fecha, None))
        
        return result

    except Exception as e:
        print(f"Error al procesar el archivo JSON: {e}")
        return []

