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
├── package.json              # Dependencias y scripts de npm
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
