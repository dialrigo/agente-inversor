# Funciones, entregables y checklists

Cada integrante tiene **una función de producción**: construye una parte de la entrega y la sube con commits propios en una rama propia. También tiene **una función de verificación**: revisa el trabajo de otra persona con un checklist. La verificación es el *review* del Pull Request: nada entra a `main` sin la aprobación de quien verifica.

## Mapa de la entrega

| Integrante | Función de producción | Archivos que entrega (commits propios) | Rúbrica | Verifica a |
|---|---|---|---|---|
| **Diego Ríos** `dialrigo` | Integración, corrida oficial, presentación y entrega en Moodle | `notebooks/Agente_Inversor.ipynb`, `results/`, presentación | Todas | Todos (checklist final) |
| **Andrés Díaz** `andresdila` | Datos, EDA y formulación del problema | `docs/informe/02_datos_eda.md`, `03_formulacion.md` | 1 | Nicolás |
| **Nicolás Gamboa** `JnicolasGh` | Entorno y pruebas automáticas | `tests/test_investor_env.py`, `docs/informe/04_entorno.md` | 2 | janayajoo |
| **janayajoo** | Diseño e iteración de la recompensa | `configs/investor_dqn_log.yaml`, `docs/informe/05_recompensa.md` | 3 | Lorena |
| **Lorena Valero** `LorenaValero20` | Evaluación held-out, baselines y anomalía | `tests/test_metrics.py`, `docs/informe/07_evaluacion.md`, `08_anomalia.md` | 4 | Marlon |
| **Marlon Umbarila** `Marlon-Umbarila` | Algoritmo, Optuna, semillas y reproducibilidad | `docs/experimentos/optuna_y_semillas.md`, `docs/informe/06_algoritmo.md`, `10_reproducibilidad.md` | 2, 4, 5 | Nataly |
| **Nataly Valbuena** `natavalbuenal` | Discusión, referencias y consolidación del informe | `docs/informe/01_introduccion.md`, `09_discusion.md`, `11_referencias.md`, informe final (Word/PDF) | 5 | Andrés |
| **Los 7** | Reflexión individual | `docs/reflexiones/<usuario>.md` | 5 | Nataly (forma) |

El anillo de verificación es Andrés → Nicolás → janayajoo → Lorena → Marlon → Nataly → Andrés. Así cada etapa la revisa quien depende de ella o quien la usa después. Diego cierra con el checklist final.

**Regla del notebook:** solo Diego hace commits sobre `Agente_Inversor.ipynb`. Si siete personas editan el mismo `.ipynb`, los conflictos de Git son casi seguros. Por eso cada quien escribe su texto en su archivo de `docs/informe/`, y Diego lo copia al notebook en la integración.

---

## Diego · Integración, corrida oficial y entrega

**Produce**
- [ ] Corrida oficial (`RETRAIN = True`, Run All) y commit de `results/` y del notebook ejecutado
- [ ] Integración de los textos de `docs/informe/` en las celdas de interpretación del notebook
- [ ] Revisión y *merge* de cada PR solo cuando su verificador lo aprobó
- [ ] Presentación de 8 a 10 diapositivas para el panel o foro (pregunta, diseño, resultado, lecciones)
- [ ] Entrega en Moodle: informe PDF, ZIP del código (sin `.venv`, `saves`, `mlruns`, `mlflow.db`) y link del repo

**Checklist final de la entrega (antes de subir a Moodle)**
- [ ] Los 7 PR de reflexión y los 6 PR de función están en `main`
- [ ] El CI está en verde (lint, build y tests)
- [ ] Las cifras del informe coinciden con `results/metricas_heldout.csv`
- [ ] El held-out se abrió una sola vez; si hubo una nueva corrida, el motivo está en `docs/decisiones.md`
- [ ] Rúbrica: cada uno de los 5 criterios tiene su sección completa en el informe

## Andrés · Datos, EDA y formulación

**Produce**
- [ ] `02_datos_eda.md`: descripción del dataset, división temporal y lectura de las figuras 01–04 (tendencia, colas pesadas, regímenes de volatilidad, correlaciones)
- [ ] `03_formulacion.md`: tabla del estado con justificación de cada indicador y respuestas a las preguntas 8 a 15 del enunciado
- [ ] Conexión explícita EDA → estado (ej.: la volatilidad se agrupa, por eso `vol_20`)

**Verifica a Nicolás (entorno), en el PR de Nicolás**
- [ ] El entorno observa exactamente lo que dice la formulación (7 indicadores + posición, en el mismo orden que `investor_data.FEATURES`)
- [ ] Las acciones del entorno son {0, 0,5, 1,0} como en la formulación
- [ ] Los tests cubren el anti-lookahead que se describe en `03_formulacion.md`
- [ ] `04_entorno.md` es coherente con `03_formulacion.md` (mismos nombres y supuestos)

## Nicolás · Entorno y pruebas automáticas

**Produce**
- [ ] `tests/test_investor_env.py` con pytest; mínimo 5 pruebas: (1) lookahead de indicadores, (2) costo de \$100 al entrar al 100 %, (3) efectivo estable, (4) cálculo manual de un paso (100.000 → 99.900 → ×1,01), (5) el held-out no está registrado en Gymnasium
- [ ] `uv add --dev pytest` y el paso `uv run pytest` en `.github/workflows/ci.yml`, para que el CI corra los tests en cada push
- [ ] `04_entorno.md`: cronología de un paso, fórmula del valor, costo, desplazamiento del 50 %, supuestos (ejecución al cierre, sin intereses) y resultados de las pruebas

