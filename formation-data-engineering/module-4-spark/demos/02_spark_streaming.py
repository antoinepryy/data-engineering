"""
Démonstration 2: Spark Structured Streaming
Module 4 - Apache Spark
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time
import threading
import json
import random
from datetime import datetime, timedelta

# ============================================================================
# INITIALISATION SPARK STREAMING
# ============================================================================

def create_streaming_session():
    """Créer une session Spark pour le streaming"""
    spark = SparkSession.builder \
        .appName("02_Spark_Streaming_Demo") \
        .config("spark.sql.streaming.schemaInference", "true") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .config("spark.sql.adaptive.enabled", "false") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    print("=" * 80)
    print("🌊 SESSION SPARK STREAMING INITIALISÉE")
    print("=" * 80)
    print(f"Version Spark: {spark.version}")
    print(f"Checkpoint: /tmp/spark-streaming-checkpoint")
    print("=" * 80)
    
    return spark

# ============================================================================
# GÉNÉRATEUR DE DONNÉES EN TEMPS RÉEL
# ============================================================================

class DataGenerator:
    """Générateur de données pour simuler un flux temps réel"""
    
    def __init__(self, output_path="/tmp/streaming_data"):
        self.output_path = output_path
        self.running = False
        self.thread = None
        
        # Créer le répertoire si nécessaire
        import os
        os.makedirs(output_path, exist_ok=True)
    
    def generate_transaction(self):
        """Générer une transaction aléatoire"""
        products = ['iPhone', 'MacBook', 'iPad', 'AirPods', 'Watch', 'TV', 'HomePod']
        countries = ['France', 'USA', 'UK', 'Germany', 'Spain', 'Italy', 'Japan']
        payment_methods = ['card', 'paypal', 'bitcoin', 'transfer']
        
        return {
            'transaction_id': f"TXN_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'timestamp': datetime.now().isoformat(),
            'customer_id': f"CUST_{random.randint(1, 1000):04d}",
            'product': random.choice(products),
            'quantity': random.randint(1, 5),
            'unit_price': round(random.uniform(50, 3000), 2),
            'country': random.choice(countries),
            'payment_method': random.choice(payment_methods),
            'is_fraud': random.random() < 0.02  # 2% de fraude
        }
    
    def generate_clickstream(self):
        """Générer un événement de clickstream"""
        pages = ['/home', '/products', '/cart', '/checkout', '/payment', '/confirmation']
        actions = ['view', 'click', 'scroll', 'add_to_cart', 'remove_from_cart']
        devices = ['mobile', 'desktop', 'tablet']
        
        return {
            'event_id': f"EVT_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            'timestamp': datetime.now().isoformat(),
            'session_id': f"SES_{random.randint(1, 100):04d}",
            'user_id': f"USER_{random.randint(1, 500):04d}",
            'page': random.choice(pages),
            'action': random.choice(actions),
            'device': random.choice(devices),
            'duration_seconds': random.randint(1, 300)
        }
    
    def _write_batch(self):
        """Écrire un batch de données"""
        batch_size = random.randint(5, 15)
        
        # Générer des transactions
        transactions = [self.generate_transaction() for _ in range(batch_size)]
        filename = f"{self.output_path}/transactions_{int(time.time())}.json"
        with open(filename, 'w') as f:
            for tx in transactions:
                f.write(json.dumps(tx) + '\n')
        
        # Générer des clickstreams
        clicks = [self.generate_clickstream() for _ in range(batch_size * 2)]
        filename = f"{self.output_path}/clicks_{int(time.time())}.json"
        with open(filename, 'w') as f:
            for click in clicks:
                f.write(json.dumps(click) + '\n')
    
    def _run_generator(self):
        """Boucle de génération de données"""
        while self.running:
            self._write_batch()
            time.sleep(2)  # Générer des données toutes les 2 secondes
    
    def start(self):
        """Démarrer la génération de données"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_generator)
            self.thread.daemon = True
            self.thread.start()
            print("✅ Générateur de données démarré")
    
    def stop(self):
        """Arrêter la génération de données"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("⏹️  Générateur de données arrêté")

# ============================================================================
# DÉMONSTRATION 1: FILE SOURCE STREAMING
# ============================================================================

def demo_file_streaming(spark):
    """Démontrer le streaming depuis des fichiers"""
    print("\n" + "=" * 80)
    print("DÉMO 1: FILE SOURCE STREAMING")
    print("=" * 80)
    
    # Schéma des transactions
    transaction_schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("country", StringType(), True),
        StructField("payment_method", StringType(), True),
        StructField("is_fraud", BooleanType(), True)
    ])
    
    # Lire le flux de transactions
    print("\n📁 Lecture du flux de fichiers JSON...")
    stream_df = spark.readStream \
        .option("maxFilesPerTrigger", 2) \
        .schema(transaction_schema) \
        .json("/tmp/streaming_data/transactions_*.json")
    
    print("✅ Stream DataFrame créé")
    print(f"Is Streaming: {stream_df.isStreaming}")
    
    # Transformations sur le flux
    processed_stream = stream_df \
        .withColumn("total_amount", col("quantity") * col("unit_price")) \
        .withColumn("event_time", to_timestamp(col("timestamp"))) \
        .withColumn("processing_time", current_timestamp())
    
    # Query 1: Affichage console
    print("\n1️⃣ AFFICHAGE EN CONSOLE:")
    query_console = processed_stream \
        .select("transaction_id", "product", "quantity", "total_amount", "is_fraud") \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    # Attendre un peu pour voir des résultats
    time.sleep(15)
    query_console.stop()
    
    return stream_df

# ============================================================================
# DÉMONSTRATION 2: AGRÉGATIONS EN STREAMING
# ============================================================================

def demo_streaming_aggregations(spark):
    """Démontrer les agrégations en streaming"""
    print("\n" + "=" * 80)
    print("DÉMO 2: AGRÉGATIONS EN STREAMING")
    print("=" * 80)
    
    # Schéma pour les clics
    click_schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("session_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("page", StringType(), True),
        StructField("action", StringType(), True),
        StructField("device", StringType(), True),
        StructField("duration_seconds", IntegerType(), True)
    ])
    
    # Lire le flux de clics
    clicks_stream = spark.readStream \
        .schema(click_schema) \
        .json("/tmp/streaming_data/clicks_*.json")
    
    # Ajouter timestamp
    clicks_with_time = clicks_stream \
        .withColumn("event_time", to_timestamp(col("timestamp")))
    
    # 1. Agrégation simple par page
    print("\n1️⃣ AGRÉGATION PAR PAGE:")
    page_counts = clicks_with_time \
        .groupBy("page") \
        .agg(
            count("*").alias("views"),
            avg("duration_seconds").alias("avg_duration")
        )
    
    query_pages = page_counts.writeStream \
        .outputMode("complete") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(10)
    query_pages.stop()
    
    # 2. Fenêtrage temporel (Tumbling Window)
    print("\n2️⃣ FENÊTRAGE TEMPOREL (10 secondes):")
    windowed_counts = clicks_with_time \
        .withWatermark("event_time", "10 seconds") \
        .groupBy(
            window(col("event_time"), "10 seconds", "10 seconds"),
            col("device")
        ) \
        .agg(
            count("*").alias("event_count"),
            approx_count_distinct("user_id").alias("unique_users")
        )
    
    query_window = windowed_counts.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(15)
    query_window.stop()
    
    # 3. Sliding Window
    print("\n3️⃣ SLIDING WINDOW (10 sec window, 5 sec slide):")
    sliding_window = clicks_with_time \
        .withWatermark("event_time", "10 seconds") \
        .groupBy(
            window(col("event_time"), "10 seconds", "5 seconds"),
            col("action")
        ) \
        .count()
    
    query_sliding = sliding_window.writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(15)
    query_sliding.stop()

# ============================================================================
# DÉMONSTRATION 3: JOINTURES EN STREAMING
# ============================================================================

def demo_stream_joins(spark):
    """Démontrer les jointures stream-stream et stream-static"""
    print("\n" + "=" * 80)
    print("DÉMO 3: JOINTURES EN STREAMING")
    print("=" * 80)
    
    # Créer un DataFrame statique de référence
    static_products = spark.createDataFrame([
        ("iPhone", "Electronics", 1000.0),
        ("MacBook", "Computers", 2000.0),
        ("iPad", "Electronics", 800.0),
        ("AirPods", "Audio", 200.0),
        ("Watch", "Wearables", 500.0),
        ("TV", "Electronics", 1500.0),
        ("HomePod", "Audio", 300.0)
    ], ["product", "category", "base_price"])
    
    print("\n📊 DataFrame statique (Products):")
    static_products.show()
    
    # Lire le flux de transactions
    transaction_schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("country", StringType(), True),
        StructField("payment_method", StringType(), True),
        StructField("is_fraud", BooleanType(), True)
    ])
    
    transactions_stream = spark.readStream \
        .schema(transaction_schema) \
        .json("/tmp/streaming_data/transactions_*.json")
    
    # 1. Stream-Static Join
    print("\n1️⃣ STREAM-STATIC JOIN:")
    enriched_stream = transactions_stream.join(
        static_products,
        on="product",
        how="left"
    )
    
    enriched_with_calc = enriched_stream \
        .withColumn("total_amount", col("quantity") * col("unit_price")) \
        .withColumn("margin", (col("unit_price") - col("base_price")) * col("quantity")) \
        .select("transaction_id", "product", "category", "quantity", 
                "unit_price", "base_price", "total_amount", "margin")
    
    query_join = enriched_with_calc.writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(15)
    query_join.stop()
    
    # 2. Détection d'anomalies avec jointure
    print("\n2️⃣ DÉTECTION D'ANOMALIES:")
    anomaly_stream = enriched_stream \
        .withColumn("price_deviation", 
                   abs(col("unit_price") - col("base_price")) / col("base_price") * 100) \
        .filter(col("price_deviation") > 20)  # Déviation > 20%
    
    query_anomaly = anomaly_stream \
        .select("transaction_id", "product", "unit_price", "base_price", "price_deviation") \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(15)
    query_anomaly.stop()

# ============================================================================
# DÉMONSTRATION 4: OUTPUT SINKS
# ============================================================================

def demo_output_sinks(spark):
    """Démontrer différents output sinks"""
    print("\n" + "=" * 80)
    print("DÉMO 4: OUTPUT SINKS")
    print("=" * 80)
    
    # Lire le flux
    transaction_schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("product", StringType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("unit_price", DoubleType(), True),
        StructField("country", StringType(), True),
        StructField("payment_method", StringType(), True),
        StructField("is_fraud", BooleanType(), True)
    ])
    
    stream_df = spark.readStream \
        .schema(transaction_schema) \
        .json("/tmp/streaming_data/transactions_*.json")
    
    # Ajouter calculs
    processed_stream = stream_df \
        .withColumn("total_amount", col("quantity") * col("unit_price")) \
        .withColumn("event_time", to_timestamp(col("timestamp")))
    
    # 1. Memory Sink (pour debug et tests)
    print("\n1️⃣ MEMORY SINK:")
    query_memory = processed_stream \
        .select("transaction_id", "product", "total_amount") \
        .writeStream \
        .outputMode("append") \
        .format("memory") \
        .queryName("transactions_memory") \
        .start()
    
    time.sleep(10)
    
    # Lire depuis la table en mémoire
    spark.sql("SELECT * FROM transactions_memory").show()
    query_memory.stop()
    
    # 2. File Sink (Parquet)
    print("\n2️⃣ FILE SINK (Parquet):")
    query_file = processed_stream \
        .writeStream \
        .outputMode("append") \
        .format("parquet") \
        .option("path", "/tmp/streaming_output/parquet") \
        .option("checkpointLocation", "/tmp/checkpoint/parquet") \
        .trigger(processingTime='10 seconds') \
        .start()
    
    time.sleep(15)
    query_file.stop()
    
    # Vérifier les fichiers créés
    print("\n📁 Fichiers Parquet créés:")
    spark.read.parquet("/tmp/streaming_output/parquet").show(5)
    
    # 3. Foreach Batch (traitement personnalisé)
    print("\n3️⃣ FOREACH BATCH (Traitement personnalisé):")
    
    def process_batch(batch_df, batch_id):
        """Fonction pour traiter chaque micro-batch"""
        print(f"\n🔄 Traitement du batch {batch_id}:")
        
        # Statistiques du batch
        stats = batch_df.agg(
            count("*").alias("transactions"),
            sum("total_amount").alias("total_revenue"),
            avg("total_amount").alias("avg_transaction"),
            sum(when(col("is_fraud") == True, 1).otherwise(0)).alias("fraud_count")
        ).collect()[0]
        
        print(f"  - Transactions: {stats['transactions']}")
        print(f"  - Revenue: ${stats['total_revenue']:.2f}")
        print(f"  - Moyenne: ${stats['avg_transaction']:.2f}")
        print(f"  - Fraudes détectées: {stats['fraud_count']}")
        
        # Sauvegarder les fraudes
        if stats['fraud_count'] > 0:
            fraud_df = batch_df.filter(col("is_fraud") == True)
            fraud_df.coalesce(1).write.mode("append").json(f"/tmp/fraud_alerts/batch_{batch_id}")
            print(f"  ⚠️  Fraudes sauvegardées dans /tmp/fraud_alerts/batch_{batch_id}")
    
    query_foreach = processed_stream \
        .writeStream \
        .outputMode("append") \
        .foreachBatch(process_batch) \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(20)
    query_foreach.stop()

# ============================================================================
# DÉMONSTRATION 5: STATEFUL OPERATIONS
# ============================================================================

def demo_stateful_operations(spark):
    """Démontrer les opérations avec état"""
    print("\n" + "=" * 80)
    print("DÉMO 5: OPÉRATIONS AVEC ÉTAT (STATEFUL)")
    print("=" * 80)
    
    # Schéma pour les clics
    click_schema = StructType([
        StructField("event_id", StringType(), True),
        StructField("timestamp", StringType(), True),
        StructField("session_id", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("page", StringType(), True),
        StructField("action", StringType(), True),
        StructField("device", StringType(), True),
        StructField("duration_seconds", IntegerType(), True)
    ])
    
    clicks_stream = spark.readStream \
        .schema(click_schema) \
        .json("/tmp/streaming_data/clicks_*.json")
    
    clicks_with_time = clicks_stream \
        .withColumn("event_time", to_timestamp(col("timestamp")))
    
    # 1. Déduplication
    print("\n1️⃣ DÉDUPLICATION (basée sur event_id):")
    deduplicated = clicks_with_time \
        .withWatermark("event_time", "10 seconds") \
        .dropDuplicates(["event_id"])
    
    query_dedup = deduplicated \
        .select("event_id", "user_id", "page", "action") \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(10)
    query_dedup.stop()
    
    # 2. Session Windows (regroupement par session)
    print("\n2️⃣ SESSION WINDOWS:")
    session_stats = clicks_with_time \
        .withWatermark("event_time", "10 minutes") \
        .groupBy(
            col("session_id"),
            session_window(col("event_time"), "5 minutes")
        ) \
        .agg(
            count("*").alias("events_count"),
            min("event_time").alias("session_start"),
            max("event_time").alias("session_end"),
            collect_list("page").alias("pages_visited")
        )
    
    query_session = session_stats.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .trigger(processingTime='10 seconds') \
        .start()
    
    time.sleep(20)
    query_session.stop()
    
    # 3. Running Totals (agrégations cumulatives)
    print("\n3️⃣ RUNNING TOTALS (Agrégations cumulatives):")
    running_totals = clicks_with_time \
        .groupBy("user_id") \
        .agg(
            count("*").alias("total_events"),
            approx_count_distinct("session_id").alias("total_sessions"),
            sum("duration_seconds").alias("total_duration")
        )
    
    query_running = running_totals.writeStream \
        .outputMode("complete") \
        .format("console") \
        .trigger(processingTime='5 seconds') \
        .start()
    
    time.sleep(15)
    query_running.stop()

# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    """Fonction principale pour exécuter les démonstrations streaming"""
    
    # Créer la session Spark
    spark = create_streaming_session()
    
    # Créer et démarrer le générateur de données
    generator = DataGenerator()
    
    try:
        print("\n🚀 DÉMARRAGE DU GÉNÉRATEUR DE DONNÉES...")
        generator.start()
        time.sleep(3)  # Attendre que quelques fichiers soient créés
        
        # Exécuter les démonstrations
        demo_file_streaming(spark)
        demo_streaming_aggregations(spark)
        demo_stream_joins(spark)
        demo_output_sinks(spark)
        demo_stateful_operations(spark)
        
        print("\n" + "=" * 80)
        print("🎉 TOUTES LES DÉMONSTRATIONS STREAMING TERMINÉES!")
        print("=" * 80)
        print("\n📊 CONCEPTS COUVERTS:")
        print("  ✅ File Source Streaming")
        print("  ✅ Agrégations en streaming")
        print("  ✅ Fenêtrage temporel (Tumbling, Sliding, Session)")
        print("  ✅ Jointures (Stream-Static, Stream-Stream)")
        print("  ✅ Output Sinks (Console, Memory, File, ForeachBatch)")
        print("  ✅ Opérations avec état (Déduplication, Sessions)")
        print("  ✅ Watermarks et Late Data")
        
    finally:
        # Arrêter le générateur
        print("\n⏹️  Arrêt du générateur de données...")
        generator.stop()
        
        # Fermer la session Spark
        input("\n⏸️  Appuyez sur Entrée pour terminer...")
        spark.stop()
        print("✅ Session Spark Streaming fermée")

if __name__ == "__main__":
    main()