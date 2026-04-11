"""
Management command untuk backup database
Supports SQLite dan PostgreSQL dengan progress tracking
"""
import os
import gzip
import subprocess
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.utils import timezone
from django.db import connection
from core.models import BackupLog
from io import StringIO


class Command(BaseCommand):
    help = 'Backup database dengan progress tracking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress backup file dengan gzip'
        )
        parser.add_argument(
            '--backup-id',
            type=int,
            help='BackupLog ID untuk tracking progress'
        )

    def handle(self, *args, **options):
        compress = options.get('compress', False)
        backup_id = options.get('backup_id')
        
        if not backup_id:
            self.stdout.write(self.style.ERROR('BackupLog ID is required'))
            return
        
        try:
            backup_log = BackupLog.objects.get(id=backup_id)
        except BackupLog.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'BackupLog with ID {backup_id} not found'))
            return
        
        # Update status to IN_PROGRESS
        backup_log.status = 'IN_PROGRESS'
        backup_log.progress = 5
        backup_log.save()
        
        try:
            # Tentukan database engine
            db_config = settings.DATABASES['default']
            db_engine = db_config['ENGINE']
            
            # Buat direktori backup jika belum ada
            backup_dir = os.path.join(settings.BASE_DIR, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if 'sqlite' in db_engine:
                base_filename = f'backup_sqlite_{timestamp}.sql'
            else:
                base_filename = f'backup_postgres_{timestamp}.sql'
            
            if compress:
                filename = base_filename + '.gz'
            else:
                filename = base_filename
            
            backup_log.filename = filename
            backup_log.progress = 10
            backup_log.save()
            
            backup_path = os.path.join(backup_dir, filename)
            
            self.stdout.write(f'Starting backup to {backup_path}')
            
            # Lakukan backup sesuai database
            if 'sqlite' in db_engine:
                self._backup_sqlite(db_config, backup_path, backup_log, compress)
            elif 'postgresql' in db_engine:
                self._backup_postgres(db_config, backup_path, backup_log, compress)
            else:
                raise Exception(f'Unsupported database engine: {db_engine}')
            
            # Update backup log
            backup_log.status = 'COMPLETED'
            backup_log.progress = 100
            backup_log.completed_at = timezone.now()
            backup_log.file_size = os.path.getsize(backup_path)
            backup_log.save()
            
            self.stdout.write(self.style.SUCCESS(f'Backup completed: {backup_path}'))
            self.stdout.write(self.style.SUCCESS(f'File size: {backup_log.file_size} bytes'))
            
        except Exception as e:
            backup_log.status = 'FAILED'
            backup_log.error_message = str(e)
            backup_log.completed_at = timezone.now()
            backup_log.save()
            self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
            raise

    def _backup_sqlite(self, db_config, backup_path, backup_log, compress):
        """Backup SQLite database"""
        db_path = db_config['NAME']
        
        if not os.path.exists(db_path):
            raise Exception(f'Database file not found: {db_path}')
        
        self.stdout.write('Backing up SQLite database...')
        backup_log.progress = 20
        backup_log.save()
        
        # Gunakan sqlite3 command untuk dump
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        backup_log.progress = 30
        backup_log.save()
        
        if compress:
            # Dump dan compress langsung
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
                    # Update progress periodically
                    if 'CREATE' in line or 'INSERT' in line:
                        if backup_log.progress < 90:
                            backup_log.progress += 1
                            backup_log.save()
        else:
            # Dump biasa
            with open(backup_path, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write(f'{line}\n')
                    # Update progress periodically
                    if 'CREATE' in line or 'INSERT' in line:
                        if backup_log.progress < 90:
                            backup_log.progress += 1
                            backup_log.save()
        
        conn.close()
        backup_log.progress = 95
        backup_log.save()

    def _backup_postgres(self, db_config, backup_path, backup_log, compress):
        """Backup PostgreSQL database menggunakan Django dumpdata"""
        self.stdout.write('Backing up PostgreSQL database...')
        backup_log.progress = 20
        backup_log.save()
        
        # Coba menggunakan pg_dump dulu (jika tersedia)
        pg_dump_available = self._check_pg_dump()
        
        if pg_dump_available:
            self.stdout.write('Using pg_dump for backup...')
            self._backup_postgres_with_pg_dump(db_config, backup_path, backup_log, compress)
        else:
            self.stdout.write('pg_dump not found, using Django dumpdata instead...')
            self._backup_postgres_with_dumpdata(backup_path, backup_log, compress)
    
    def _check_pg_dump(self):
        """Check if pg_dump is available"""
        try:
            result = subprocess.run(
                ['pg_dump', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _backup_postgres_with_pg_dump(self, db_config, backup_path, backup_log, compress):
        """Backup PostgreSQL dengan pg_dump command"""
        env = os.environ.copy()
        if db_config.get('PASSWORD'):
            env['PGPASSWORD'] = db_config['PASSWORD']
        
        cmd = [
            'pg_dump',
            '-h', db_config.get('HOST', 'localhost'),
            '-p', str(db_config.get('PORT', 5432)),
            '-U', db_config.get('USER', 'postgres'),
            '-d', db_config['NAME'],
            '--no-owner',
            '--no-acl',
        ]
        
        backup_log.progress = 30
        backup_log.save()
        
        try:
            if compress:
                self.stdout.write('Dumping and compressing...')
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                backup_log.progress = 70
                backup_log.save()
                
                with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                    f.write(result.stdout)
                
                backup_log.progress = 95
                backup_log.save()
            else:
                cmd.extend(['-f', backup_path])
                subprocess.run(cmd, env=env, check=True)
                
                backup_log.progress = 95
                backup_log.save()
                
        except subprocess.CalledProcessError as e:
            raise Exception(f'pg_dump failed: {e.stderr if hasattr(e, "stderr") else str(e)}')
    
    def _backup_postgres_with_dumpdata(self, backup_path, backup_log, compress):
        """Backup PostgreSQL using Django dumpdata (fallback method)"""
        from django.core.management import call_command
        from io import StringIO
        
        backup_log.progress = 30
        backup_log.save()
        
        # Generate SQL dump with schema and data
        sql_output = StringIO()
        
        # Get schema SQL
        self.stdout.write('Generating schema SQL...')
        with connection.cursor() as cursor:
            # Get all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'babycare' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            backup_log.progress = 40
            backup_log.save()
            
            # Write header
            sql_output.write("-- PostgreSQL Database Backup\n")
            sql_output.write(f"-- Generated by Django on {datetime.now()}\n")
            sql_output.write(f"-- Database: {connection.settings_dict['NAME']}\n")
            sql_output.write("-- Using Django dumpdata method\n\n")
            sql_output.write("BEGIN;\n\n")
            
            progress_step = 50 / len(tables) if tables else 0
            current_progress = 40
            
            # For each table, get CREATE statement and data
            for table in tables:
                self.stdout.write(f'Processing table: {table}')
                
                # Get table schema
                cursor.execute(f"""
                    SELECT column_name, data_type, character_maximum_length,
                           is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'babycare' AND table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                
                # Write CREATE TABLE equivalent (simplified)
                sql_output.write(f"-- Table: {table}\n")
                
                # Get all data from table
                cursor.execute(f'SELECT * FROM babycare.{table}')
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    column_names = [desc[0] for desc in cursor.description]
                    
                    # Write INSERT statements
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # Escape single quotes
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            elif isinstance(value, bool):
                                values.append('TRUE' if value else 'FALSE')
                            elif isinstance(value, datetime):
                                values.append(f"'{value.isoformat()}'")
                            else:
                                values.append(f"'{str(value)}'")
                        
                        sql_output.write(
                            f"INSERT INTO babycare.{table} ({', '.join(column_names)}) "
                            f"VALUES ({', '.join(values)});\n"
                        )
                
                sql_output.write("\n")
                
                current_progress += progress_step
                backup_log.progress = int(current_progress)
                backup_log.save()
            
            sql_output.write("COMMIT;\n")
        
        backup_log.progress = 90
        backup_log.save()
        
        # Write to file
        sql_content = sql_output.getvalue()
        
        if compress:
            with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                f.write(sql_content)
        else:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(sql_content)
        
        backup_log.progress = 95
        backup_log.save()
        
        self.stdout.write(f'Backup completed with {len(tables)} tables')
