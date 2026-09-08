from customtkinter import (
    CTk,
    CTkButton,
    CTkEntry,
    StringVar,
    IntVar,
    CTkToplevel,
    CTkLabel,
)
from tkinter import Menu, BOTH, NORMAL, DISABLED
from tkinter.ttk import Treeview
from tkinter.messagebox import showerror, askyesno
from .database import Database


class CreateEdit(CTkToplevel):
    def __init__(
        self, database: Database, callback, data: dict | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.database = database
        self.callback = callback

        self.data: dict | None = data
        self.title("Editar Producto" if data else "Crear Producto")

        CTkLabel(self, text="Código (4 caracteres):").pack()
        self.cvar: StringVar = StringVar(value="" if data is None else data["codigo"])
        self.cvar.trace_add("write", lambda *_: self.check_valid())
        self.codigo: CTkEntry = CTkEntry(self, textvariable=self.cvar)
        self.codigo.pack()
        if data is not None:
            self.codigo.configure(state=DISABLED)

        CTkLabel(self, text="Nombre:").pack()
        self.nvar: StringVar = StringVar(value="" if data is None else data["nombre"])
        self.nvar.trace_add("write", lambda *_: self.check_valid())
        self.nombre: CTkEntry = CTkEntry(self, textvariable=self.nvar)
        self.nombre.pack()

        CTkLabel(self, text="Cantidad (>= 0):").pack()
        self.cant_var: StringVar = StringVar(
            value="" if data is None else str(data["cantidad"])
        )
        self.cant_var.trace_add("write", lambda *_: self.check_valid())
        self.cantidad: CTkEntry = CTkEntry(self, textvariable=self.cant_var)
        self.cantidad.pack()

        CTkLabel(self, text="Precio (centavos):").pack()
        self.pvar: StringVar = StringVar(
            value="" if data is None else str(data["precio"])
        )
        self.pvar.trace_add("write", lambda *_: self.check_valid())
        self.precio: CTkEntry = CTkEntry(self, textvariable=self.pvar)
        self.precio.pack()

        self.btn_send: CTkButton = CTkButton(
            self, text="Guardar", state=DISABLED, command=self.save
        )
        self.btn_send.pack()
        self.check_valid()

    def check_valid(self):
        codigo = self.cvar.get().strip()
        nombre = self.nvar.get().strip()
        cant_str = self.cant_var.get().strip()
        precio_str = self.pvar.get().strip()

        is_valid = True
        if not self.data and len(codigo) != 4:
            is_valid = False
        if not nombre:
            is_valid = False
        try:
            cant = int(cant_str)
            if cant < 0:
                is_valid = False
        except ValueError:
            is_valid = False
        try:
            precio = int(precio_str)
            if precio <= 0:
                is_valid = False
        except ValueError:
            is_valid = False

        if is_valid:
            self.btn_send.configure(state=NORMAL)
        else:
            self.btn_send.configure(state=DISABLED)

    def save(self):
        try:
            codigo = self.cvar.get().strip()
            nombre = self.nvar.get().strip()
            cantidad = int(self.cant_var.get().strip())
            precio = int(self.pvar.get().strip())

            if self.data is None:
                self.database.insert_product(codigo, nombre, cantidad, precio)
            else:
                self.database.update_product(
                    codigo=codigo, nombre=nombre, cantidad=cantidad, precio=precio
                )

            self.callback()
            self.destroy()
        except Exception as e:
            showerror(title="Error", message=str(e))


class Gui(CTk):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.database: Database = Database()
        self.title("Productos")
        COLS: tuple[str, ...] = ("codigo", "nombre", "precio", "cantidad")
        self.table: Treeview = Treeview(self, columns=COLS, show="headings")
        for c in COLS:
            self.table.heading(c, text=c.capitalize())
        self.table.pack(expand=True, fill=BOTH)

        self.btn_create: CTkButton = CTkButton(
            self, text="Crear", command=self.open_create
        )
        self.btn_create.pack()

        self.cmenu: Menu = Menu(self, tearoff=0)
        self.cmenu.add_command(label="Editar", command=self.open_edit)
        self.cmenu.add_command(label="Eliminar", command=self.delete)

        self.table.bind("<Button-3>", self.show_menu)
        self.load_data()

    def load_data(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for r in self.database.get_products():
            self.table.insert(
                "",
                "end",
                iid=r[0],
                values=(r["codigo"], r["nombre"], r["precio"], r["cantidad"]),
            )

    def open_create(self):
        CreateEdit(database=self.database, callback=self.load_data)

    def open_edit(self):
        try:
            selected_id = self.table.selection()[0]
            values = self.table.item(selected_id, "values")
            data = {
                "codigo": values[0],
                "nombre": values[1],
                "precio": values[2],
                "cantidad": values[3],
            }
            CreateEdit(database=self.database, callback=self.load_data, data=data)
        except Exception as e:
            showerror(title="Error", message="Seleccione un elemento para editar.")

    def show_menu(self, event):
        item_id = self.table.identify_row(event.y)
        if item_id:
            if item_id not in self.table.selection():
                self.table.selection_set(item_id)
            self.cmenu.tk_popup(event.x_root, event.y_root)

    def delete(self):
        try:
            selected = self.table.selection()
            if not selected:
                return
            codigo: str = selected[0]
            if askyesno(message=f"Desea eliminar el producto {codigo}?"):
                self.database.delete_product(codigo)
                self.table.delete(codigo)
        except Exception as e:
            showerror(message=e)


if __name__ == "__main__":
    Gui().mainloop()
