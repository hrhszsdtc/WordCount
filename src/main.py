# -*- coding: utf-8 -*-

import contextlib
import fitz
import io
import os
import pandas as pd
import re
import sys
import tkinter as tk
from tkinter import filedialog, ttk
from collections import Counter
from tabulate import tabulate


def parsePDF(file):
    with fitz.open(file) as doc:
        text = ""
        for page in doc.pages():
            text += page.get_text()
        if text:
            return text
        else:
            return -1


supported_output_format = {
    "Excel": ["excel", ".xlsx"],
    "Markdown": ["github", ".md"],
    "HTML": ["html", ".html"],
    "Word": ["presto", ".docx"],
    "Txt": ["pretty", ".txt"],
}


class TabToNormal:
    def __init__(self):
        self.file_path = tk.StringVar()
        self.file_path.choose_file = self.file_path

    def select_file(self):
        self.file_path.choose_file.set(filedialog.askopenfilename())
        return self.file_path.get()

    def to_new(self, model, word):
        chosen_value_list = supported_output_format.get(model)
        chosen_value = chosen_value_list[0]
        counts = Counter(word)
        items = counts.most_common()
        if chosen_value == "excel":
            tab = tabulate(items, headers=["Word", "Count"], tablefmt="github")
            self.table_to_excel(tab)
        else:
            tab = tabulate(items, headers=["Word", "Count"], tablefmt=chosen_value)
            suffix = chosen_value_list[1]
            with open("output" + suffix, "w", encoding="utf-8") as f:
                f.write(tab)

    def table_to_excel(self, table):
        new_tab = self.table_to_new(table)
        df = pd.DataFrame(
            {"Word": [row[0] for row in new_tab], "Count": [row[1] for row in new_tab]}
        )
        df.to_excel("output.xlsx", sheet_name="Sheet1", header=None, index=False)

    def table_to_new(self, table):
        table_list = table.splitlines()
        table_list = [line.split("|") for line in table_list]
        table_list = [list(filter(None, line)) for line in table_list]
        table_list = table_list[2:]
        return table_list


words = None


class GUI(ttk.Frame, TabToNormal):
    def __init__(self, master=None):
        super().__init__(master)
        TabToNormal.__init__(self)
        self.master = master
        self.master.title("英文词频统计")
        scriptpath = os.path.abspath(__file__)
        scriptdir = os.path.dirname(scriptpath)
        imagepath = os.path.join(scriptdir, "icon.png")
        img = tk.PhotoImage(file=imagepath)
        self.master.call("wm", "iconphoto", self.master._w, img)
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.sub_frame = ttk.Frame(self)
        self.text = tk.Text(self.sub_frame)
        self.scroll = ttk.Scrollbar(self.sub_frame)
        self.text.config(yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)
        self.text.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid(row=0, column=1, sticky="ns")
        self.sub_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.button_file = ttk.Button(
            self, text="浏览", command=lambda: self.count_word(self.select_file())
        )
        self.button_file.grid(row=1, column=0)
        self.combobox = ttk.Combobox(self, state="readonly")
        self.combobox["values"] = list(supported_output_format.keys())
        self.combobox.current(0)
        self.combobox.grid(row=1, column=1, sticky="e")
        self.button = ttk.Button(self, text="导出", command=self.button_command)
        self.button.grid(row=1, column=2, sticky="w")

    def button_command(self):
        mode = self.combobox.get()
        global words
        if words:
            self.to_new(mode, words)
        else:
            return

    def count_word(self, file):
        self.text.delete(0.0, tk.END)
        try:
            with open(file, "r", encoding="utf-8") as f:
                filename, extension = os.path.splitext(f.name)
                if extension in [".pdf", ".xps", ".oxps", ".cbz", ".fb2", ".epub"]:
                    content = parsePDF(f)
                else:
                    content = f.read()
            try:
                text = content.lower()
                text = re.sub(r"[^A-Za-z\\'-]", " ", text)
                global words
                words = re.findall(r"\b\w+(?:-\w+)*\b", text)
                counts = Counter(words)
                items = counts.most_common()
                table = tabulate(items, headers=["Word", "Count"], tablefmt="pretty")
                sys.stdout.write(table)
                return words
            except Exception as e:
                sys.stderr.write(f"内部错误:{e}")
        except FileNotFoundError as fe:
            sys.stderr.write(f"{fe}: 文件{file}未找到")
        except Exception as e:
            sys.stderr.write(f"{e}")


class PrintToText:
    def __init__(self, text):
        self.text = text

    def write(self, s):
        self.text.insert(tk.END, s)
        self.text.see(tk.END)
        self.text.update()


def start_gui():
    root = tk.Tk()
    gui = GUI(master=root)
    ptt = PrintToText(gui.text)
    with contextlib.redirect_stdout(ptt), contextlib.redirect_stderr(ptt):
        gui.master.mainloop()


start_gui()
