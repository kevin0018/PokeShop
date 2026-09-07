# PokeShop

Proyecto de e-commerce de Pokémon implementado con Domain Driven Design (DDD), Bounded Context y Arquitectura Hexagonal.

## Estructura del Proyecto

El proyecto está organizado siguiendo los principios de DDD con Bounded Contexts bien definidos:

### Backend (Python/FastAPI)
```
backend/
├── main.py                    # Punto de entrada de la aplicación
├── pyproject.toml            # Configuración y dependencias
├── .env.example              # Variables de entorno de ejemplo
└── src/
    ├── pokemon/              # Bounded Context: Gestión de Pokémon
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── presentation/
    ├── user/                 # Bounded Context: Gestión de Usuarios
    │   ├── domain/
    │   ├── application/
    │   ├── infrastructure/
    │   └── presentation/
    └── shared/               # Código compartido entre contextos
        ├── domain/
        ├── infrastructure/
        └── presentation/
```

### Frontend (Vue.js/TypeScript)
```
frontend/
├── src/
│   ├── App.vue               # Componente raíz de la aplicación
│   ├── main.ts               # Punto de entrada de la aplicación
│   ├── pokemon/              # Bounded Context: Gestión de Pokémon
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   ├── cart/                 # Bounded Context: Carrito de Compras
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   ├── user/                 # Bounded Context: Gestión de Usuarios
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   ├── shared/               # Código compartido entre contextos
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   └── presentation/
│   ├── components/           # Componentes Vue reutilizables
│   ├── views/                # Páginas de la aplicación
│   ├── router/               # Configuración de rutas
│   └── stores/               # Estados globales (Pinia)
├── package.json              # Dependencias y scripts de pnpm
├── vite.config.ts            # Configuración de Vite
├── tailwind.config.js        # Configuración de TailwindCSS
└── tsconfig.json             # Configuración de TypeScript
```

## Arquitectura por Bounded Context

Cada Bounded Context sigue la arquitectura hexagonal con las siguientes capas:

- **Domain**: Entidades, Value Objects, Servicios de Dominio y Reglas de Negocio
- **Application**: Casos de Uso, Commands, Queries y Application Services  
- **Infrastructure**: Implementaciones de repositorios, APIs externas, base de datos
- **Presentation**: Controllers, DTOs, Interfaces de usuario

## Bounded Contexts Definidos

### 1. Pokemon Context
Responsable de la gestión del catálogo de Pokémon, sus características, tipos, evoluciones, etc.

### 2. User Context  
Gestiona el registro, autenticación, perfiles de usuario y preferencias.

### 3. Cart Context (Frontend)
Maneja el carrito de compras, añadir/quitar productos, cálculos de precio.

### 4. Shared Context
Contiene código compartido como Value Objects comunes, servicios de infraestructura compartidos, etc.

## Tecnologías Utilizadas

### Backend
- **Python 3.11+**
- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos y settings

### Frontend  
- **Vue.js 3** - Framework JavaScript progresivo
- **TypeScript** - Superset tipado de JavaScript
- **Vite** - Build tool y dev server
- **TailwindCSS** - Framework CSS utility-first
- **Pinia** - Store management
- **Vue Router** - Routing


## Desarrollo con Docker

Requisito: Docker Desktop con contenedores Linux y Docker Compose v2.
No necesitas instalar Python, Node.js ni pnpm en el host.
Si un puerto est� ocupado, copia `.env.example` a `.env` en la ra�z y cambia
`FRONTEND_PORT` o `BACKEND_PORT`; las URLs siguientes muestran los valores por defecto.
Compose adapta CORS autom�ticamente al puerto del frontend.

```sh
docker compose up --build --wait
```

- Frontend Vue/Vite: http://localhost:5173
- API FastAPI: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Compose arranca frontend, backend, PostgreSQL 16 y Redis 7, esperando a que
sus health checks pasen. Los puertos web solo se publican en localhost;
PostgreSQL y Redis son accesibles dentro de la red de Compose como `db:5432`
y `redis:6379`. Sus datos se conservan en vol�menes entre reinicios.
Las credenciales de Compose son exclusivamente para desarrollo local.

El c�digo se monta en los contenedores y se recarga al editarlo. Se activa
polling para detectar cambios tambi�n en Windows/WSL. Las dependencias de
Vue se guardan en un volumen Linux separado del `node_modules` del host.
El frontend usa pnpm 10.10.0 y su lockfile; Python conserva Poetry y su lockfile.

El backend est� en fase de estructura inicial: actualmente solo implementa
`/health` y la documentaci�n de FastAPI. Los contextos contienen marcadores
`.keep`; todav�a no hay rutas de usuarios/Pok�mon, modelos ni migraciones.
PostgreSQL y Redis quedan preparados mediante `DATABASE_URL` y `REDIS_URL`,
pero el health check de la API no verifica conexiones a estos servicios.
No se crean tablas ni se cargan datos autom�ticamente.

```sh
# Estado y logs
docker compose ps
docker compose logs -f

# Verificar dentro de los contenedores
docker compose exec frontend pnpm build
docker compose exec backend python -m unittest discover -s tests -v

# A�adir una dependencia de Vue y actualizar el lockfile
docker compose exec frontend pnpm add <paquete>

# Tras modificar dependencias o Dockerfiles
docker compose up --build --wait

# Detener el stack conservando los datos
docker compose down
```

Este Compose usa servidores de desarrollo, no es una configuraci�n de producci�n.
No utilices `docker compose down -v` si quieres conservar los datos: elimina
los vol�menes de PostgreSQL, Redis y dependencias del frontend.

Para desarrollo sin Docker, consulta [frontend/README.md](frontend/README.md)
y [backend/README.md](backend/README.md).
