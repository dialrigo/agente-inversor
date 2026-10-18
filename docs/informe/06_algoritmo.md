# Algoritmo y protocolo de entrenamiento

## DQN: por qué (acciones discretas) y cómo funciona en una frase por componente

Usamos **DQN** (*Deep Q-Network*, implementación de Stable-Baselines3) porque el espacio de acciones es discreto y pequeño: $A = \{0\,\%, 50\,\%, 100\,\%\}$ del capital invertido. DQN aprende una función $Q_\theta(s, a)$ que estima el retorno descontado de elegir la acción $a$ en el estado $s$ y luego seguir la política; la política final es simplemente $\pi(s) = \arg\max_a Q_\theta(s,a)$, sin necesidad de parametrizar una distribución sobre acciones como en PPO.

| Componente | Qué hace en nuestro problema |
|---|---|
| Red Q | Recibe las 8 variables del estado (7 indicadores normalizados + posición actual) y devuelve un valor Q para cada una de las 3 fracciones de inversión. |
| Objetivo de Bellman | Entrena la red para que $Q(s_t,a_t) \approx r_{t+1} + \gamma \max_{a'} Q_{\text{obj}}(s_{t+1},a')$, con pérdida Huber. |
| *Replay buffer* | Guarda las transiciones $(s_t, a_t, r_{t+1}, s_{t+1})$ y entrena con minilotes aleatorios; rompe la correlación entre días consecutivos de la serie. |
| Red objetivo | Copia congelada de la red Q que se actualiza cada 1.000 pasos; estabiliza el objetivo de Bellman. |
| Exploración ε-greedy | Con probabilidad ε el agente elige una fracción al azar; ε baja linealmente de 1,0 a 0,05 durante el primer 30 % del entrenamiento. |
| Política de evaluación | Greedy y determinista (`deterministic=True`): en validación y held-out no hay exploración, por eso basta un episodio. |

**¿Por qué no PPO?** PPO también sirve para acciones discretas y el repositorio lo soporta (`algo: ppo`), pero DQN es la recomendación del enunciado, aprovecha mejor una serie histórica corta gracias al *replay buffer* (cada transición se reutiliza muchas veces) y su política greedy es más fácil de interpretar. PPO queda como trabajo futuro, junto con las demás extensiones que se discuten en la sección de limitaciones.

## Arquitectura de la red

Perceptrón multicapa (`MlpPolicy` de SB3, `net_arch: [64, 64]`, activación ReLU):

```
estado (8) → Lineal 8×64 → ReLU → Lineal 64×64 → ReLU → Lineal 64×3 → Q(s, ·) para {0 %, 50 %, 100 %}
```

≈ 4.900 parámetros entrenables (576 + 4.160 + 195). Una red pequeña es suficiente para 8 entradas y reduce el riesgo de memorizar los ~1.600 días de entrenamiento. Se entrena en CPU: con una MLP de este tamaño la GPU no aporta velocidad.

## Tabla de hiperparámetros (lr, batch, γ, pasos, buffer, ε, parada, semillas)

Valores de `configs/investor_dqn_simple.yaml` (v1), `configs/investor_dqn_log_dd.yaml` (v2, versión final) y `configs/investor_dqn_log.yaml` (v3, control). Las tres versiones de la recompensa usan **los mismos hiperparámetros**, para que la comparación entre recompensas no se confunda con un cambio del algoritmo. Tras la búsqueda con Optuna y la prueba de semillas **se mantuvieron estos valores** (ver más abajo).

| Hiperparámetro | Valor | Justificación |
|---|---|---|
| Algoritmo | DQN (SB3) | Acciones discretas |
| Arquitectura | MLP [64, 64], ReLU | Entrada de 8 variables; red pequeña |
| Optimizador / pérdida | Adam / Huber (por defecto en SB3) | Huber es robusta a recompensas extremas (días de ±5 %) |
| Learning rate | 1 × 10⁻⁴ | Conservador; la recompensa diaria es muy ruidosa |
| Batch size | 64 | |
| Discount factor γ | 0,99 | Horizonte efectivo ≈ 100 días: el agente valora lo que pasa en los próximos meses, no solo mañana |
| Pasos totales | 150.000 | ≈ 595 episodios de 252 días |
| Longitud del episodio (train) | 252 días con inicio aleatorio | Un año bursátil; ~1.360 inicios posibles dan diversidad de situaciones |
| `learning_starts` | 2.000 | Llena el buffer antes de entrenar |
| `train_freq` | 4 | Una actualización de la red cada 4 pasos |
| Replay buffer | 50.000 transiciones | Cubre todo el periodo de entrenamiento (~31 veces la serie) |
| Actualización red objetivo | cada 1.000 pasos (copia completa, τ = 1) | |
| ε inicial → final | 1,0 → 0,05 | |
| Fracción de exploración | 0,3 (ε llega a 0,05 en el paso 45.000) | |
| Criterio de parada | Número fijo de pasos (150.000) | No hay *early stopping* sobre validación: evitamos elegir el punto de corte mirando datos de evaluación |
| Semilla | 42 (modelo, entorno y sampler de Optuna) | Ver `10_reproducibilidad.md` |
| Recompensa × escala | × 100 (puntos porcentuales) | Estabiliza el entrenamiento; no cambia la política óptima |
| Costo de transacción | 10 bps sobre el valor operado | Igual para agente y baselines |

