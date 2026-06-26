"""Create default users for local development only.

WARNING: These are development-only credentials.
Production must use environment variables or secrets manager.
"""
import asyncio
import sys
sys.path.insert(0, "/app")

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

async def main():
    from app.core.config import settings
    from app.models.usuario import Usuario
    from app.core.database import Base
    from app.auth.service import AuthService

    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        result = await db.execute(select(Usuario).where(Usuario.username == "admin"))
        existing = result.scalar_one_or_none()

        if existing:
            print("Admin user already exists")
        else:
            admin = Usuario(
                username="admin",
                password_hash=AuthService.hash_password("admin123"),
                role="administrador",
                active=True,
            )
            db.add(admin)

            operador = Usuario(
                username="operador",
                password_hash=AuthService.hash_password("operador123"),
                role="operador",
                active=True,
            )
            db.add(operador)

            await db.commit()
            print("Created dev users: admin (administrador), operador (operador)")

    await engine.dispose()

asyncio.run(main())
