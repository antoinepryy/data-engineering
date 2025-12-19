# Modeles Vosk pour STT

Les modeles Vosk sont volumineux et ne sont pas inclus dans le repo Git.
Suivez ces instructions pour les telecharger et les configurer.

## Modeles disponibles

| Modele | Langue | Taille | Description |
|--------|--------|--------|-------------|
| `vosk-model-small-fr-0.22` | Francais | 41 MB | Modele leger, rapide |
| `vosk-model-small-en-us-0.15` | Anglais | 40 MB | Modele leger, rapide |
| `vosk-model-fr-0.22` | Francais | 1.4 GB | Modele large, haute precision |

## Telechargement

### Option 1: Dans le conteneur Docker (recommande)

```bash
# Creer le repertoire des modeles
docker exec vocal-python mkdir -p /app/models

# Telecharger le modele francais (small) - 41 MB
docker exec vocal-python bash -c "
  cd /app/models && \
  wget -q https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip && \
  unzip -q vosk-model-small-fr-0.22.zip && \
  rm vosk-model-small-fr-0.22.zip
"

# Telecharger le modele anglais (small) - 40 MB
docker exec vocal-python bash -c "
  cd /app/models && \
  wget -q https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip && \
  unzip -q vosk-model-small-en-us-0.15.zip && \
  rm vosk-model-small-en-us-0.15.zip
"

# (Optionnel) Telecharger le modele francais large - 1.4 GB
docker exec vocal-python bash -c "
  cd /app/models && \
  wget -q https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip && \
  unzip -q vosk-model-fr-0.22.zip && \
  rm vosk-model-fr-0.22.zip
"
```

### Option 2: Telechargement local puis copie

```bash
# Telecharger localement
cd /tmp
wget https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
unzip vosk-model-small-fr-0.22.zip

# Copier dans le conteneur
docker cp vosk-model-small-fr-0.22 vocal-python:/app/models/
```

## Verification

Verifiez que les modeles sont bien installes:

```bash
docker exec vocal-python ls -la /app/models/
```

Verifiez que Vosk est disponible via l'API:

```bash
curl http://localhost:8000/api/engines
```

Reponse attendue:
```json
{
  "vosk": {
    "available": true,
    "languages": ["fr", "en"]
  },
  ...
}
```

## URLs de telechargement direct

- Francais (small): https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip
- Anglais (small): https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
- Francais (large): https://alphacephei.com/vosk/models/vosk-model-fr-0.22.zip

## Autres modeles

Tous les modeles Vosk sont disponibles sur:
https://alphacephei.com/vosk/models

Modeles recommandes pour d'autres langues:
- Allemand: `vosk-model-small-de-0.15` (45 MB)
- Espagnol: `vosk-model-small-es-0.42` (39 MB)
- Italien: `vosk-model-small-it-0.22` (48 MB)