## Protocolo: train / validación / held-out y qué se decidió en cada uno

| Periodo | Fechas | Días | Para qué se usó | Qué **no** se hizo |
|---|---|---|---|---|
| Entrenamiento | 2009-08-03 → 2015-12-31 | 1.616 | Aprender los pesos de la red; calcular media y desviación de la normalización | — |
| Validación | 2016-01-04 → 2016-12-30 | 252 | Comparar las versiones de la recompensa, elegir la versión final (criterio retorno / máx. drawdown), calificar los trials de Optuna y medir la robustez por semillas | No se usa para entrenar |
| Held-out | 2017-01-03 → 2018-08-29 | 418 | Evaluación final, **una sola vez**, en la corrida oficial | No se usó para elegir hiperparámetros, recompensa, arquitectura ni versión final |

(Los primeros ~50 días de 2009 se descartan porque las medias móviles necesitan calentamiento.)

## Optuna: espacio de búsqueda y resultado (validación)

Comando: `uv run rlgames-sb tune --config configs/investor_dqn_log_dd.yaml`. Sampler TPE con semilla 42; 15 trials de 50.000 pasos cada uno. Cada trial entrena en 2009–2015 y se califica con la **recompensa total del episodio de validación 2016** (`eval_env: Investor-log_dd-val-v0`). El held-out nunca interviene.

| Hiperparámetro | Espacio |
|---|---|
| learning_rate | log-uniforme [3 × 10⁻⁵, 10⁻³] |
| γ | {0,9; 0,95; 0,99} |
| exploration_fraction | uniforme [0,1; 0,5] |
| batch_size | {32, 64, 128} |

**Resultado.** La búsqueda tardó 8 minutos. Solo 1 de los 15 trials terminó con recompensa positiva en validación: el trial 3 (learning rate 1,48 × 10⁻⁴, **γ = 0,9**, exploración 0,337, batch 64) con +0,47; los otros 14 quedaron entre −26,6 y −1,7, sin un patrón claro por hiperparámetro. Además, la recompensa que cada trial alcanza en entrenamiento no predice su resultado en validación (correlación de Spearman −0,01): los trials que más aprenden en 2009–2015 están entre los peores en 2016, señal de sobreajuste al periodo de entrenamiento y de no estacionariedad. Tabla, curvas de aprendizaje y figura en `docs/experimentos/optuna_y_semillas.md`.

**Limitaciones de la búsqueda.** (1) El objetivo de Optuna es la recompensa de validación, no el criterio retorno / máximo drawdown con el que se eligió la versión final; con `log_dd` ambos van en la misma dirección, pero no son idénticos. (2) Cada trial usa una sola semilla y solo 50.000 pasos (un tercio del entrenamiento final), así que el ranking incluye ruido de inicialización; con 15 trials y un único año de validación existe riesgo de sobreajustar a 2016. La prueba de semillas confirmó que ese riesgo se materializó.

## Robustez con semillas

Para no decidir con un solo trial, se reentrenaron **los dos candidatos (YAML y trial 3 de Optuna) con 150.000 pasos y 4 semillas** (42, 1, 7, 123), evaluando en validación 2016 (`scripts/semillas.py`).

| Configuración | Retorno acum. % (media ± desv.) | Máx. drawdown % | Retorno / DD medio | Cambios de posición | Exposición media % | Semillas con retorno > 0 |
|---|---|---|---|---|---|---|
| **YAML (v2 final)** | **+1,43 ± 5,42** | **8,86 ± 3,15** | **0,35** | 37 | 19,6 | 2 de 4 |
| Optuna (trial 3) | −7,46 ± 3,78 | 14,59 ± 4,62 | −0,50 | 68 | 31,9 | 0 de 4 |
| Comprar y mantener | +4,24 | 13,53 | 0,31 | 1 | 100 | — |

**Interpretación.**

- **Decisión: se mantienen los hiperparámetros del YAML.** El candidato de Optuna pierde con las 4 semillas, opera casi el doble y tiene más drawdown que el mercado. Su buen resultado en la búsqueda fue suerte de una semilla con 50.000 pasos: un caso de sobreajuste a la validación por quedarse con el máximo de 15 corridas ruidosas. Con γ = 0,9 el agente mira un horizonte de ~10 días y vuelve a sobreoperar, como v1 y v3. La decisión se tomó solo con validación y quedó en `docs/decisiones.md`; como confirma los hiperparámetros con que se hizo la corrida oficial, esta no se repite.
- **La v2 depende mucho de la semilla.** Con el YAML, 2 semillas ganan ~6 % con ~6 % de drawdown y 2 pierden entre 2,5 y 4 %. La desviación entre semillas (5,4 puntos) supera la diferencia media frente a comprar y mantener, así que en validación **no puede afirmarse que la v2 le gane al mercado en retorno**; el +9,0 % de la corrida oficial en validación es un caso favorable.
- **Lo robusto es el control del riesgo.** Las 4 semillas tienen menor drawdown que comprar y mantener (6,1–12,3 % frente a 13,5 %) y una exposición media de 16–27 %: la penalización produce de forma estable un agente conservador. Es lo que se observó después en el held-out: la v2 ganó +3,5 % frente a +56,4 % de comprar y mantener, con un drawdown algo menor (13,9 % frente a 15,4 %); ver `07_evaluacion.md`.
