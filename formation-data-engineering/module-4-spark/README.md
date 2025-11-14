# ⚡ Module 4: Apache Spark
## Formation Data Engineering - Big Data Processing

---

## 🎯 Objectifs du Module

- Maîtriser Apache Spark pour le traitement de données massives
- Comprendre l'architecture distribuée de Spark
- Développer avec PySpark (DataFrames, SQL, Streaming)
- Optimiser les performances des jobs Spark
- Implémenter du streaming temps réel avec Structured Streaming
- Utiliser Spark ML pour le machine learning distribué

---

## 🏗️ Architecture Apache Spark

```
┌────────────────────────────────────────────────────────────┐
│                     Driver Program                          │
│                    (SparkContext)                          │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    Cluster Manager                          │
│              (Standalone/YARN/Mesos/K8s)                   │
└────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Worker 1    │     │   Worker 2    │     │   Worker 3    │
│              │     │              │     │              │
│  Executor    │     │  Executor    │     │  Executor    │
│   ┌─────┐    │     │   ┌─────┐    │     │   ┌─────┐    │
│   │Task │    │     │   │Task │    │     │   │Task │    │
│   │Task │    │     │   │Task │    │     │   │Task │    │
│   └─────┘    │     │   └─────┘    │     │   └─────┘    │
└──────────────┘     └──────────────┘     └──────────────┘
```

---

## 🚀 Démarrage Rapide

### 1. Lancer l'environnement Spark

```bash
# Depuis le dossier principal
cd formation-data-engineering

# Démarrer le cluster Spark
docker-compose up -d spark-master spark-worker-1 spark-worker-2

# Vérifier le cluster
docker-compose ps

# Accéder à Spark UI
open http://localhost:9090
```

### 2. Lancer PySpark

```bash
# Accéder au container master
docker exec -it spark-master bash

# Lancer PySpark interactif
pyspark --master spark://spark-master:7077

# Ou Python avec Spark
python
>>> from pyspark.sql import SparkSession
>>> spark = SparkSession.builder.appName("test").getOrCreate()
```

### 3. Soumettre un Job

```bash
# Soumettre un job Python
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --driver-memory 2g \
  --executor-memory 2g \
  --executor-cores 2 \
  /opt/spark-apps/demos/01_spark_basics.py
```

---

## 📚 Concepts Fondamentaux

### RDD vs DataFrame vs Dataset

| Aspect | RDD | DataFrame | Dataset |
|--------|-----|-----------|---------|
| **Type** | Low-level | High-level | High-level |
| **Schema** | Non | Oui | Oui |
| **Optimisation** | Limitée | Catalyst | Catalyst |
| **API** | Functional | SQL + DSL | Type-safe |
| **Performance** | Base | Optimisée | Optimisée |

### Transformations vs Actions

**Transformations** (Lazy):
- `map()`, `filter()`, `select()`, `join()`, `groupBy()`
- Créent un nouveau RDD/DataFrame
- Ne sont pas exécutées immédiatement

**Actions** (Eager):
- `collect()`, `count()`, `show()`, `save()`
- Déclenchent l'exécution
- Retournent un résultat

---

## 💻 Exercices Pratiques

### Exercice 1: DataFrames et SQL (45 min)

**Objectif**: Analyser un dataset e-commerce avec Spark SQL

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# 1. Créer la session
spark = SparkSession.builder \
    .appName("Exercice1_DataFrame") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# 2. Charger les données
# Option A: Créer des données de test
data = [
    (1, "iPhone", "Electronics", 999.99, 10, "2024-01-15"),
    (2, "MacBook", "Computers", 1999.99, 5, "2024-01-16"),
    (3, "AirPods", "Audio", 199.99, 25, "2024-01-17"),
    # ... plus de données
]

columns = ["product_id", "name", "category", "price", "stock", "date"]
df = spark.createDataFrame(data, columns)

# 3. Transformations DataFrame
# TODO: Calculer le revenue potentiel (price * stock)
df_with_revenue = df.withColumn("potential_revenue", col("price") * col("stock"))

# TODO: Filtrer les produits > $500
expensive_products = df_with_revenue.filter(col("price") > 500)