**Verifica a janayajoo (recompensa), en el PR de janayajoo**
- [ ] Las fórmulas de `05_recompensa.md` coinciden línea por línea con `InvestorEnv.step`
- [ ] El config nuevo (`investor_dqn_log.yaml`) solo cambia la recompensa: mismos hiperparámetros y semilla
- [ ] Su evaluación usa validación (`"val"`), nunca `"test"`

## janayajoo · Diseño e iteración de la recompensa

**Produce**
- [ ] `configs/investor_dqn_log.yaml`: tercera variante (retorno log sin penalización), copia del config v2 con `env: Investor-log-v0` y `eval_env: Investor-log-val-v0`. Aísla el efecto del log frente al de la penalización
- [ ] Entrenar las 3 variantes y comparar en **validación**: retorno, máximo drawdown, costos, cambios de posición y uso de cada acción
- [ ] `05_recompensa.md`: el ciclo completo (v1 → comportamiento → problema → v2 → comparación), la tabla de las 3 variantes, *reward hacking* de cada una y la justificación de la versión elegida

**Verifica a Lorena (evaluación), en el PR de Lorena**
- [ ] La versión evaluada en held-out es la que eligió la celda de selección en validación
- [ ] Las interpretaciones de `07_evaluacion.md` mencionan el comportamiento que induce la recompensa elegida
- [ ] `tests/test_metrics.py` pasa y sus cálculos manuales son correctos

## Lorena · Evaluación held-out, baselines y anomalía

**Produce**
- [ ] `tests/test_metrics.py`: probar `investor_eval.metrics` con una serie pequeña hecha a mano (ej.: valores 100 → 120 → 90 → 110: retorno +10 %, drawdown 25 %)
- [ ] `07_evaluacion.md`: tabla final de las 4 estrategias, lectura de la curva de capital, del drawdown y de las posiciones, y respuesta explícita y honesta a la pregunta central
- [ ] `08_anomalia.md`: análisis del tramo de peor desempeño (sección 9 del notebook) y al menos una hipótesis de por qué ocurrió
- [ ] Verificación manual: comprar y mantener ≈ retorno del activo − 0,1 %

**Verifica a Marlon (algoritmo y reproducibilidad), en el PR de Marlon**
- [ ] Optuna calificó los trials en validación (`eval_env` del config), no en test
- [ ] Si los mejores hiperparámetros de Optuna se adoptaron, se hizo **antes** de la corrida oficial y quedó en `docs/decisiones.md`
- [ ] La tabla de semillas muestra la variabilidad y está interpretada

## Marlon · Algoritmo, Optuna, semillas y reproducibilidad

**Produce**
- [ ] Clonar desde cero en su máquina y seguir **solo** el README y `CONFIGURACION_KERNEL.md`; corregir en su PR cualquier paso que falle o confunda
- [ ] Correr `uv run rlgames-sb tune --config configs/investor_dqn_log_dd.yaml` y el bloque `RUN_SEEDS = True` del notebook
- [ ] `docs/experimentos/optuna_y_semillas.md`: mejores hiperparámetros, captura de MLflow y tabla de métricas en validación con 3 semillas
- [ ] `06_algoritmo.md`: DQN, arquitectura y tabla de hiperparámetros (learning rate, batch, γ, pasos, buffer, ε inicial y final, parada, semillas)
- [ ] `10_reproducibilidad.md`: comandos, versiones (Python, torch, SB3), tiempo de ejecución y si los números coinciden con los oficiales

**Verifica a Nataly (discusión e informe), en el PR de Nataly**
- [ ] Cada cifra del informe coincide con `results/metricas_heldout.csv` o con la corrida de validación
- [ ] Las limitaciones mencionadas son coherentes con lo que vio al reproducir
- [ ] El informe final tiene todas las secciones de `docs/informe/`

## Nataly · Discusión, referencias y consolidación del informe

**Produce**
- [ ] `01_introduccion.md`: contexto, pregunta central y resumen del resultado
- [ ] `09_discusion.md`: *reward hacking*, no-estacionariedad, datos escasos, supuestos del simulador y sesgo de supervivencia, conectados con **nuestros** resultados
- [ ] `11_referencias.md` en APA 7
- [ ] Informe final en Word/PDF: une las secciones 01 a 11 y las 7 reflexiones, con figuras de `results/` numeradas y citadas

**Verifica a Andrés (formulación), en el PR de Andrés**
- [ ] Las preguntas 8 a 15 están respondidas, una por una
- [ ] Cada indicador tiene una justificación que no sea genérica
- [ ] El texto se entiende sin haber visto el código

**Verifica las 7 reflexiones (forma)**
- [ ] Cada una responde las 5 preguntas, con voz propia y con referencia a algo concreto del proyecto

## Los 7 · Reflexión individual

- [ ] Crear la rama `reflexion/<usuario>` y editar `docs/reflexiones/<usuario>.md`
- [ ] Responder las 5 preguntas del enunciado (3 a 6 líneas cada una), en primera persona
- [ ] Abrir el PR y asignar a Nataly como revisora
