# Sistema de Control y Búsqueda de Inventario de Libros
## Biblioteca Pública Central Cecilio Acosta

Sistema web para la gestión centralizada de inventario de libros, consulta pública de catálogo, seguimiento de ejemplares físicos, control de visitas presenciales y análisis estadístico de visitantes para la Biblioteca Pública Central Cecilio Acosta (Los Teques, Estado Miranda).

---

### Características Principales

* **Gestión de Catálogo:** Registro, actualización, catalogación decimal Dewey y retiro de títulos.
* **Control de Ejemplares Físicos:** Mapeo de copias por libro con ubicación física detallada en estantería y control de disponibilidad en tiempo real.
* **Formatos Accesibles:** Soporte nativo para filtrado y catalogación de obras adaptadas en sistema Braille y audiolibros.
* **Catálogo Público y Lista de Intereses:** Búsqueda según filtros y carrusel personalizado para usuarios registrados.
* **Control de Asistencia Digital:** Registro de visitas de ciudadanos en sala y módulo analítico con gráficos interactivos de tendencias.
* **Arquitectura Limpia:** Separación estricta entre entidades de dominio, contratos, DAOs con SQLAlchemy 2.0, servicios de aplicación y controladores Flask basados en vistas.

---

### Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Framework Web:** Flask 3.1.3 (Jinja2, MethodViews)
* **Base de Datos:** PostgreSQL
* **ORM:** SQLAlchemy 2.0.51 / Flask-SQLAlchemy 3.1.1
* **Frontend:** HTML5, CSS3 modular (variables nativas), JavaScript (Fetch API) y Chart.js
* **Pruebas y Calidad:** Pytest, Pytest-Cov, Ruff Linter y Formatter, Pre-commit Hooks

---

### Estructura del Proyecto

```text
├── config/
│   ├── base.py
│   ├── development.py
│   ├── production.py
│   └── testing.py
├── docs/
│   ├── mer.png
│   └── mer.puml
├── src/
│   ├── contracts/
│   ├── dao/
│   ├── dtos/
│   ├── entities/
│   ├── exceptions/
│   ├── handlers/
│   ├── models/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   ├── db/
│   │   ├── db.sql
│   │   └── data_dummy.sql
│   ├── extensions.py
│   └── __init__.py
├── tests/
│   ├── conftest.py
│   ├── test_dtos.py
│   ├── test_core_service.py
│   └── test_inventory_service.py
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── requirements.txt
├── seed_admin.py
└── wsgi.py
```

---

### Instalación y Configuración

#### 1. Clonar el repositorio
```bash
git clone https://github.com/AndresDN1/sistema-biblioteca-cecilio-acosto
.git
cd <sistema-biblioteca-cecilio-acosto>
```

#### 2. Crear y activar el entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### 3. Instalar las dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno
Crear un archivo `.env` en la raíz del proyecto:
```ini
APP_SETTINGS=config.development.DevelopmentConfig
SECRET_KEY= (Generar clave criptográfica)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/library
```

#### 5. Configurar la base de datos PostgreSQL
Crear la base de datos en PostgreSQL:
```sql
CREATE DATABASE library;
```

Ejecutar la estructura del esquema:
```bash
psql -U postgres -d library -h localhost -f src/db/db.sql
```

Almacenar el usuario administrador inicial:
```bash
python seed_admin.py
```

Poblar con datos de prueba:
```bash
psql -U postgres -d library -h localhost -f src/db/data_dummy.sql
```

---

### Ejecución de la Aplicación

```bash
python wsgi.py
```

La plataforma estará disponible en:
```text
http://127.0.0.1:5000/
```

Credenciales de acceso administrativo:
* **Usuario:** `admin`
* **Contraseña:** `admin123`

---

### Pruebas Unitarias y Cobertura

Ejecutar la suite completa de pruebas:
```bash
pytest -v
```

Generar el informe de cobertura de código en terminal y formato HTML:
```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

---

### Calidad de Código y Git Hooks

Instalar los ganchos de control de calidad para formateo y análisis estático automático con Ruff antes de cada confirmación:
```bash
pre-commit install
```

Ejecutar manualmente el linter y formateador sobre todo el código:
```bash
pre-commit run --all-files
```
