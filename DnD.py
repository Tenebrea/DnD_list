import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import json
import sqlite3


db_path = "Details.db"

class CharacterSheetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("D&D 2024 Character Sheet")
        self.geometry("800x700")

        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()

        self.character_data = {}

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Имя персонажа")
        self.name_entry.pack(pady=5)

        self.level_entry = ctk.CTkEntry(self, placeholder_text="Уровень")
        self.level_entry.pack(pady=5)

        self.race_option = ctk.CTkOptionMenu(self, values=["Загрузка..."])
        self.race_option.pack(pady=5)

        self.class_option = ctk.CTkOptionMenu(self, values=["Загрузка..."])
        self.class_option.pack(pady=5)

        self.stat_entries = {}
        self.create_stats_section()

        ctk.CTkLabel(self, text="Заклинания").pack(pady=5)
        self.spell_listbox = ctk.CTkTextbox(self, height=100)
        self.spell_listbox.pack(pady=5)

        self.add_spell_button = ctk.CTkButton(self, text="Добавить заклинание", command=self.add_spell)
        self.add_spell_button.pack(pady=3)

        self.remove_spell_button = ctk.CTkButton(self, text="Удалить последнее заклинание", command=self.remove_last_spell)
        self.remove_spell_button.pack(pady=3)

        self.load_button = ctk.CTkButton(self, text="Загрузить персонажа", command=self.load_character)
        self.load_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self, text="Сохранить персонажа", command=self.save_character)
        self.save_button.pack(pady=10)

        self.load_reference_data()

    def create_stats_section(self):
        stat_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat in stat_names:
            entry = ctk.CTkEntry(self, placeholder_text=stat.capitalize())
            entry.pack(pady=2)
            self.stat_entries[stat] = entry

    def load_reference_data(self):
        self.cursor.execute("SELECT Name FROM Race")
        races = [row[0] for row in self.cursor.fetchall()]
        self.race_option.configure(values=races or ["Нет данных"])

        self.cursor.execute("SELECT Name FROM Class")
        classes = [row[0] for row in self.cursor.fetchall()]
        self.class_option.configure(values=classes or ["Нет данных"])
        
        self.cursor.execute("SELECT Name FROM Spells")
        self.spell_names = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT Description FROM Spells")
        self.spell_descs = [row[0] for row in self.cursor.fetchall()]

    def load_character(self):
        file_path = fd.askopenfilename(filetypes=[("JSON файлы", "*.json")])
        if not file_path:
            return
        with open(file_path, 'r', encoding='utf-8') as f:
            self.character_data = json.load(f)

        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, self.character_data.get("name", ""))

        self.level_entry.delete(0, 'end')
        self.level_entry.insert(0, str(self.character_data.get("level", 1)))

        self.race_option.set(self.character_data.get("race", ""))
        self.class_option.set(self.character_data.get("class", ""))

        for stat, entry in self.stat_entries.items():
            entry.delete(0, 'end')
            entry.insert(0, str(self.character_data.get("stats", {}).get(stat, 0)))

        self.spell_listbox.delete("0.0", "end")
        for spell in self.character_data.get("spells", []):
            self.spell_listbox.insert("end", f"{spell}\n")

    def save_character(self):
        try:
            self.character_data["name"] = self.name_entry.get()
            self.character_data["level"] = int(self.level_entry.get())
            self.character_data["race"] = self.race_option.get()
            self.character_data["class"] = self.class_option.get()
            self.character_data["stats"] = {
                stat: int(entry.get()) for stat, entry in self.stat_entries.items()
            }

            spells = self.spell_listbox.get("0.0", "end").strip().split("\n")
            self.character_data["spells"] = [s for s in spells if s.strip()]

            file_path = fd.asksaveasfilename(defaultextension=".json", filetypes=[("JSON файлы", "*.json")])
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.character_data, f, indent=4, ensure_ascii=False)
                mb.showinfo("Успех", "Персонаж сохранён!")
        except Exception as e:
            mb.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def add_spell(self):
        if not self.spell_names:
            mb.showwarning("Нет заклинаний", "В базе нет заклинаний.")
            return
        spell_list = ctk.CTkToplevel()
        spell_list.title("Список заклинаний")
        spell_list.geometry("300x400")
        spell_listbox = ctk.CTkTextbox(spell_list, height=300)
        spell_listbox.pack(pady=10)
        spell_list.scrollbar = ctk.CTkScrollbar(self, command=self.textbox.yview)
        spell_list.scrollbar.grid(row=0, column=1)
        for spell in self.spell_names:
            spell_listbox.insert("end", f"{spell}\n")


        spell = sd.askstring("Добавить заклинание", f"Введите название (пример: {self.spell_names[0]})")
        if spell in self.spell_names:
            self.spell_listbox.insert("end", f"{spell}\n")
        elif spell:
            mb.showwarning("Не найдено", "Такого заклинания нет в базе.")

    def remove_last_spell(self):
        content = self.spell_listbox.get("0.0", "end").strip().split("\n")
        if content:
            self.spell_listbox.delete("0.0", "end")
            for line in content[:-1]:
                self.spell_listbox.insert("end", f"{line}\n")


app = CharacterSheetApp()
app.mainloop()