# TODO: Grouper par catégorie
category_stats = df_with_revenue.groupBy("category").agg(
    count("*").alias("product_count"),
    sum("potential_revenue").alias("total_revenue"),
    avg("price").alias("avg_price")
)

# 4. Spark SQL
df.createOrReplaceTempView("products")

# TODO: Écrire une requête SQL équivalente
sql_result = spark.sql("""
    SELECT 
        category,
        COUNT(*) as product_count,
        SUM(price * stock) as total_revenue,
        AVG(price) as avg_price
    FROM products
    GROUP BY category
    ORDER BY total_revenue DESC
""")

sql_result.show()

# 5. Sauvegarder les résultats
category_stats.write \
    .mode("overwrite") \
    .parquet("/tmp/category_stats")
```

### Exercice 2: Optimisation des Performances (60 min)

**Objectif**: Optimiser un job Spark lent

```python
# Problème: Ce code est LENT
def slow_version(spark):
    # Charger un gros fichier
    df = spark.read.json("/data/large_file.json")
    
    # Multiples transformations
    result = df.filter(col("amount") > 100)
    result = result.filter(col("status") == "completed")
    result = result.filter(col("country").isin(["FR", "US", "UK"]))
    
    # Jointure non optimisée
    customers = spark.read.csv("/data/customers.csv")
    joined = result.join(customers, "customer_id")
    
    # Agrégation
    final = joined.groupBy("country", "category").sum("amount")
    final.show()
    
    return final

# Solution optimisée
def optimized_version(spark):
    # 1. Combiner les filtres
    df = spark.read.json("/data/large_file.json")
    filtered = df.filter(
        (col("amount") > 100) & 
        (col("status") == "completed") &
        (col("country").isin(["FR", "US", "UK"]))
    )
    
    # 2. Broadcast join pour petite table
    customers = spark.read.csv("/data/customers.csv")
    from pyspark.sql.functions import broadcast
    joined = filtered.join(broadcast(customers), "customer_id")
    
    # 3. Repartition avant agrégation
    joined_repartitioned = joined.repartition("country", "category")
    
    # 4. Cache si réutilisation
    joined_repartitioned.cache()
    
    # 5. Agrégation
    final = joined_repartitioned.groupBy("country", "category").sum("amount")
    
    # 6. Coalesce pour réduire les partitions de sortie
    final.coalesce(10).show()
    
    return final

# Mesurer les performances
import time

start = time.time()
slow_result = slow_version(spark)
slow_time = time.time() - start

start = time.time()
fast_result = optimized_version(spark)
fast_time = time.time() - start

print(f"Version lente: {slow_time:.2f}s")
print(f"Version optimisée: {fast_time:.2f}s")
print(f"Amélioration: {((slow_time - fast_time) / slow_time * 100):.1f}%")
```

### Exercice 3: Structured Streaming (60 min)

**Objectif**: Créer un pipeline de streaming temps réel

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# 1. Setup
spark = SparkSession.builder \
    .appName("Exercice3_Streaming") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

# 2. Définir le schéma
schema = StructType([
    StructField("event_id", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("user_id", StringType()),
    StructField("action", StringType()),
    StructField("product_id", StringType()),
    StructField("amount", DoubleType())
])

# 3. Lire le stream
# TODO: Créer un stream depuis des fichiers JSON
stream_df = spark.readStream \
    .option("maxFilesPerTrigger", 1) \
    .schema(schema) \
    .json("/data/streaming/events/*.json")

# 4. Transformations
# TODO: Ajouter watermark pour gérer les données en retard
with_watermark = stream_df \
    .withWatermark("timestamp", "10 minutes")

# TODO: Calculer les métriques par fenêtre de temps
windowed_stats = with_watermark \
    .groupBy(
        window(col("timestamp"), "5 minutes", "1 minute"),
        col("action")
    ) \
    .agg(
        count("*").alias("event_count"),
        sum("amount").alias("total_amount"),
        avg("amount").alias("avg_amount")
    )

# 5. Output
# TODO: Écrire vers la console
query = windowed_stats.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .trigger(processingTime='10 seconds') \
    .start()

# Attendre 1 minute
query.awaitTermination(60)
query.stop()

# 6. Sink vers fichiers Parquet
# TODO: Sauvegarder les résultats
file_query = windowed_stats.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/data/output/streaming_results") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .trigger(processingTime='30 seconds') \
    .start()

file_query.awaitTermination(120)
file_query.stop()
```

