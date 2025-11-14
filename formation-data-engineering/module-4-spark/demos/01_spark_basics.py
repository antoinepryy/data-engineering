"""
Démonstration 1: Les Bases de Spark
Module 4 - Apache Spark
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time
import random

# ============================================================================
# INITIALISATION SPARK
# ============================================================================

def create_spark_session():
    """Créer une session Spark avec configuration optimisée"""
    spark = SparkSession.builder \
        .appName("01_Spark_Basics_Demo") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .config("spark.ui.showConsoleProgress", "true") \
        .getOrCreate()
    
    # Configuration du niveau de log
    spark.sparkContext.setLogLevel("WARN")
    
    print("=" * 80)
    print("🚀 SESSION SPARK INITIALISÉE")
    print("=" * 80)
    print(f"Version Spark: {spark.version}")
    print(f"Application ID: {spark.sparkContext.applicationId}")
    print(f"Spark UI: http://localhost:4040")
    print("=" * 80)
    
    return spark

# ============================================================================
# CRÉATION DE DONNÉES DE DÉMONSTRATION
# ============================================================================

def create_sample_data(spark, num_records=10000):
    """Créer un DataFrame avec des données de démonstration"""
    print("\n📊 Création de données de démonstration...")
    
    # Générer des données aléatoires
    data = []
    products = ['Laptop', 'Phone', 'Tablet', 'Headphones', 'Speaker', 'Watch', 'Camera']
    categories = ['Electronics', 'Audio', 'Wearables', 'Computing']
    countries = ['France', 'USA', 'Germany', 'UK', 'Spain', 'Italy', 'Japan']
    
    for i in range(num_records):
        data.append({
            'order_id': i + 1,
            'product': random.choice(products),
            'category': random.choice(categories),
            'quantity': random.randint(1, 10),
            'unit_price': round(random.uniform(50, 2000), 2),
            'discount': round(random.uniform(0, 0.3), 2),
            'customer_id': random.randint(1, 1000),
            'country': random.choice(countries),
            'order_date': f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            'is_premium': random.choice([True, False])
        })
    
    # Créer le DataFrame
    df = spark.createDataFrame(data)
    
    print(f"✅ DataFrame créé avec {df.count()} lignes")
    print(f"📋 Colonnes: {df.columns}")
    
    return df

# ============================================================================
# DÉMONSTRATION 1: OPÉRATIONS BASIQUES
# ============================================================================

def demo_basic_operations(spark, df):
    """Démontrer les opérations basiques sur DataFrame"""
    print("\n" + "=" * 80)
    print("DÉMO 1: OPÉRATIONS BASIQUES")
    print("=" * 80)
    
    # 1. Afficher le schéma
    print("\n1️⃣ SCHÉMA DU DATAFRAME:")
    df.printSchema()
    
    # 2. Afficher les premières lignes
    print("\n2️⃣ PREMIÈRES LIGNES:")
    df.show(5, truncate=False)
    
    # 3. Statistiques descriptives
    print("\n3️⃣ STATISTIQUES DESCRIPTIVES:")
    df.describe(['quantity', 'unit_price', 'discount']).show()
    
    # 4. Sélection de colonnes
    print("\n4️⃣ SÉLECTION DE COLONNES:")
    df.select('order_id', 'product', 'quantity', 'unit_price').show(5)
    
    # 5. Filtrage
    print("\n5️⃣ FILTRAGE (Quantity > 5):")
    df.filter(col('quantity') > 5).show(5)
    
    # 6. Ajout de colonnes calculées
    print("\n6️⃣ COLONNES CALCULÉES:")
    df_with_total = df.withColumn(
        'total_price', 
        col('quantity') * col('unit_price') * (1 - col('discount'))
    )
    df_with_total.select('order_id', 'quantity', 'unit_price', 'discount', 'total_price').show(5)
    
    return df_with_total

# ============================================================================
# DÉMONSTRATION 2: AGRÉGATIONS
# ============================================================================

def demo_aggregations(spark, df):
    """Démontrer les agrégations et groupements"""
    print("\n" + "=" * 80)
    print("DÉMO 2: AGRÉGATIONS ET GROUPEMENTS")
    print("=" * 80)
    
    # 1. Agrégations simples
    print("\n1️⃣ AGRÉGATIONS SIMPLES:")
    df.agg(
        count("*").alias("total_orders"),
        sum("quantity").alias("total_quantity"),
        avg("unit_price").alias("avg_price"),
        max("unit_price").alias("max_price"),
        min("unit_price").alias("min_price")
    ).show()
    
    # 2. Group By simple
    print("\n2️⃣ GROUP BY PAR PRODUIT:")
    product_stats = df.groupBy("product").agg(
        count("*").alias("orders_count"),
        sum("quantity").alias("total_sold"),
        avg("unit_price").alias("avg_price"),
        sum(col("quantity") * col("unit_price") * (1 - col("discount"))).alias("revenue")
    ).orderBy(desc("revenue"))
    product_stats.show()
    
    # 3. Group By multiple colonnes
    print("\n3️⃣ GROUP BY MULTIPLE (Category, Country):")
    category_country = df.groupBy("category", "country").agg(
        count("*").alias("orders"),
        sum("quantity").alias("units_sold")
    ).orderBy("category", "country")
    category_country.show(10)
    
    # 4. Pivot
    print("\n4️⃣ PIVOT TABLE (Products by Country):")
    pivot_table = df.groupBy("product").pivot("country").sum("quantity")
    pivot_table.show()
    
    # 5. Window Functions
    print("\n5️⃣ WINDOW FUNCTIONS (Ranking):")
    from pyspark.sql.window import Window
    
    window_spec = Window.partitionBy("category").orderBy(desc("unit_price"))
    df_ranked = df.withColumn("rank", rank().over(window_spec))
    df_ranked.select("category", "product", "unit_price", "rank") \
        .filter(col("rank") <= 3) \
        .show()
    
    return product_stats

# ============================================================================
# DÉMONSTRATION 3: JOINS
# ============================================================================

def demo_joins(spark):
    """Démontrer les différents types de jointures"""
    print("\n" + "=" * 80)
    print("DÉMO 3: JOINTURES")
    print("=" * 80)
    
    # Créer deux DataFrames pour les jointures
    customers = spark.createDataFrame([
        (1, "Alice", "France"),
        (2, "Bob", "USA"),
        (3, "Charlie", "UK"),
        (4, "Diana", "Germany"),
        (5, "Eve", "Spain")
    ], ["customer_id", "name", "country"])
    
    orders = spark.createDataFrame([
        (101, 1, 1500.00),
        (102, 2, 2300.00),
        (103, 1, 800.00),
        (104, 3, 1200.00),
        (105, 6, 500.00)  # Customer 6 n'existe pas
    ], ["order_id", "customer_id", "amount"])
    
    print("\n📊 DataFrame Customers:")
    customers.show()
    
    print("\n📊 DataFrame Orders:")
    orders.show()
    
    # 1. Inner Join
    print("\n1️⃣ INNER JOIN:")
    inner = customers.join(orders, on="customer_id", how="inner")
    inner.show()
    
    # 2. Left Join
    print("\n2️⃣ LEFT JOIN:")
    left = customers.join(orders, on="customer_id", how="left")
    left.show()
    
    # 3. Right Join
    print("\n3️⃣ RIGHT JOIN:")
    right = customers.join(orders, on="customer_id", how="right")
    right.show()
    
    # 4. Full Outer Join
    print("\n4️⃣ FULL OUTER JOIN:")
    full = customers.join(orders, on="customer_id", how="full")
    full.show()
    
    # 5. Cross Join
    print("\n5️⃣ CROSS JOIN (limité):")
    # Créer de petits DataFrames pour le cross join
    colors = spark.createDataFrame([("Red",), ("Blue",), ("Green",)], ["color"])
    sizes = spark.createDataFrame([("S",), ("M",), ("L",)], ["size"])
    cross = colors.crossJoin(sizes)
    cross.show()

# ============================================================================
# DÉMONSTRATION 4: UDF (User Defined Functions)
# ============================================================================

def demo_udf(spark, df):
    """Démontrer l'utilisation des UDF"""
    print("\n" + "=" * 80)
    print("DÉMO 4: USER DEFINED FUNCTIONS (UDF)")
    print("=" * 80)
    
    # 1. UDF simple
    def categorize_price(price):
        if price < 100:
            return "Budget"
        elif price < 500:
            return "Standard"
        elif price < 1000:
            return "Premium"
        else:
            return "Luxury"
    
    # Enregistrer l'UDF
    categorize_price_udf = udf(categorize_price, StringType())
    
    print("\n1️⃣ UDF SIMPLE (Catégorisation des prix):")
    df_categorized = df.withColumn("price_category", categorize_price_udf(col("unit_price")))
    df_categorized.select("product", "unit_price", "price_category").show(10)
    
    # 2. UDF avec multiple paramètres
    def calculate_margin(price, cost_percentage=0.6):
        cost = price * cost_percentage
        margin = price - cost
        return round(margin, 2)
    
    calculate_margin_udf = udf(lambda x: calculate_margin(x), FloatType())
    
    print("\n2️⃣ UDF AVEC CALCULS (Marge):")
    df_margin = df.withColumn("estimated_margin", calculate_margin_udf(col("unit_price")))
    df_margin.select("product", "unit_price", "estimated_margin").show(10)
    
    # 3. UDF vectorisée (Pandas UDF) - Plus performante
    from pyspark.sql.functions import pandas_udf
    import pandas as pd
    
    @pandas_udf(returnType=FloatType())
    def calculate_tax_pandas(prices: pd.Series) -> pd.Series:
        return prices * 0.20  # 20% TVA
    
    print("\n3️⃣ PANDAS UDF (Calcul TVA - Plus rapide):")
    df_tax = df.withColumn("tax_amount", calculate_tax_pandas(col("unit_price")))
    df_tax.select("product", "unit_price", "tax_amount").show(10)
    
    return df_categorized

