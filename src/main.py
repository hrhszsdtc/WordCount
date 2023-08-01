# -*- coding: utf-8 -*-

import contextlib
import functools
import io
import multiprocessing
import os
import re
import signal
import sys
import tkinter as tk
from collections import Counter
from tkinter import filedialog, messagebox, ttk

import dill
import easyocr
import fitz
import pandas as pd
from tabulate import tabulate

import log


def parse_pdf(file):
    with fitz.open(file) as doc:
        text = ""
        for page in doc.pages():
            text += page.get_text()
        if text:
            return text
        else:
            return


queue = multiprocessing.Queue()


def parse_img_inner(f, queue):
    reader = easyocr.Reader(["en"])
    try:
        result = reader.readtext(f)
        text = ""
        for result in result:
            text += result[1] + " "
        queue.put(text)
        return text
    except KeyboardInterrupt as ke:
        messagebox.showinfo("任务已取消", str(ke))
        log.info(f"取消任务:{ke}")
        return
    except Exception as e:
        messagebox.showerror("错误", str(e))
        log.warning(f"错误:{e}")
        return


def parse_img(f):
    p = multiprocessing.Process(target=parse_img_inner, args=(f, queue), kwargs=None)
    p.start()
    p.join()
    details = queue.get()
    if details is not None:
        return details.split()


supported_output_formats = {
    "Excel": ["excel", ".xlsx"],
    "Markdown": ["github", ".md"],
    "HTML": ["html", ".html"],
    "Word": ["presto", ".docx"],
    "Txt": ["pretty", ".txt"],
}


class SingletonTabToNormal(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class TabToNormal(metaclass=SingletonTabToNormal):
    def __init__(self):
        self.file_path = tk.StringVar()
        self.file_path.choose_file = self.file_path

    def select_file(self):
        self.file_path.choose_file.set(filedialog.askopenfilename())
        return self.file_path.get()

    def to_new(self, model, word):
        chosen_value_list = supported_output_formats.get(model)
        chosen_value = chosen_value_list[0]
        counts = Counter(word)
        items = counts.most_common()
        filetypes = [(model, chosen_value_list[1])]
        filename = filedialog.asksaveasfilename(
            filetypes=filetypes, defaultextension=chosen_value_list[1]
        )
        if filename:
            if chosen_value == "excel":
                tab = tabulate(items, headers=["Word", "Count"], tablefmt="github")
                self.table_to_excel(tab, filename)
            else:
                tab = tabulate(items, headers=["Word", "Count"], tablefmt=chosen_value)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(tab)

    def table_to_excel(self, table, filename):
        new_tab = self.table_to_new(table)
        df = pd.DataFrame(
            {"Word": [row[0] for row in new_tab], "Count": [row[1] for row in new_tab]}
        )
        df.to_excel(filename + ".xlsx", sheet_name="Sheet1", header=None, index=False)

    def table_to_new(self, table):
        table_list = table.splitlines()
        table_list = [line.split("|") for line in table_list]
        table_list = [list(filter(None, line)) for line in table_list]
        table_list = table_list[2:]
        return table_list


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
        self.combobox["values"] = list(supported_output_formats.keys())
        self.combobox.current(0)
        self.combobox.grid(row=1, column=1, sticky="e")
        self.button = ttk.Button(self, text="导出", command=self.button_command)
        self.button.grid(row=1, column=2, sticky="w")

    def button_command(self):
        mode = self.combobox.get()
        if self.words:
            TabToNormal().to_new(mode, self.words)
        else:
            return

    def count_word(self, file):
        self.text.delete(0.0, tk.END)
        try:
            with open(file, "r", encoding="utf-8") as f:
                filename, extension = os.path.splitext(f.name)
                if extension in [".pdf", ".xps", ".oxps", ".cbz", ".fb2", ".epub"]:
                    content = parse_pdf(f)
                elif extension in [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".bmp",
                    ".tiff",
                    ".tif",
                    ".tga",
                    ".icb",
                    ".vda",
                    ".vst",
                    ".dcm",
                    ".dcm30",
                ]:
                    content = parse_img(f)
                else:
                    content = f.read()
            try:
                text = content.lower()
                text = re.sub(r"[^A-Za-z\\'-]", " ", text)
                self.words = re.findall(r"\b\w+(?:-\w+)*\b", text)
                counts = Counter(self.words)
                items = counts.most_common()
                table = tabulate(items, headers=["Word", "Count"], tablefmt="pretty")
                sys.stdout.write(table)
                messagebox.showinfo("成功", "已成功统计")
            except Exception as e:
                messagebox.showerror("失败", f"发生错误:{e}")
                log.critical(f"内部错误:{e}")
        except FileNotFoundError as fe:
            messagebox.showwarning("警告", "请选择一个正确的文件")
            log.debug(f"{fe}: 文件{file}未找到")
        except Exception as e:
            messagebox.showerror("失败", f"发生错误:{e}")
            log.error(f"{e}")


class PrintToText:
    def __init__(self, text):
        self.text = text

    def write(self, s):
        self.text.insert(tk.END, s)
        self.text.see(tk.END)
        self.text.update()


if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(master=root)
    gui.words = None
    ptt = PrintToText(gui.text)
    with contextlib.redirect_stdout(ptt), contextlib.redirect_stderr(ptt):
        gui.master.mainloop()
