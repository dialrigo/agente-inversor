# Guía del equipo · Agente Inversor

**Entrega:** domingo 18 de octubre de 2026, 23:59 (Moodle). Meta interna: **domingo a las 18:00**.
**Equipo:** 7 integrantes, confirmado con el profesor.
**Producto:** código reproducible (este repositorio) e informe.

## Cómo trabajamos

Repetimos el esquema de la actividad anterior: **una persona integra y cada integrante revisa un criterio de la rúbrica**. Cada criterio vale 1 punto, así que cada rol es dueño de "su punto". Los roles y checklists están en [01_roles_y_checklists.md](01_roles_y_checklists.md).

| Archivo | Para qué |
|---|---|
| `00_LEEME_PRIMERO.md` | Este documento: plan, fechas y reglas |
| `01_roles_y_checklists.md` | Qué revisa cada quien, contra qué criterio de la rúbrica |
| `02_guia_ejecucion.md` | Paso a paso para clonar, instalar y correr |
| `03_estructura_informe.md` | Esqueleto del informe, sección por sección |

## Cronograma

| Día | Qué | Quién |
|---|---|---|
| **Lun 12** | Repositorio armado: entorno, notebook y guías | Diego |
| **Mar 13** | Repo en GitHub con los 7 colaboradores. Todos clonan, `uv sync` y prueba de humo | Diego → todos |
| **Mié 14** | **Corrida oficial** (Run All con `RETRAIN = True`), commit de `results/`. Empieza la revisión por roles | Diego → todos |
| **Jue 15** | Revisión por roles. Ajustes **solo** con datos de train o validación. Si hay ajuste, nueva corrida oficial | Roles 1 a 4 |
| **Vie 16** | Interpretaciones escritas en el notebook. Reflexiones individuales | Todos |
| **Sáb 17** | Informe consolidado. Prueba de reproducibilidad desde cero en otra máquina | Nataly · Marlon |
| **Dom 18** | Revisión final y entrega antes de las 18:00 | Diego |

## Reglas de oro (la rúbrica castiga esto)

1. **El held-out (2017–2018) se mira una sola vez.** Nada de "probemos otro learning rate porque en test dio mal". Para eso está la validación de 2016.
2. **Si encuentras un error de código** (por ejemplo, lookahead o un costo mal cobrado), eso sí se corrige aunque ya hayamos visto el held-out. Se documenta en `docs/decisiones.md` y se repite la corrida oficial completa.
3. **Una sola corrida oficial** alimenta el informe: la de Diego, guardada en `results/`. Las corridas de cada integrante son para verificar, no para reemplazar números.
4. **Un resultado negativo no es un mal proyecto.** Si el agente no le gana a comprar y mantener, lo explicamos con honestidad. La rúbrica premia la rigurosidad, no el retorno.
5. **Cambios pequeños y documentados.** Cualquier decisión nueva va en `docs/decisiones.md` con fecha, autor y motivo.

## Flujo en GitHub

- Diego mantiene la rama `main`.
- Cada rol trabaja en una rama `revision/<rol>` (por ejemplo `revision/entorno`) y abre un Pull Request.
- Los comentarios de revisión van como *issues* o comentarios en el PR, citando la celda o la línea.
- Nadie hace push directo a `main` después de la corrida oficial.

```powershell
git clone https://github.com/dialrigo/agente-inversor.git
cd agente-inversor
git checkout -b revision/<tu-rol>
# ... cambios ...
git add -A
git commit -m "revision(<rol>): <qué cambió>"
git push -u origin revision/<tu-rol>
```
