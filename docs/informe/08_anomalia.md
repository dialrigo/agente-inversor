# Comportamiento inesperado del agente

| Dueño | Verifica | Fuente | Rúbrica |
|---|---|---|---|
| Lorena Valero (`LorenaValero20`) | janayajoo | Secc. 9 · `results/11` | 4 |

> **Estado:** la sección 01 describe el método. Las secciones 02 a 04 se completan con la salida de la sección 9 del notebook en la **corrida oficial**. Las líneas marcadas con ⏳ se reemplazan por los datos oficiales.

## 01. Cómo se identificó el comportamiento inesperado

En lugar de elegir a mano un episodio "interesante", lo que podría sesgar el análisis, el tramo se buscó de forma sistemática. Para cada día del held-out se calculó la diferencia entre el retorno logarítmico de 30 días hábiles del agente elegido y el de comprar y mantener. El tramo analizado es el de **mayor desventaja** del agente frente a ese baseline.

Para ese tramo se reportan:

- el movimiento del precio del activo;
- la exposición media del agente (qué fracción del capital tuvo invertida);
- cuántas veces cambió de posición.

Como diagnóstico adicional sobre todo el held-out se cuentan las **idas y vueltas**: secuencias A → B → A en tres días consecutivos, que indican que el agente cambia de decisión y vuelve atrás pagando dos veces el costo de operar.

## 02. Tramo de peor desempeño frente a comprar y mantener

*Figura 11 · `results/11_anomalia.png`.*

⏳ Datos de la salida del notebook:

| Dato | Valor |
|---|---|
| Fechas del tramo | ⏳ |
| Desventaja frente a comprar y mantener (puntos log) | ⏳ |
| Movimiento del precio en el tramo | ⏳ |
| Exposición media del agente | ⏳ |
| Cambios de posición en el tramo | ⏳ |
| Idas y vueltas en todo el held-out | ⏳ |

## 03. Qué hizo el agente y qué vio en el estado

⏳ Describir la decisión en palabras: ¿se salió del mercado (total o parcialmente) mientras el precio subía? ¿se quedó invertido durante una caída? ¿alternó de posición varias veces?

Para conectarlo con el estado, mirar en el tramo los indicadores que el agente observa. Por ejemplo, una caída corta previa en `ret_5` o `ret_20`, un salto de `vol_20` o un `rsi_14` alto pueden haber llevado al agente a reducir la exposición justo antes de una recuperación.

## 04. Hipótesis

⏳ Elegir la más consistente con lo observado y justificarla. Pueden combinarse.

| Hipótesis | Qué la apoyaría |
|---|---|
| **Efecto de la recompensa (reward hacking)** | Con la penalización de drawdown, el agente aprendió que salir del mercado tras una caída reduce la penalización, aunque luego se pierda la recuperación. Se vería como salidas sistemáticas después de días negativos |
| **No-estacionariedad** | Las relaciones que el agente aprendió en 2009–2015 no se mantienen en 2017–2018. Por ejemplo, la volatilidad de 2018 es distinta de la del entrenamiento. Se vería como indicadores fuera de los rangos típicos del entrenamiento |
| **Ruido o sobreajuste** | Con ~1.600 días de entrenamiento, la red pudo memorizar patrones sin valor predictivo. Se vería como cambios de posición sin relación clara con ningún indicador, o como muchas idas y vueltas |

⏳ Cerrar con una frase sobre qué se cambiaría para corregirlo. Por ejemplo: penalizar la rotación en la recompensa, más datos o un activo menos tendencial.
