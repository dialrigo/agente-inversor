# Guía del equipo · Agente Inversor

**Entrega:** domingo 18 de octubre de 2026, 23:59 (Moodle). Meta interna: **domingo a las 18:00**.
**Equipo:** 7 integrantes (confirmado con el profesor).
**Producto:** código reproducible (este repositorio) + informe + presentación para el panel o foro.

## Cómo trabajamos

Cada integrante **produce** una parte de la entrega y **verifica** la de otro compañero. Cada uno sube su parte con commits propios, en una rama propia, y la integra por Pull Request. El PR solo se fusiona cuando su verificador lo aprueba con el checklist.

| Archivo | Para qué |
|---|---|
| `00_LEEME_PRIMERO.md` | Este documento: plan, fechas y reglas |
| `01_funciones_y_checklists.md` | **Qué produce y qué verifica cada quien** |
| `02_guia_ejecucion.md` | Paso a paso para instalar y correr |
| `03_flujo_github.md` | Ramas, commits y Pull Requests |
| `../informe/` | Una sección del informe por archivo, cada una con dueño |
| `../reflexiones/` | Un archivo por integrante |

## Cronograma

| Día | Hito | Quién |
|---|---|---|
| **Mar 13** | Aceptar la invitación de GitHub, clonar, `uv sync`, prueba de humo y crear la rama propia | Todos |
| **Mar 13–Mié 14** | Tests del entorno y de métricas en `main` (CI en verde) | Nicolás, Lorena |
| **Mié 14** | Variante de recompensa `log` y Optuna/semillas sobre **validación** | janayajoo, Marlon |
| **Mié 14 (noche)** | **Corrida oficial** con la configuración final; commit de `results/` | Diego |
| **Jue 15** | Secciones del informe con los resultados oficiales (PR por cada una) | Andrés, Nicolás, janayajoo, Lorena, Marlon |
| **Vie 16** | Verificaciones cruzadas aprobadas y merge; reflexiones individuales | Todos |
| **Sáb 17** | Informe consolidado (Word/PDF), notebook integrado, presentación | Nataly, Diego |
| **Dom 18** | Checklist final y entrega antes de las 18:00 | Diego |

## Reglas de oro

1. **El held-out (2017–2018) se mira una sola vez,** en la corrida oficial. Para ajustar hiperparámetros o recompensa está la validación de 2016.
2. **Los errores de código sí se corrigen,** aunque ya hayamos visto el held-out. Se documentan en `docs/decisiones.md` y se repite la corrida oficial.
3. **Una sola corrida oficial alimenta el informe:** la de Diego, en `results/`.
4. **Un resultado negativo no es un mal proyecto.** La rúbrica premia la rigurosidad, no el retorno.
5. **Solo Diego edita el notebook.** Los demás escriben en `docs/informe/` y `docs/reflexiones/`.
6. **Nadie hace push directo a `main`.** Todo entra por Pull Request aprobado.
