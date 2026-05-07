def main():  
  import tkinter as tk
  import ast,os
  from tkinter import messagebox, simpledialog

  gtmpout = None

  DB_PATH = os.path.join(os.path.expanduser("~"), "mangomgr_db.txt")

  # --- DATABASE FUNCTIONS ---

  def writefile(data):
      try:
          with open(DB_PATH, "w", encoding="utf-8") as f:
              f.write(repr(data))
      except Exception as e:
          messagebox.showerror("Write Error", f"Failed to Write: {e}")

  def readfile():
      try:
          with open(DB_PATH, "r", encoding="utf-8") as f:
              content = f.read().strip()
          if not content:
              return {}
          return ast.literal_eval(content)
      except Exception:
          writefile({})
          return {}

  # --- CORE ACTIONS ---

  def action(task):
      pydb = readfile()
      
      if task == "repo":
          name = simpledialog.askstring("New Repository", "Enter Repository Name:", parent=root)
          if name:
              if name in pydb:
                  messagebox.showerror("Error", "Repository Already Exists!")
              else:
                  pydb[name] = []
                  writefile(pydb)
                  messagebox.showinfo("Success", f"Repository \"{name}\" Created Successfully.")

      elif task == "commit":
          reposelect("single")
          name = gtmpout
          if name and name in pydb:
              gettext(f"Commit to {name}")
              code = gtmpout
              if code:
                  pydb[name].append(code)
                  writefile(pydb)
                  messagebox.showinfo("Success", "Commit Saved!")
          elif name:
              messagebox.showerror("Error", "Repository Not Found.")

      elif task == "delete":
        reposelect("multiple")
        if not gtmpout:return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete those repositories? This action cannot be undone."):return
        for _ in gtmpout:
          del pydb[_]
        writefile(pydb)
        messagebox.showwarning("Success", "Deleted Successfully.")

  # --- IMPROVED HISTORY VIEWER ---

  def showrepo(repo_name):
      pydb = readfile()
      if repo_name not in pydb:
          messagebox.showerror("Error", "Repository Not Found.")
          return

      history = pydb[repo_name]
      if not history:
          messagebox.showinfo("Empty", "No Commits Found in This Repository.")
          return

      # Use Toplevel (Proper popup)
      popup = tk.Toplevel(root)
      popup.geometry("600x650")
      popup.title(f"{repo_name}")
      popup.config(bg="#1C2A35")

      # Use a dict for state to avoid 'global' headaches
      state = {"index": 0}

      # Header
      ver_label = tk.Label(popup, text=f"Version 1 / {len(history)}", font=("Consolas", 14, "bold"), bg="#1C2A35", fg="#4A6D89")
      ver_label.pack(pady=10)

      # Text Area with Scrollbar
      frame = tk.Frame(popup, bg="#1C2A35")
      frame.pack(expand=True, fill="both", padx=20)
      
      scrollbar = tk.Scrollbar(frame)
      scrollbar.pack(side="right", fill="y")

      text_box = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, bg="#0D1117", fg="#C9D1D9", font=("Consolas", 11), padx=10, pady=10)
      text_box.pack(side="left", expand=True, fill="both")
      scrollbar.config(command=text_box.yview)

      def update_view():
          idx = state["index"]
          ver_label.config(text=f"Version {idx + 1} / {len(history)}")
          text_box.config(state="normal")
          text_box.delete("1.0", "end")
          text_box.insert("1.0", history[idx])
          text_box.config(state="disabled")

      def move(direction, e=None):
          if direction == "next" and state["index"] < len(history) - 1:
              state["index"] += 1
          elif direction == "prev" and state["index"] > 0:
              state["index"] -= 1
          update_view()

      # Footer Controls
      ctrl_frame = tk.Frame(popup, bg="#1C2A35")
      ctrl_frame.pack(pady=20)
      
      tk.Button(ctrl_frame, text="← Previous", command=lambda: move("prev"), bg="#30363D", fg="white", width=12).pack(side="left", padx=10)
      tk.Button(ctrl_frame, text="Next →", command=lambda: move("next"), bg="#30363D", fg="white", width=12).pack(side="left", padx=10)

      # Binds
      popup.bind("<Left>", lambda e: move("prev"))
      popup.bind("<Right>", lambda e: move("next"))

      update_view()


  def gettext(a):
      global gtmpout
      gtmpout = None
      def finish():
          global gtmpout
          gtmpout = text_box.get("1.0", "end").strip()
          t.destroy()
      t = tk.Toplevel(root)
      t.geometry("600x600")
      t.title(a)
      t.config(bg="#1C2A35")

      frame = tk.Frame(t, bg="#1C2A35")
      frame.pack(expand=True, fill="both", padx=20)
      
      scrollbar = tk.Scrollbar(frame)
      scrollbar.pack(side="right", fill="y")

      text_box = tk.Text(frame, width=45, height=22, wrap="word", yscrollcommand=scrollbar.set, bg="#0D1117", fg="#C9D1D9", font=("Consolas", 11), padx=10, pady=10, insertbackground="white")
      text_box.pack(side="left", expand=True, fill="both")
      scrollbar.config(command=text_box.yview)
      

      submitbtn = tk.Button(t, text="Submit", **btn_style, command=finish)
      submitbtn.pack(pady=10)
      root.wait_window(t)



  def reposelect(i):
      global gtmpout
      gtmpout = []
      pydb = readfile()
      items = list(pydb.keys())
      
      a = tk.Toplevel(root)
      a.geometry("600x600")
      a.title("Repository Selection")
      a.config(bg="#1C2A35")
      
      frame = tk.Frame(a, bg="#1C2A35")
      frame.pack(expand=True, fill="both", padx=20)
      
      scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
      
      lb = tk.Listbox(frame, bg="black", fg="white", font=("Arial", 14), 
                      selectbackground="#010054", selectforeground="#85E5F7", 
                      yscrollcommand=scrollbar.set,
                      selectmode=tk.SINGLE if i == "single" else tk.MULTIPLE)
      
      scrollbar.config(command=lb.yview)
      
      scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
      lb.pack(side=tk.LEFT, expand=True, fill="both")

      for item in items:
          lb.insert(tk.END, item)

      def finish():
          global gtmpout
          gtmpout = [lb.get(idx) for idx in lb.curselection()] if i == "multiple" else (lb.get(lb.curselection()[0]) if lb.curselection() else "")
          a.destroy()

      submitbtn = tk.Button(a, text="Submit", **btn_style, command=finish)
      submitbtn.pack(pady=10)

      root.wait_window(a)


  # --- MAIN UI ---

  def buttonreposelect(a):
    reposelect(a)
    return gtmpout

  root = tk.Tk()
  root.geometry("400x500")
  root.title("Mango - Your Code Manager")
  root.config(bg="#0D1117")

  tk.Label(root, text="MANGO", font=("Consolas", 24, "bold"), bg="#0D1117", fg="#FFAC1C").pack(pady=30)

  btn_style = {"bg": "#21262D", "fg": "#C9D1D9", "relief": "flat", "width": 20, "font": ("Arial", 10, "bold"), "pady": 5}

  tk.Button(root, text="New Repository", command=lambda: action("repo"), **btn_style).pack(pady=10)
  tk.Button(root, text="Commit", command=lambda: action("commit"), **btn_style).pack(pady=10)
  tk.Button(root, text="View Repositories", command=lambda:(repo := buttonreposelect("single")) and showrepo(repo), **btn_style).pack(pady=10)
  tk.Button(root, text="Delete", command=lambda: action("delete"), bg="#8E1515", fg="white", relief="flat", width=20).pack(pady=40)

  root.mainloop()

if __name__ == '__main__':
  main()

# when importing you need to use libname.main() to start otherwise it'll run on its own