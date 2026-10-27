"""API exclusiva de Playwright; base temporal y cierre explícito para Windows."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import uvicorn
from sqlmodel import Session

from conftest import temporary_postgres
from app.config import Settings
from app.db.session import get_session
from app.main import create_app


if __name__ == "__main__":
    with temporary_postgres() as engine:
        application = create_app(Settings(cors_origins=["http://127.0.0.1:5175"]))

        def test_session():
            with Session(engine) as session:
                yield session

        application.dependency_overrides[get_session] = test_session
        server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=8001, access_log=False))

        # Esta ruta solo existe en este proceso de pruebas, nunca en app.main.
        @application.post("/__test/shutdown")
        def shutdown():
            server.should_exit = True
            return {"status": "stopping"}

        server.run()