# ============================================================================
# DÉMONSTRATION 5: OPTIMISATION ET PERFORMANCE
# ============================================================================

def demo_optimization(spark, df):
    """Démontrer les techniques d'optimisation"""
    print("\n" + "=" * 80)
    print("DÉMO 5: OPTIMISATION ET PERFORMANCE")
    print("=" * 80)
    
    # 1. Partitioning
    print("\n1️⃣ PARTITIONING:")
    print(f"Nombre de partitions actuel: {df.rdd.getNumPartitions()}")
    
    # Repartitionner
    df_repartitioned = df.repartition(10)
    print(f"Après repartition: {df_repartitioned.rdd.getNumPartitions()}")
    
    # Coalesce (plus efficace pour réduire les partitions)
    df_coalesced = df.coalesce(5)
    print(f"Après coalesce: {df_coalesced.rdd.getNumPartitions()}")
    
    # 2. Caching
    print("\n2️⃣ CACHING:")
    start_time = time.time()
    count1 = df.count()
    time1 = time.time() - start_time
    print(f"Première exécution (sans cache): {time1:.2f} secondes")
    
    # Mettre en cache
    df.cache()
    
    start_time = time.time()
    count2 = df.count()
    time2 = time.time() - start_time
    print(f"Deuxième exécution (avec cache): {time2:.2f} secondes")
    print(f"Amélioration: {((time1-time2)/time1*100):.1f}%")
    
    # 3. Broadcast Join
    print("\n3️⃣ BROADCAST JOIN:")
    # Créer un petit DataFrame pour broadcast
    small_df = spark.createDataFrame([
        ("Electronics", 1.1),
        ("Audio", 1.05),
        ("Wearables", 1.15),
        ("Computing", 1.08)
    ], ["category", "multiplier"])
    
    print("Petit DataFrame à broadcaster:")
    small_df.show()
    
    # Broadcast join
    df_multiplied = df.join(broadcast(small_df), on="category", how="left")
    df_multiplied = df_multiplied.withColumn(
        "adjusted_price", 
        col("unit_price") * col("multiplier")
    )
    
    print("\nRésultat avec Broadcast Join:")
    df_multiplied.select("product", "category", "unit_price", "multiplier", "adjusted_price").show(5)
    
    # 4. Explain Plan
    print("\n4️⃣ PLAN D'EXÉCUTION:")
    df_multiplied.explain(True)
    
    # Nettoyer le cache
    df.unpersist()

