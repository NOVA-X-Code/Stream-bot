"""
Database migration system
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

class Migration:
    """Database migration manager"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.migrations_dir = Path("migrations")
        self.migrations_dir.mkdir(exist_ok=True)
    
    async def create_migration(self, name: str, up_sql: str, down_sql: str) -> Path:
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.json"
        
        migration = {
            "name": name,
            "up": up_sql,
            "down": down_sql,
            "created_at": datetime.now().isoformat()
        }
        
        filepath = self.migrations_dir / filename
        with open(filepath, "w") as f:
            json.dump(migration, f, indent=2)
        
        return filepath
    
    async def migrate(self, target_version: Optional[str] = None):
        """Run pending migrations"""
        migrations = sorted(self.migrations_dir.glob("*.json"))
        current_version = await self._get_current_version()
        
        for migration_file in migrations:
            if target_version and migration_file.stem > target_version:
                break
            
            if migration_file.stem > current_version:
                print(f"⬆️ Applying migration: {migration_file.name}")
                with open(migration_file) as f:
                    migration = json.load(f)
                
                # Execute migration
                await self.client.rpc("execute_sql", {"sql": migration["up"]})
                
                # Update version
                await self._set_current_version(migration_file.stem)
    
    async def rollback(self, steps: int = 1):
        """Rollback migrations"""
        current_version = await self._get_current_version()
        migrations = sorted(self.migrations_dir.glob("*.json"))
        
        for _ in range(steps):
            if not current_version:
                break
            
            # Find current migration
            current_migration = next(
                (m for m in migrations if m.stem == current_version),
                None
            )
            
            if current_migration:
                print(f"⬇️ Rolling back: {current_migration.name}")
                with open(current_migration) as f:
                    migration = json.load(f)
                
                # Execute rollback
                await self.client.rpc("execute_sql", {"sql": migration["down"]})
                
                # Update version
                prev_version = migrations[
                    migrations.index(current_migration) - 1
                ].stem
                await self._set_current_version(prev_version)
                current_version = prev_version
    
    async def _get_current_version(self) -> str:
        """Get current schema version"""
        try:
            result = await self.client.table("schema_migrations") \
                .select("version") \
                .order("applied_at", ascending=False) \
                .limit(1) \
                .execute()
            
            if result:
                return result[0]["version"]
        except:
            await self._create_migrations_table()
        
        return ""
    
    async def _set_current_version(self, version: str):
        """Set current schema version"""
        await self.client.table("schema_migrations") \
            .insert({
                "version": version,
                "applied_at": datetime.now().isoformat()
            }) \
            .execute()
    
    async def _create_migrations_table(self):
        """Create the migrations table"""
        sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id BIGSERIAL PRIMARY KEY,
            version VARCHAR(50) NOT NULL,
            applied_at TIMESTAMP DEFAULT NOW()
        );
        """
        await self.client.rpc("execute_sql", {"sql": sql})
