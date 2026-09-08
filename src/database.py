from sqlite3 import connect, Connection, Cursor, Error, Row
from pathlib import Path
from contextlib import contextmanager
from collections.abc import Generator


class Database:
    def __init__(self) -> None:
        self.conn: Connection = connect(Path.home() / "DB.sqlite")
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS productos(
                codigo TEXT PRIMARY KEY CHECK(length(codigo) = 4),
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL CHECK(cantidad > -1),
                precio INTEGER NOT NULL CHECK(precio > 0)
            );
        """
        )
        self.conn.row_factory = Row

    @contextmanager
    def get_cursor(self) -> Generator[Cursor]:
        cursor: Cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Error as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def insert_product(
        self, codigo: str, nombre: str, cantidad: int, precio: int
    ) -> None:
        with self.get_cursor() as c:
            c.execute(
                "INSERT INTO productos (codigo, cantidad, precio, nombre) VALUES (?, ?, ?, ?);",
                (codigo, cantidad, precio, nombre),
            )

    def delete_product(self, codigo: str) -> None:
        with self.get_cursor() as c:
            c.execute("DELETE FROM productos WHERE codigo = ?;", (codigo,))

    def update_product(
        self,
        codigo: str,
        nombre: str | None = None,
        cantidad: int | None = None,
        precio: int | None = None,
    ) -> None:
        data: dict = {} 

        if nombre is not None:
            data["nombre"] = nombre
        if cantidad is not None:
            data["cantidad"] = cantidad
        if precio is not None:
            data["precio"] = precio

        if not data:
            return

        query = f"UPDATE productos SET {', '.join([f"{c} = ?" for c in tuple(data.keys())])} WHERE codigo = ?;"

        with self.get_cursor() as c:
            c.execute(query, list(data.values()) + [codigo])
    
    def get_products(self) -> list[Row]:
        with self.get_cursor() as c:
            return c.execute("SELECT * FROM productos;").fetchall()