# ============================================================================
# DÉMONSTRATION 6: SPARK SQL
# ============================================================================

def demo_spark_sql(spark, df):
    """Démontrer l'utilisation de Spark SQL"""
    print("\n" + "=" * 80)
    print("DÉMO 6: SPARK SQL")
    print("=" * 80)
    
    # Enregistrer le DataFrame comme vue temporaire
    df.createOrReplaceTempView("orders")
    
    # 1. Requête simple
    print("\n1️⃣ REQUÊTE SQL SIMPLE:")
    result1 = spark.sql("""
        SELECT product, 
               COUNT(*) as order_count,
               AVG(unit_price) as avg_price
        FROM orders
        GROUP BY product
        ORDER BY order_count DESC
        LIMIT 5
    """)
    result1.show()
    
    # 2. Requête avec CTE
    print("\n2️⃣ REQUÊTE AVEC CTE:")
    result2 = spark.sql("""
        WITH product_stats AS (
            SELECT 
                product,
                category,
                SUM(quantity) as total_quantity,
                AVG(unit_price) as avg_price,
                SUM(quantity * unit_price * (1 - discount)) as revenue
            FROM orders
            GROUP BY product, category
        )
        SELECT 
            category,
            COUNT(DISTINCT product) as product_count,
            SUM(revenue) as total_revenue,
            AVG(avg_price) as category_avg_price
        FROM product_stats
        GROUP BY category
        ORDER BY total_revenue DESC
    """)
    result2.show()
    
    # 3. Window Functions en SQL
    print("\n3️⃣ WINDOW FUNCTIONS EN SQL:")
    result3 = spark.sql("""
        SELECT 
            product,
            category,
            unit_price,
            RANK() OVER (PARTITION BY category ORDER BY unit_price DESC) as price_rank,
            PERCENT_RANK() OVER (PARTITION BY category ORDER BY unit_price) as price_percentile,
            LAG(unit_price, 1) OVER (PARTITION BY category ORDER BY order_id) as prev_price
        FROM orders
        WHERE category = 'Electronics'
        LIMIT 10
    """)
    result3.show()
    
    # 4. Requête complexe avec sous-requêtes
    print("\n4️⃣ REQUÊTE COMPLEXE:")
    result4 = spark.sql("""
        SELECT 
            o.country,
            o.product_count,
            o.total_revenue,
            o.total_revenue / t.global_revenue * 100 as revenue_percentage
        FROM (
            SELECT 
                country,
                COUNT(DISTINCT product) as product_count,
                SUM(quantity * unit_price * (1 - discount)) as total_revenue
            FROM orders
            GROUP BY country
        ) o
        CROSS JOIN (
            SELECT SUM(quantity * unit_price * (1 - discount)) as global_revenue
            FROM orders
        ) t
        ORDER BY total_revenue DESC
    """)
    result4.show()
    
    return result4

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """Fonction principale pour exécuter toutes les démonstrations"""
    
    # Créer la session Spark
    spark = create_spark_session()
    
    try:
        # Créer les données de démonstration
        df = create_sample_data(spark, num_records=10000)
        
        # Exécuter les démonstrations
        df_with_total = demo_basic_operations(spark, df)
        product_stats = demo_aggregations(spark, df_with_total)
        demo_joins(spark)
        df_categorized = demo_udf(spark, df)
        demo_optimization(spark, df)
        sql_result = demo_spark_sql(spark, df)
        
        print("\n" + "=" * 80)
        print("🎉 TOUTES LES DÉMONSTRATIONS TERMINÉES AVEC SUCCÈS!")
        print("=" * 80)
        print("\n📊 RÉSUMÉ DES CONCEPTS COUVERTS:")
        print("  ✅ Création et manipulation de DataFrames")
        print("  ✅ Opérations de sélection et filtrage")
        print("  ✅ Agrégations et groupements")
        print("  ✅ Jointures (inner, left, right, full, cross)")
        print("  ✅ Window Functions")
        print("  ✅ User Defined Functions (UDF)")
        print("  ✅ Optimisation (partitioning, caching, broadcast)")
        print("  ✅ Spark SQL")
        print("\n💡 Consultez l'UI Spark sur http://localhost:4040")
        
    finally:
        # Fermer la session Spark
        input("\n⏸️  Appuyez sur Entrée pour terminer...")
        spark.stop()
        print("✅ Session Spark fermée")

if __name__ == "__main__":
    main()