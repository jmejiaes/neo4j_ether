# Changelog — paper enhancement

Resumen técnico de la ampliación del paper *"Blockchain Trajectories in Graph
Databases: A Neo4j-Based Model for Ethereum Transaction Analytics"*: qué cambió,
por qué, y cómo revertir cada extensión. Las decisiones formales están en
`docs/adr/` (citadas como ADR-000X).

---

## 1. Resumen

El objetivo era doble: (a) ordenar el repositorio y (b) ampliar la sección
experimental, que en el paper original se quedaba en **100 bloques**.

- El cuello de botella real no era el modelo ni Neo4j (las 14 consultas corrían en
  <1 s), sino la **adquisición de datos**: Etherscan tardaba ~4 min/bloque. Se
  reemplazó por **BigQuery**, lo que bajó el costo ~3000× y permitió escalar.
- Se escaló de **100 → hasta 10.000 bloques** y se replicó el análisis en **4 eras**
  de la historia de Ethereum (2016, 2020, 2023, 2024).
- El pipeline nuevo **reproduce los resultados publicados** del paper original
  (Apéndice A): las conclusiones previas se confirman y se extienden.
- Se agregó una **discusión crítica** (fortalezas/limitaciones del modelo) basada en
  los datos nuevos.

---

## 2. Qué se hizo, por área

### 2.1 Repositorio (ADR-0004)
- **Antes:** dos repos git enredados (uno anidado en `src/`), notebooks duplicados,
  PDFs, `.env` con **secretos reales** versionados, `.DS_Store`, resultados sueltos.
- **Ahora:** un solo repo (`neo4j_ether`), paquete `src/ether/`, scripts en
  `scripts/`, documentación en `docs/`, datos en `data/` (ignorado por git), material
  viejo archivado en `_legacy/` (ignorado, no borrado). `.env` fuera de git +
  `.env.example`.

### 2.2 Fuente de datos: Etherscan → BigQuery (ADR-0001, ADR-0007)
- **Antes:** Etherscan, una llamada por cada dirección de cada transacción
  (~4 min/bloque). A ese ritmo, 1.000 bloques = ~66 h.
- **Ahora:** dataset público `bigquery-public-data.crypto_ethereum` (bloques,
  transacciones, `traces` = transacciones internas, `contracts`). Una ventana
  completa se baja en segundos.
- **Optimización clave (ADR-0007):** las tablas están particionadas por *fecha*, no
  por número de bloque; filtrar solo por bloque escaneaba la tabla entera (una
  consulta de `traces` a 100 bloques escaneaba **2,9 TB**). Filtrando también por
  `block_timestamp` se pasó a **~1,5 GB** por ventana (~3000× menos).

### 2.3 Modelo (ADR-0002, ADR-0006)
- **`balance` eliminado** del nodo cuenta, y el *block reward* del nodo bloque:
  **ninguna de las 14 consultas los usa**, y el `balance` obtenido era el *actual*
  (no el del bloque analizado), incorrecto para un análisis histórico. El modelo
  queda `(address, isContract)` y bloque `(number, time)`, consistente con §3.1.
- **Etiqueta unificada a `ExternalTransaction`** (el código usaba `:Transaction`,
  el Cypher impreso en el paper usaba `:ExternalTransaction`): ahora las consultas
  publicadas corren tal cual.

### 2.4 Infraestructura Neo4j (ADR-0005)
- **Neo4j Community 2026.01.3 local (Docker)** en vez de Aura: Aura Free tope ~200k
  nodos; una sola ventana de 1.000 bloques ya lo supera. Local corrió ~2,9M nodos.
- **Escritura por lotes con `UNWIND`** + índices/constraints creados antes de cargar:
  millones de escrituras individuales serían inviables.

### 2.5 Experimentación (ADR-0003)
- **Escala:** ladder acumulativo **{2, 10, 50, 100, 1.000, 10.000}** bloques (antes
  solo hasta 100). Los primeros cuatro mantienen continuidad con el paper.
- **Multi-era:** el mismo ladder en 4 eras — 2016 (pre-DeFi), 2020 (DeFi Summer),
  2023 (post-Merge), 2024 (post-Dencun, la ventana original).
- **Diseño removible:** las eras son entradas de configuración en
  `src/ether/experiments/eras.py`; la 2024 es la canónica. Quitar una era = borrar
  su entrada (ver sección 5).