### Exercice 4: Spark ML - Machine Learning (90 min)

**Objectif**: Créer un pipeline ML pour prédire les ventes

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder

# 1. Charger les données
data = spark.read.csv("/data/sales_data.csv", header=True, inferSchema=True)

# 2. Préparation des features
# TODO: Encoder les catégories
category_indexer = StringIndexer(inputCol="category", outputCol="category_index")
country_indexer = StringIndexer(inputCol="country", outputCol="country_index")

# TODO: Assembler les features
assembler = VectorAssembler(
    inputCols=["price", "quantity", "category_index", "country_index", "discount"],
    outputCol="features_raw"
)

# TODO: Normaliser
scaler = StandardScaler(inputCol="features_raw", outputCol="features")

# 3. Modèle
# TODO: Classifier RandomForest
rf = RandomForestClassifier(
    labelCol="sale_success",
    featuresCol="features",
    numTrees=100
)

# 4. Pipeline
pipeline = Pipeline(stages=[
    category_indexer,
    country_indexer,
    assembler,
    scaler,
    rf
])

# 5. Train/Test Split
train, test = data.randomSplit([0.8, 0.2], seed=42)

# 6. Cross-Validation
# TODO: Grid search pour hyperparamètres
paramGrid = ParamGridBuilder() \
    .addGrid(rf.numTrees, [50, 100, 200]) \
    .addGrid(rf.maxDepth, [5, 10, 15]) \
    .build()

evaluator = MulticlassClassificationEvaluator(
    labelCol="sale_success",
    predictionCol="prediction",
    metricName="accuracy"
)

crossval = CrossValidator(
    estimator=pipeline,
    estimatorParamMaps=paramGrid,
    evaluator=evaluator,
    numFolds=3
)

# 7. Entraînement
cv_model = crossval.fit(train)

# 8. Évaluation
predictions = cv_model.transform(test)
accuracy = evaluator.evaluate(predictions)
print(f"Accuracy: {accuracy:.2%}")

# 9. Feature Importance
best_model = cv_model.bestModel.stages[-1]
importances = best_model.featureImportances
print(f"Feature Importances: {importances}")

# 10. Sauvegarder le modèle
cv_model.write().overwrite().save("/models/sales_predictor")
```

### Exercice 5: Delta Lake (60 min)

**Objectif**: Utiliser Delta Lake pour le versioning et ACID

```python
from delta import *
from pyspark.sql.functions import *

