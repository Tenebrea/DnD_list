import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import json
import sqlite3
import re
from random import *

from Get_params import Settings as s

set = s()


class CharacterSheetApp(ctk.CTk, s):
    def __init__(self):
        super().__init__()

        self.title("D&D 2024 Character Sheet")
        self.geometry("800x700")
        self.resizable(False, False)
        self.configure(fg_color=set.fg_color)

        self.db_connection = sqlite3.connect(set.db_path)
        self.cursor = self.db_connection.cursor()

        self.character_data = {}

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Имя персонажа", text_color=set.font_color,
                                       fg_color=set.ent_color, placeholder_text_color=set.font_color)
        self.name_entry.place(x = 10, y = 10)

        self.level_entry = ctk.CTkEntry(self, placeholder_text="Уровень", text_color=set.font_color,
                                        fg_color=set.ent_color, placeholder_text_color=set.font_color, width = 80)
        self.level_entry.place(x = 170, y = 10)

        self.race_option = ctk.CTkOptionMenu(self, values=["Загрузка..."], text_color=set.font_color,
                                             fg_color=set.btn_color)
        self.race_option.place(x = 10, y = 50)

        self.class_option = ctk.CTkOptionMenu(self, values=["Загрузка..."], text_color=set.font_color,
                                              fg_color=set.btn_color)
        self.class_option.place(x = 10, y = 80)

        self.stat_entries = {}
        self.create_stats_section()

        ctk.CTkLabel(self, text="Заклинания", text_color=set.font_color).place(x = 230, y = 50)
        self.spell_listbox = ctk.CTkTextbox(self, height=100, text_color=set.font_color, fg_color=set.ent_color)
        self.spell_listbox.place(x = 170, y = 80)

        self.add_spell_button = ctk.CTkButton(self, text="Добавить заклинание", command=self.add_spell,
                                              text_color=set.font_color, fg_color=set.btn_color)
        self.add_spell_button.place(x = 190, y = 190)

        self.remove_spell_button = ctk.CTkButton(self, text="Удалить последнее заклинание",
                                                 command=self.remove_last_spell, text_color=set.font_color,
                                                 fg_color=set.btn_color)
        self.remove_spell_button.place(x = 165, y = 220)

        self.load_button = ctk.CTkButton(self, text="Загрузить персонажа", command=self.load_character,
                                         text_color=set.font_color, fg_color=set.btn_color)
        self.load_button.place(x = 190, y = 250)

        self.save_button = ctk.CTkButton(self, text="Сохранить персонажа", command=self.save_character,
                                         text_color=set.font_color, fg_color=set.btn_color)
        self.save_button.place(x = 190, y = 280)

        self.roll_label = ctk.CTkLabel(self, text_color=set.font_color, text = "")
        self.roll_label.place(x = 450, y = 310)

        self.roll_button = ctk.CTkButton(self, text="Бросить куб", command=self.dice_roll, text_color=set.font_color,
                                         fg_color=set.btn_color)
        self.roll_button.place(x = 300, y = 340)

        self.roll_entry = ctk.CTkEntry(self, placeholder_text="Введите выражение для броска", text_color=set.font_color,
                                       fg_color=set.ent_color, placeholder_text_color=set.font_color)
        self.roll_entry.place(x = 300, y = 310)

        self.load_reference_data()

    def create_stats_section(self, x = 260, y = 10):
        stat_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for stat in stat_names:
            entry = ctk.CTkEntry(self, placeholder_text=stat.capitalize(), text_color=set.font_color,
                                 fg_color=set.ent_color, placeholder_text_color=set.font_color, width = 80)
            entry.place(x = x, y = y)
            self.stat_entries[stat] = entry
            x+=90

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
        spell_list.geometry("600x600")
        scrollable_frame = ctk.CTkScrollableFrame(spell_list, 980, 580)
        scrollable_frame.pack(pady=10, padx=10)

        for spell in range(len(self.spell_names) - 1):
            b = ctk.CTkButton(scrollable_frame, 40, 20, text=self.spell_names[spell],
                              command=lambda num=spell: self.spell_listbox.insert("end", f"{self.spell_names[num]}\n"))
            b.pack(pady=10, padx=10)
            l = ctk.CTkLabel(scrollable_frame, width=10, text=self.spell_descs[spell], wraplength=400)
            l.pack(fill="both", pady=10, padx=10, expand=True)

    def remove_last_spell(self):
        content = self.spell_listbox.get("0.0", "end").strip().split("\n")
        if content:
            self.spell_listbox.delete("0.0", "end")
            for line in content[:-1]:
                self.spell_listbox.insert("end", f"{line}\n")

    def dice_roll(self, result=0, start=1):
        roll = self.roll_entry.get()

        roll = roll.replace(" ", "")
        a1 = re.split(r"[+\-/*]", roll)
        a2 = re.findall(r"[+\-*/]", roll)
        try:
            if re.match(r"[0-9]+?d[0-9]+?", a1[0]):
                for i in range(int(a1[0].split("d")[0])):
                    result += randint(1, int(a1[0].split("d")[1]))
            elif re.match(r"[0-9]+?", a1[0]):
                result += int(a1[0])
            else:
                result = "error"
        except TypeError:
            self.roll_label.configure(text=result)
            return

        for i in a2:
            match i:
                case "+":
                    if re.match(r"[0-9]+?d[0-9]+?", a1[start]):
                        for _ in range(int(a1[start].split("d")[0])):
                            result += randint(1, int(a1[start].split("d")[1]))
                    elif re.match(r"[0-9]+?", a1[start]):
                        result += int(a1[start])
                    else:
                        self.roll_label.configure(text=result)
                        return

                case "-":
                    if re.match(r"[0-9]+?d[0-9]+?", a1[start]):
                        for _ in range(int(a1[start].split("d")[0])):
                            result -= randint(1, int(a1[start].split("d")[1]))
                    elif re.match(r"[0-9]+?", a1[start]):
                        try: result -= int(a1[start])
                        except TypeError:
                            self.roll_label.configure(text=result)
                            return
                    else:
                        self.roll_label.configure(text=result)
                        return

                case "/":
                    if re.match(r"[0-9]+?d[0-9]+?", i):
                        for _ in range(int(a1[start].split("d")[0])):
                            result //= randint(1, int(a1[start].split("d")[1]))
                    elif re.match(r"[0-9]+?", a1[start]):
                        result //= int(a1[start])
                    else:
                        self.roll_label.configure(text=result)
                        return

                case "*":
                    if re.match(r"[0-9]+?d[0-9]+?", i):
                        for _ in range(int(a1[start].split("d")[0])):
                            result *= randint(1, int(a1[start].split("d")[1]))
                    elif re.match(r"[0-9]+?", a1[start]):
                        result *= int(a1[start])
                    else:
                        self.roll_label.configure(text=result)
                        return
            start += 1
        self.roll_label.configure(text=result)


app = CharacterSheetApp()
app.mainloop()
