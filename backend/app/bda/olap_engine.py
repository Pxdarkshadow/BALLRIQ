"""
BDA DuckDB OLAP Engine: Executes high-speed SQL queries directly over partitioned Parquet Lakehouse.
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
import duckdb
import os

BASE_DIR = Path(__file__).resolve().parents[3]
LAKE_DIR = BASE_DIR / "data" / "lake"


class CricketOLAPEngine:
    def __init__(self, lake_dir: Path = LAKE_DIR):
        self.lake_dir = lake_dir
        self.con = duckdb.connect(database=":memory:")
        self._register_views()

    def _register_views(self):
        """Register Parquet directories as zero-copy SQL views in DuckDB."""
        matches_path = str(self.lake_dir / "matches" / "**" / "*.parquet").replace("\\", "/")
        comm_path = str(self.lake_dir / "commentary" / "**" / "*.parquet").replace("\\", "/")
        events_path = str(self.lake_dir / "ball_events.parquet").replace("\\", "/")
        batting_path = str(self.lake_dir / "batting_stats.parquet").replace("\\", "/")
        bowling_path = str(self.lake_dir / "bowling_stats.parquet").replace("\\", "/")
        players_path = str(self.lake_dir / "players.parquet").replace("\\", "/")

        if (self.lake_dir / "matches").exists():
            self.con.execute(f"CREATE OR REPLACE VIEW matches AS SELECT * FROM read_parquet('{matches_path}', hive_partitioning=1);")
        if (self.lake_dir / "commentary").exists():
            self.con.execute(f"CREATE OR REPLACE VIEW commentary AS SELECT * FROM read_parquet('{comm_path}', hive_partitioning=1);")
        if (self.lake_dir / "ball_events.parquet").exists():
            self.con.execute(f"CREATE OR REPLACE VIEW ball_events AS SELECT * FROM read_parquet('{events_path}');")
        if (self.lake_dir / "batting_stats.parquet").exists():
            self.con.execute(f"CREATE OR REPLACE VIEW batting_stats AS SELECT * FROM read_parquet('{batting_path}');")
        if (self.lake_dir / "bowling_stats.parquet").exists():
            self.con.execute(f"CREATE OR REPLACE VIEW bowling_stats AS SELECT * FROM read_parquet('{bowling_path}');")
        if (self.lake_dir / "players.parquet").exists():
            self.con.execute(f"CREATE OR REPLACE VIEW players AS SELECT * FROM read_parquet('{players_path}');")

    def get_lakehouse_summary(self) -> Dict[str, Any]:
        """Return dataset statistics, partition layouts, and file sizes."""
        tables_info = []
        for table in ["matches", "commentary", "ball_events", "batting_stats", "bowling_stats", "players"]:
            try:
                count = self.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                cols = [desc[0] for desc in self.con.execute(f"SELECT * FROM {table} LIMIT 0").description]
                tables_info.append({
                    "table_name": table,
                    "row_count": count,
                    "column_count": len(cols),
                    "columns": cols
                })
            except Exception as e:
                pass

        total_bytes = sum(f.stat().st_size for f in self.lake_dir.rglob("*.parquet") if f.is_file())
        return {
            "lake_path": str(self.lake_dir),
            "total_size_mb": round(total_bytes / (1024 * 1024), 2),
            "tables": tables_info,
            "engine": "DuckDB Columnar In-Memory OLAP",
            "storage_format": "Apache Parquet (Snappy Compressed)"
        }

    def get_phase_analytics(self, match_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Phase-wise breakdown (Powerplay, Middle, Death) of run rates, boundaries, dot balls."""
        where_clause = f"WHERE match_id = '{match_id}'" if match_id else ""
        query = f"""
            SELECT
                phase,
                COUNT(*) as total_balls,
                SUM(runs) as total_runs,
                ROUND(AVG(runs) * 6, 2) as estimated_run_rate,
                SUM(is_boundary) as boundaries,
                ROUND(SUM(is_boundary) * 100.0 / COUNT(*), 2) as boundary_percentage,
                SUM(is_dot) as dot_balls,
                ROUND(SUM(is_dot) * 100.0 / COUNT(*), 2) as dot_percentage,
                SUM(is_wicket) as wickets
            FROM ball_events
            {where_clause}
            GROUP BY phase
            ORDER BY CASE
                WHEN phase = 'Powerplay' THEN 1
                WHEN phase = 'Middle' THEN 2
                ELSE 3
            END;
        """
        df = self.con.execute(query).df()
        return df.to_dict(orient="records")

    def get_multilingual_commentary_metrics(self) -> List[Dict[str, Any]]:
        """Big data aggregation of commentary text characteristics across languages."""
        query = """
            SELECT
                language,
                COUNT(*) as total_commentary,
                ROUND(AVG(text_length), 1) as avg_char_length,
                SUM(is_boundary) as total_boundary_mentions,
                SUM(is_wicket) as total_wicket_mentions
            FROM ball_events
            GROUP BY language
            ORDER BY total_commentary DESC;
        """
        df = self.con.execute(query).df()
        return df.to_dict(orient="records")

    def get_top_batting_aggregates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Aggregate top run scorers, strike rates and boundary counts."""
        query = f"""
            SELECT
                p.name as player_name,
                COUNT(*) as innings_played,
                SUM(b.runs) as total_runs,
                SUM(b.balls) as total_balls,
                ROUND(SUM(b.runs) * 100.0 / NULLIF(SUM(b.balls), 0), 2) as strike_rate,
                SUM(b.fours) as total_fours,
                SUM(b.sixes) as total_sixes,
                MAX(b.runs) as high_score
            FROM batting_stats b
            JOIN players p ON b.player_id = p.player_id
            GROUP BY p.name
            ORDER BY total_runs DESC
            LIMIT {limit};
        """
        df = self.con.execute(query).df()
        return df.to_dict(orient="records")

    def get_top_bowling_aggregates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Aggregate top wicket takers and economy rates."""
        query = f"""
            SELECT
                p.name as player_name,
                COUNT(*) as innings_bowled,
                SUM(bw.wickets) as total_wickets,
                SUM(bw.runs_conceded) as total_runs_conceded,
                ROUND(SUM(bw.overs), 1) as total_overs,
                ROUND(SUM(bw.runs_conceded) / NULLIF(SUM(bw.overs), 0), 2) as economy_rate
            FROM bowling_stats bw
            JOIN players p ON bw.player_id = p.player_id
            GROUP BY p.name
            ORDER BY total_wickets DESC, economy_rate ASC
            LIMIT {limit};
        """
        df = self.con.execute(query).df()
        return df.to_dict(orient="records")

    def execute_custom_sql(self, sql_query: str) -> Dict[str, Any]:
        """Execute arbitrary read-only SQL for the BDA interactive explorer."""
        # Sanitize basic dangerous commands
        sanitized = sql_query.strip().lower()
        if any(bad in sanitized for bad in ["drop", "delete", "insert", "update", "alter", "truncate", "copy"]):
            return {"status": "error", "error": "Only read-only SELECT queries are allowed."}

        try:
            rel = self.con.execute(sql_query)
            cols = [desc[0] for desc in rel.description] if rel.description else []
            rows = rel.fetchall()
            return {
                "status": "success",
                "columns": cols,
                "rows": [list(r) for r in rows[:100]],
                "total_rows_returned": len(rows),
                "is_truncated": len(rows) > 100
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
