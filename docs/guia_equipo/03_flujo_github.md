# Flujo de trabajo en GitHub

## 1. Una sola vez

1. Acepta la invitación que llegó a tu correo (o entra a https://github.com/dialrigo/agente-inversor/invitations).
2. Clona e instala:

```powershell
git clone https://github.com/dialrigo/agente-inversor.git
cd agente-inversor
uv sync
uv run python scripts/prueba_humo.py
```

3. Configura tu nombre con el **mismo correo de tu cuenta de GitHub**. Si no, tus commits no te aparecen como contribuciones:

```powershell
git config user.name "Tu Nombre"
git config user.email "correo-de-tu-cuenta-github@ejemplo.com"
```

## 2. Ramas

Una rama por entregable, con este nombre:

| Tipo | Rama | Ejemplo |
|---|---|---|
| Función | `funcion/<tema>` | `funcion/tests-entorno`, `funcion/recompensa` |
| Reflexión | `reflexion/<usuario>` | `reflexion/andresdila` |

```powershell
git checkout main
git pull
git checkout -b funcion/<tema>
```

## 3. Commits pequeños y claros

Haz varios commits a medida que avanzas, no uno gigante al final. Formato del mensaje: `tipo(área): qué cambió`.

```powershell
git add docs/informe/05_recompensa.md
git commit -m "docs(recompensa): comparación de las 3 variantes en validación"
git push -u origin funcion/recompensa
```

Tipos: `feat` (código nuevo), `test`, `docs`, `fix`, `exp` (experimentos y configs).

## 4. Pull Request y verificación

1. En GitHub: **Compare & pull request** → base `main`.
2. La plantilla del PR ya trae el checklist. Marca lo que produjiste.
3. En *Reviewers* asigna a tu **verificador** (ver `01_funciones_y_checklists.md`).
4. El verificador revisa con su checklist y deja **Approve** o **Request changes**, comentando sobre las líneas concretas.
5. Diego hace el merge cuando hay aprobación y el CI está en verde.

## 5. Si `main` avanzó mientras trabajabas

```powershell
git checkout main
git pull
git checkout funcion/<tema>
git merge main
git push
```

Si aparece un conflicto en un archivo que no es tuyo, no lo resuelvas a ciegas: avisa a su dueño.