### 2.6 Reporte / análisis
- Reporte reorganizado por `(era × cantidad de bloques)`: comparación *dentro de la
  era* (a lo largo del ladder) y *entre eras* (a cantidad fija de bloques).
- Salidas en `data/` (regenerables): gráficos PNG, tablas CSV y MD por corrida.

### 2.7 Documento del paper
- Manuscrito único (`docs/paper/paper_v2.md` + `.docx`) que fusiona el original
  (Intro, Related Work, Modelo) con: abstract revisado, metodología nueva (§4),
  resultados de escala (§4.3) y entre-eras (§4.4), **discusión crítica (§5,
  pros/cons)** y conclusiones (§6). Se presenta de forma autónoma, sin lenguaje de
  revisión.
- Incluye **5 figuras con caption** embebidas y **6 tablas de resultados reales**
  (Apéndice A) generadas desde los CSV (`scripts/gen_appendix_tables.py`).

---

## 3. Qué se agregó que antes no existía

1. Sección experimental a escala (hasta 10.000 bloques) — responde a la limitación
   declarada del paper ("100 bloques es poco").
2. **Análisis entre eras** (nuevo eje): evolución estructural de la red.
3. **Discusión crítica del modelo** (§5): capacidades, fortalezas, limitaciones, y
   un veredicto explícito de si cada eje nuevo aporta valor.
4. Detección de contrato *point-in-time* (más correcta que `eth_getCode` actual).
5. Nota de escalabilidad de consultas (§4.6) — hallazgo genuino (ver sección 4).
6. **6 tablas de resultados reales** (Apéndice A) en vez de solo mencionarlas.

---

## 4. Hallazgos clave (resultados)

**Dentro de la era 2024 (al escalar):**
- WETH es el nodo más central en participación **a toda escala**, y su cuota se
  mantiene **estable en ~6% de las participaciones** de 2 a 10.000 bloques (algo
  mayor solo en la ventana más pequeña). La concentración es **estable en cuatro
  órdenes de magnitud**, no se agudiza.
- Los patrones (rankings, intermediarios dominantes) se **estabilizan** por
  ~100–1.000 bloques; escalar a 10k confirma y afina *magnitudes* (p. ej. máximos de
  valor), no reordena la estructura.

**Entre eras (ventanas de 10.000 bloques):**

| Era | tx externas | tx internas | tx/bloque | interna/externa | WETH |
|-----|------------:|------------:|----------:|----------------:|:-----|
| 2016 |    80.796 |  16.133 |   8,1 | 0,20 | ausente |
| 2020 | 1.878.933 | 385.042 | 187,9 | 0,20 | #2 (Uniswap router #1) |
| 2023 | 1.301.965 | 739.050 | 130,2 | 0,57 | #2 |
| 2024 | 1.530.170 | 849.527 | 153,0 | 0,56 | #1 |

- **Densificación:** ~8 → ~188 tx/bloque (≈20×).
- **Complejidad de contratos:** ratio interna/externa 0,20 → 0,57 tras el Merge.
- **Emergencia de WETH:** ausente en 2016 → #2 en 2020/2023 → #1 en 2024.

**Hallazgos técnicos (§4.6, §5.3):**
- La consulta de participación total (4.2.3) era **cuadrática** en cuentas hub
  (WETH ~287k aristas): no terminaba a 10.000 bloques (78 min). Reformulada a una
  sola pasada da resultados idénticos en **2 s**. Es la única consulta que necesitó
  reescritura.
- Borrar el grafo de 2,9M nodos en una sola transacción **agotaba la memoria**; se
  resolvió con borrado por lotes.

### 4.1 Corrección del denominador de participación (ADR-0008)

Al validar las consultas contra los CSV de las corridas se detectó, y se verificó
numéricamente, que la Query 4.2.3 usaba un **denominador incorrecto**
(`COUNT(todos los nodos)` en vez de participaciones). Al escalar, eso fabricaba una
tendencia falsa (la participación de WETH parecía "crecer" 6,99% → 9,83% solo porque
los usuarios por transacción caen al agrandar la ventana). Con el denominador
correcto (participaciones = aristas `SENT_BY`+`RECEIVED_BY`), la participación es
**plana (~6%)** — el hallazgo corregido reportado arriba.

- **Se corrigió:** la query, la Tabla A.2, las Figuras 5 y 7, y la prosa del Abstract,
  §4.3, §5.2, §5.4 y §6.
