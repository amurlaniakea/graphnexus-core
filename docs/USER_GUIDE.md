# GraphNexus User Guide

## Interpretación Visual del Dashboard 3D

### Colores de Nodos (Roles Estructurales — 4 tipos fijos)
El sistema clasifica automáticamente cada nodo según su comportamiento matemático en la red, basándose en Betweenness, Closeness y Degree Centrality.

- **Rojo (#ff2a6a) — Global Broker (Intermediario Global):** Alta intermediación (Betweenness > 0.05) pero bajo grado de conexión (≤ 3). Actúa como puente entre comunidades. Si cae, la red se fragmenta.
- **Cyan (#00ffc8) — Local Hub (Núcleo Local):** Alto grado (> 5) pero baja intermediación. Dominante dentro de su comunidad, sin influencia global.
- **Amarillo (#ffe600) — Super-Spreader (Superpropagador):** Alta cercanía (Closeness > 0.3). Puede alcanzar al resto de la red rápidamente. Ideal para propagar información.
- **Púrpura (#6a3cff) — Peripheral (Periférico):** Métricas bajas. Nodo de borde con poca influencia estructural.

Nota: Si la red es muy densa (como el dataset de trabajos de IA con `business-rule-col`), puede que no existan Brokers (todos los nodos tienen grado alto). Esto es matemáticamente correcto, no un error.

### Tamaños de Nodos
Escalados por Degree Centrality (número de conexiones directas). Nodos más grandes = más conectados.

### Resaltados Especiales
- **Blanco brillante:** Nodos en la ruta crítica (pathfinding).
- **Tamaño aumentado (15 vs 5):** Nodos en la ruta crítica.
- **Aristas amarillas (#ffff00):** Conexiones de la ruta crítica.
- **Aristas más gruesas (3.5 vs 1.5):** Conexiones de la ruta crítica.

## Métricas de Centralidad (Panel de Análisis — al hacer clic en nodo)

### Betweenness Centrality
- Qué mide: Cuántas veces un nodo actúa como puente en las rutas más cortas entre todos los pares.
- Interpretación: Valores altos = cuello de botella crítico. Si este nodo se elimina, la red se divide.
- Rango: 0.0 a 1.0 (normalizado, con muestreo `k=min(500, len(G))` para rendimiento).

### Closeness Centrality
- Qué mide: Qué tan rápido puede un nodo conectarse con todos los demás (inverso de la suma de distancias).
- Interpretación: Valores altos = super-contagiador. Ideal para sembrar información rápidamente.
- Rango: 0.0 a 1.0.

### Degree Centrality
- Qué mide: Número de conexiones directas (normalizado por número máximo posible).
- Interpretación: Valores altos = nodo muy conectado (hub local o central).
- Rango: 0.0 a 1.0.

## Controles del Dashboard

### Community Filter
Filtra nodos por comunidad detectada (Leiden por defecto, o Louvain). Útil para aislar ecosistemas.

### Weight Threshold (Umbral de Peso)
Filtra aristas por peso (fuerza de conexión). Subir el umbral oculta conexiones débiles, dejando solo el esqueleto estructural fuerte de la red. Útil para eliminar ruido.

### Node Search
Busca nodos por ID y centra la cámara en ellos.

### Botón "Exportar Métricas"
Descarga CSV con: `id`, `role`, `group`, `betweenness`, `closeness`, `degree`. Útil para análisis posterior en Excel, Python, R.

## Pathfinding (Rutas Críticas)

### Uso desde CLI
```bash
graphnexus --input data.csv --node-id id_col --target connection_col --pathfinding "NodoA,NodoZ"
```

### Interpretación Visual
- La ruta más corta se resalta con nodos blancos y aristas amarillas.
- Útil para rastrear flujos: dinero, malware, dependencias logísticas, cadenas de suministro.
- Si no hay ruta (`NOT FOUND`), los nodos no están conectados en el grafo.

## Modos de Construcción de Relaciones

### `--target` (Conexión Directa)
Crea aristas entre dos columnas. Requiere que los valores coincidan exactamente entre filas. Ejemplo: `--node-id person --target knows`.

### `--business-rule-col` (Agrupación y Conexión Intra-Grupo)
Agrupa filas por una columna y conecta los miembros del grupo con topología en estrella (O(N)). Ideal para redes de co-ocurrencia (ej. trabajos en la misma empresa). Ejemplo: `--node-id job --business-rule-col company`.

### `--pathfinding`
Calcula la ruta más corta entre dos nodos existentes. Requiere que los nodos existan en el grafo.

### `--time-col` (Análisis Temporal — Fase 4, backend implementado)
Permite incluir una columna de fechas. El backend la convierte a Unix timestamp (`int`). El frontend puede usar esta información para filtros temporales (futuro).

## Ejemplo Completo
```bash
graphnexus --input /tmp/zip_data/12/global_ai_jobs_2026.csv \
  --node-id Job_Title \
  --business-rule-col Company \
  --pathfinding "AI Software Engineer,NLP Engineer" \
  --theme "AI Jobs Market - Critical Path"
```
Esto genera un grafo con los títulos de trabajo como nodos, conectados por la empresa compartida, con la ruta más corta resaltada.

## Resolución de Problemas Comunes

| Síntoma | Causa | Solución |
|---|---|---|
| Todos los nodos son púrpura | No hay roles diversos (red muy densa o muy dispersa) | Normal. Revisa `Betweenness` en el panel de análisis. |
| `Critical Path: NOT FOUND` | Los nodos del `--pathfinding` no existen o no están conectados | Usa `--target` o `--business-rule-col` para crear aristas primero. |
| `Nodes: X | Edges: 0` | `--target` usa valores que no coinciden con `--node-id` | Usa `--business-rule-col` en su lugar para agrupar. |
| `Weight Threshold` no cambia nada | Todas las aristas tienen peso 0 o muy bajo | El grafo es muy disperso. Revisa con `--business-rule-col`. |