# 1. Configuration Delta
spark = SparkSession.builder \
    .appName("Exercice5_Delta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# 2. Créer une table Delta
# TODO: Écrire en format Delta
df = spark.read.json("/data/events.json")
df.write.format("delta").mode("overwrite").save("/data/delta/events")

# 3. Lire Delta Table
delta_table = DeltaTable.forPath(spark, "/data/delta/events")

# 4. Updates et Deletes
# TODO: Update conditionnel
delta_table.update(
    condition = "amount < 0",
    set = {"status": "'invalid'"}
)

# TODO: Delete
delta_table.delete("timestamp < '2024-01-01'")

# 5. Merge (Upsert)
new_data = spark.read.json("/data/new_events.json")

delta_table.alias("old").merge(
    new_data.alias("new"),
    "old.event_id = new.event_id"
).whenMatchedUpdate(set={
    "amount": "new.amount",
    "timestamp": "new.timestamp"
}).whenNotMatchedInsert(values={
    "event_id": "new.event_id",
    "amount": "new.amount",
    "timestamp": "new.timestamp"
}).execute()

# 6. Time Travel
# TODO: Voir l'historique
history = delta_table.history()
history.show()

# TODO: Lire une version antérieure
df_v0 = spark.read.format("delta").option("versionAsOf", 0).load("/data/delta/events")
df_yesterday = spark.read.format("delta").option("timestampAsOf", "2024-01-01").load("/data/delta/events")

# 7. Optimisation
# TODO: Compaction
delta_table.optimize().executeCompaction()

# TODO: Z-Order
delta_table.optimize().executeZOrderBy("user_id", "timestamp")

# 8. Schema Evolution
# TODO: Ajouter une colonne
df_with_new_col = df.withColumn("processed", lit(False))
df_with_new_col.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/data/delta/events")
```

### Exercice 6: Projet Complet - Pipeline ETL Temps Réel (2h)

**Objectif**: Créer un pipeline complet de bout en bout

```python
"""
Projet: Pipeline de détection de fraude en temps réel
- Source: Stream Kafka de transactions
- Processing: Spark Structured Streaming
- ML: Modèle de détection de fraude
- Sink: Delta Lake + Alertes
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml import PipelineModel
from delta import *
import json

# 1. Setup complet
spark = SparkSession.builder \
    .appName("FraudDetectionPipeline") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

# 2. Charger le modèle ML pré-entraîné
fraud_model = PipelineModel.load("/models/fraud_detector")

# 3. Lire depuis Kafka (ou fichiers pour la démo)
transaction_stream = spark.readStream \
    .format("json") \
    .option("maxFilesPerTrigger", 1) \
    .load("/data/streaming/transactions/*.json")

# 4. Enrichissement des données
enriched_stream = transaction_stream \
    .withColumn("hour", hour("timestamp")) \
    .withColumn("day_of_week", dayofweek("timestamp")) \
    .withColumn("amount_category", 
        when(col("amount") < 100, "small")
        .when(col("amount") < 1000, "medium")
        .otherwise("large")
    )

# 5. Détection de fraude avec ML
predictions = fraud_model.transform(enriched_stream)

fraud_stream = predictions \
    .withColumn("is_fraud", col("prediction") == 1) \
    .withColumn("fraud_probability", col("probability")[1])

# 6. Alertes pour fraudes hautement probables
high_risk_fraud = fraud_stream \
    .filter(col("fraud_probability") > 0.8)

# 7. Fonction pour envoyer des alertes
def send_fraud_alert(batch_df, batch_id):
    if batch_df.count() > 0:
        alerts = batch_df.select(
            "transaction_id", 
            "amount", 
            "fraud_probability"
        ).collect()
        
        for alert in alerts:
            print(f"🚨 ALERTE FRAUDE - Transaction: {alert['transaction_id']}, "
                  f"Montant: ${alert['amount']}, "
                  f"Probabilité: {alert['fraud_probability']:.1%}")
        
        # Sauvegarder dans Delta pour audit
        batch_df.write \
            .format("delta") \
            .mode("append") \
            .save("/data/delta/fraud_alerts")

# 8. Streaming Query avec multiple sinks
# Sink 1: Alertes haute priorité
alert_query = high_risk_fraud.writeStream \
    .foreachBatch(send_fraud_alert) \
    .trigger(processingTime='10 seconds') \
    .start()

# Sink 2: Toutes les transactions vers Delta Lake
delta_query = fraud_stream.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoint/transactions") \
    .trigger(processingTime='30 seconds') \
    .start("/data/delta/transactions")

# Sink 3: Métriques agrégées
metrics_stream = fraud_stream \
    .withWatermark("timestamp", "5 minutes") \
    .groupBy(
        window(col("timestamp"), "5 minutes"),
        col("is_fraud")
    ) \
    .agg(
        count("*").alias("transaction_count"),
        sum("amount").alias("total_amount"),
        avg("fraud_probability").alias("avg_fraud_score")
    )

metrics_query = metrics_stream.writeStream \
    .format("console") \
    .outputMode("append") \
    .trigger(processingTime='30 seconds') \
    .start()

# 9. Monitoring
print("Pipeline démarré. Monitoring:")
print("- Transactions: /data/delta/transactions")
print("- Alertes: /data/delta/fraud_alerts")
print("- Checkpoint: /tmp/checkpoint/transactions")

# Attendre 5 minutes
spark.streams.awaitAnyTermination(300)

# 10. Analyse post-traitement
print("\n📊 Statistiques finales:")
spark.read.format("delta").load("/data/delta/transactions") \
    .groupBy("is_fraud") \
    .agg(
        count("*").alias("count"),
        avg("amount").alias("avg_amount")
    ).show()
```

---

## 🎓 Best Practices

### 1. **Partitionnement**
```python
# Bon: Partitionner par colonnes fréquemment filtrées
df.write.partitionBy("year", "month").parquet("/data/output")

# Repartitionner pour optimiser les joins
df.repartition(200, "join_key")
```

### 2. **Caching Stratégique**
```python
# Cacher les DataFrames réutilisés
df_filtered = df.filter(expensive_condition).cache()
# Utiliser df_filtered plusieurs fois
# ...
df_filtered.unpersist()  # Libérer la mémoire
```

### 3. **Broadcast Joins**
```python
# Pour tables < 10MB
small_df = spark.read.csv("small_table.csv")
result = large_df.join(broadcast(small_df), "key")
```

### 4. **Éviter les Collects**
```python
# Mauvais
all_data = df.collect()  # Ramène tout en mémoire driver

# Bon
df.write.parquet("/output")  # Écrire directement
sample = df.limit(1000).collect()  # Limiter
```

### 5. **Configuration Optimale**
```python
spark = SparkSession.builder \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.adaptive.skewJoin.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .getOrCreate()
```

---

## 📊 Monitoring et Debugging

### Spark UI
- **Jobs**: Vue d'ensemble des jobs
- **Stages**: Détails des stages
- **Storage**: DataFrames cachés
- **Environment**: Configuration
- **Executors**: Métriques des executors
- **SQL**: Plans d'exécution SQL

### Métriques Clés
```python
# Temps d'exécution
df.explain(True)  # Plan d'exécution

# Statistiques
df.describe().show()
df.summary().show()

# Partitions
print(f"Partitions: {df.rdd.getNumPartitions()}")

# Taille estimée
df.cache()
spark.catalog.cacheTable("table_name")
```

---

## 🚀 Déploiement en Production

### Spark Submit
```bash
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --driver-memory 4g \
  --executor-memory 8g \
  --executor-cores 4 \
  --num-executors 10 \
  --conf spark.sql.shuffle.partitions=200 \
  --conf spark.dynamicAllocation.enabled=true \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  --py-files dependencies.zip \
  main.py
```

### Configuration YARN
```bash
# Resources
--conf spark.yarn.executor.memoryOverhead=2g
--conf spark.yarn.driver.memoryOverhead=1g

# Dynamic Allocation
--conf spark.dynamicAllocation.enabled=true
--conf spark.dynamicAllocation.minExecutors=2
--conf spark.dynamicAllocation.maxExecutors=20
```

---

## 🔧 Troubleshooting

### OutOfMemoryError
```python
# Solutions:
# 1. Augmenter la mémoire
spark.conf.set("spark.executor.memory", "8g")

# 2. Augmenter les partitions
df.repartition(1000)

# 3. Utiliser persist avec DISK_ONLY
df.persist(StorageLevel.DISK_ONLY)
```

### Slow Joins
```python
# 1. Broadcast small tables
broadcast(small_df)

# 2. Salt keys pour éviter skew
df.withColumn("salted_key", concat(col("key"), lit("_"), (rand() * 10).cast("int")))

# 3. Utiliser bucketing
df.write.bucketBy(10, "key").sortBy("key").saveAsTable("bucketed_table")
```

### Data Skew
```python
# Identifier le skew
df.groupBy("key").count().describe().show()

# Résoudre avec salting
salt_factor = 10
df_salted = df.withColumn("salt", (rand() * salt_factor).cast("int"))
df_salted = df_salted.withColumn("salted_key", concat(col("key"), lit("_"), col("salt")))
```

---

## 📚 Ressources

- [Documentation Spark](https://spark.apache.org/docs/latest/)
- [PySpark API](https://spark.apache.org/docs/latest/api/python/)
- [Spark by Examples](https://sparkbyexamples.com/)
- [Delta Lake](https://delta.io/)
- [Databricks Learning](https://www.databricks.com/learn)

---

## 🎯 Projet Final Spark

**Créer une Plateforme d'Analyse Temps Réel**

1. **Ingestion**: Streaming depuis Kafka/Files
2. **Processing**: Transformations complexes
3. **ML**: Modèle de prédiction/classification
4. **Storage**: Delta Lake avec partitioning
5. **Serving**: API pour requêtes temps réel
6. **Monitoring**: Métriques et alertes

**Livrables**:
- Code PySpark optimisé
- Pipeline Streaming
- Modèle ML entraîné
- Documentation architecture
- Tests de performance

---

✨ **Félicitations!** Vous maîtrisez maintenant Apache Spark pour le traitement de données massives!