- **No afecta:** rankings (WETH #1, top-3 estable), conteos crudos, densificación,
  ratio interna/externa, ni la emergencia de WETH entre eras.

### 4.2 Auditoría de correctitud y consistencia

Se auditaron el código y los resultados; todos los números publicados quedaron
verificados y no se halló ningún fallo que invalide resultados. Ajustes aplicados:
- **Limitación n=1** (§5.3): se reconoce explícitamente que cada era es **una sola
  ventana de ~2 días**, así que las diferencias entre eras son indicativas, no
  medias estadísticas.
- **Clasificación de contratos** (§5.3 + `bigquery.py`): incluye contratos creados
  en-ventana; se documenta que precompiles/alias L2 se cuentan como EOA, por lo que
  el % de contratos (5–7%) es una cota inferior leve.
- **Consistencia de queries de pares** (`analytics_queries.py`): 5_3/5_4/5_5 se
  restringen a transacciones externas, igual que 5_1/6.
- **Ratio interna/externa**: reformulado como transferencias internas con valor
  (cota inferior conservadora).

---

## 5. Reversibilidad (cómo quitar cada extensión)

Todo está diseñado para ser reversible. Por cada extensión:

| Extensión | Cómo quitarla | Impacto |
|-----------|---------------|---------|
| **Multi-era (dejar solo 2024)** | Borrar/comentar las 3 eras extra en `eras.py`; borrar `data/results/<era>` y `data/output/cross_era_*`. En el paper: quitar §4.4 y las partes entre-eras de §5. | Bajo. Diseñado removible (ADR-0003). La era 2024 y el análisis dentro-de-era quedan intactos: vuelve a ser esencialmente el paper original a mayor escala. |
| **Menos escala (p. ej. tope 1.000)** | Cambiar `LADDER` en `eras.py`. | Trivial. Se pierde la curva de escalabilidad y el hallazgo de la consulta 4.2.3. |
| **Volver a Etherscan** | El código legacy sigue en `ingestion/etherscan.py`. | No recomendado: reintroduce el cuello de botella de 4 min/bloque; inviable a gran escala. |
| **Reintroducir `balance`** | Enriquecer con una pasada extra (Etherscan o estado por bloque). | Cuesta trabajo y ninguna consulta lo usa. |
| **Quitar la Discusión §5 (pros/cons)** | Borrar la sección. | Es interpretación/argumentación; conviene revisarla y ajustarla antes de decidir. |
| **Quitar figuras** | Quitar los `![...]` en el `.md` y re-renderizar. | Cosmético. |
| **Menos/más tablas del Apéndice A** | Editar `scripts/gen_appendix_tables.py` y re-generar. | Trivial. |

Si se prefiere quedarse solo con la era 2024, quitar el resto es borrar unas entradas
de configuración y un directorio — no rompe nada. Fue una restricción de diseño desde
el principio.

---

## 6. Justificación resumida

- **BigQuery en vez de Etherscan:** único camino viable para ≥1.000 bloques y varias
  eras; además reproduce los números publicados. (ADR-0001, ADR-0007)
- **Eliminar `balance`/reward:** no los usa ninguna consulta y el `balance` era
  semánticamente incorrecto para análisis histórico. (ADR-0002)
- **Multi-era removible:** aporta el hallazgo más valioso (evolución de la red) sin
  atar el paper a él. (ADR-0003)
- **Neo4j local + escritura por lotes:** Aura no aguanta la escala; los lotes hacen
  viable cargar millones de elementos. (ADR-0005)
- **Etiqueta `ExternalTransaction`:** hace que el Cypher del paper corra literal.
  (ADR-0006)
- **Partition pruning:** sin esto una consulta agota la cuota gratuita; con esto todo
  el experimento cabe en la capa gratis. (ADR-0007)
- **Denominador de participación corregido:** un porcentaje necesita un denominador
  dimensionalmente coherente; a escala, el error latente se volvía titular. (ADR-0008)

---

## 7. Estado

- **Completo:** refactor, pipeline BigQuery, 4 eras × ladder a 10k, análisis
  dentro/entre eras, gráficos, ADRs, y el manuscrito (`paper_v2`, MD + DOCX con
  figuras y discusión).
- **Posibles siguientes pasos (abiertos):**
  - Mantener las 4 eras o quedarse solo con 2024 (ver sección 5).
  - Empujar la escala a 100.000 bloques (test de escalabilidad mayor).
  - Incrustar las Figuras 1–3 conceptuales (hoy solo en el `.docx` original).
