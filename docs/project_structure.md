# プロジェクト構成案

## 1. ディレクトリ構造

```
Galactic-Ledger/
├── backend/                # Python / FastAPI
│   ├── app/
│   │   ├── api/            # API Endpoints (Routes)
│   │   │   ├── v1/         # API Versioning
│   │   │   └── deps.py     # Dependencies (DB session, User auth)
│   │   ├── core/           # Config, Security, Events
│   │   ├── db/             # Database connectivity
│   │   ├── models/         # SQLAlchemy ORM Models (DB Schema)
│   │   ├── schemas/        # Pydantic Models (Request/Response)
│   │   ├── services/       # Business Logic (Economy, Combat, Pathfinding)
│   │   └── main.py         # Entry point
│   ├── tests/              # Pytest
│   ├── alembic/            # DB Migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
│
├── frontend/               # React / TypeScript / Vite
│   ├── src/
│   │   ├── assets/         # Images, Fonts
│   │   ├── components/     # Reusable UI Components (Buttons, Panels)
│   │   ├── features/       # Feature-based modules
│   │   │   ├── map/        # Galaxy Map (PixiJS logic)
│   │   │   ├── market/     # Market Dashboard & Charts
│   │   │   └── fleet/      # Fleet Management
│   │   ├── hooks/          # Custom Hooks (API fetch, WebSocket)
│   │   ├── stores/         # Global State (Zustand/Redux)
│   │   ├── types/          # TypeScript definitions
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docs/                   # Documentation
├── infra/                  # Infrastructure (Nginx, MySQL configs)
└── docker-compose.yml      # Orchestration
```

## 2. モジュール設計のポイント

### Backend: Service Layer Pattern
- **Logicの分離**: APIルーター（Controller）にロジックを書かず、`services/` ディレクトリにビジネスロジックを集約します。
    - 例: `POST /buy` は `market_service.execute_trade()` を呼ぶだけ。
- これにより、WebSocketや定期実行バッチ（Celery）からも同じロジックを再利用可能にします。

### Frontend: Feature-based Architecture
- 機能ごとにフォルダを分けることで、コードベースが肥大化してもメンテナンス性を保ちます。
- `features/map` の中には、その機能専用のコンポーネント、フック、型定義を閉じ込めます。
