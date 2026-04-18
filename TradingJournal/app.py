import tkinter as tk
from tkinter import ttk
from engine import sync_trades, load_db, save_db


BG = "#0f1116"
CARD = "#1a1d24"
TEXT = "#e6e6e6"
ACCENT = "#3b82f6"
GREEN = "#22c55e"
RED = "#ef4444"


class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trade Journal")
        self.root.geometry("1400x800")
        self.root.configure(bg=BG)

        self.data = load_db()
        self.selected_trade = None

        self.build_ui()
        self.load_trade_list()

    # ---------------- UI ----------------
    def build_ui(self):
        # TOP BAR
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", pady=5)

        tk.Label(top, text="Trade Journal", fg=TEXT, bg=BG,
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=10)

        tk.Button(top, text="Sync Trades",
                  bg=ACCENT, fg="white",
                  command=self.sync).pack(side="right", padx=10)

        # MAIN
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        # LEFT PANEL
        self.left = tk.Frame(main, bg=CARD, width=320)
        self.left.pack(side="left", fill="y")

        self.canvas = tk.Canvas(self.left, bg=CARD, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.left, command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.list_frame = tk.Frame(self.canvas, bg=CARD)
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # RIGHT PANEL
        self.right = tk.Frame(main, bg=BG)
        self.right.pack(side="right", fill="both", expand=True, padx=10)

        self.title = tk.Label(self.right, text="", fg=TEXT, bg=BG,
                              font=("Segoe UI", 18, "bold"))
        self.title.pack(anchor="w", pady=10)

        self.pre = self.create_text("Pre-Trade Analysis")
        self.post = self.create_text("Post-Trade Review")

        self.rr = self.create_entry("Risk : Reward")
        self.emotions = self.create_text("Emotions")
        self.lessons = self.create_text("Lessons Learned")
        self.tags = self.create_entry("Tags")

        self.rating = tk.Scale(self.right, from_=1, to=10,
                               orient="horizontal", bg=BG, fg=TEXT,
                               highlightthickness=0)
        self.rating.pack(fill="x", pady=10)

        tk.Button(self.right, text="Save",
                  bg=ACCENT, fg="white",
                  command=self.save_trade).pack(pady=10)

    # ---------------- COMPONENTS ----------------
    def create_text(self, label):
        tk.Label(self.right, text=label, bg=BG, fg="#9aa4b2").pack(anchor="w")
        txt = tk.Text(self.right, height=3, bg=CARD, fg=TEXT, insertbackground="white")
        txt.pack(fill="x", pady=5)
        return txt

    def create_entry(self, label):
        tk.Label(self.right, text=label, bg=BG, fg="#9aa4b2").pack(anchor="w")
        entry = tk.Entry(self.right, bg=CARD, fg=TEXT, insertbackground="white")
        entry.pack(fill="x", pady=5)
        return entry

    # ---------------- TRADE LIST ----------------
    def load_trade_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for i, t in enumerate(self.data):
            self.create_trade_card(t, i)

    def create_trade_card(self, trade, index):
        frame = tk.Frame(self.list_frame, bg=CARD, padx=10, pady=8)
        frame.pack(fill="x", pady=5, padx=5)

        frame.bind("<Button-1>", lambda e, i=index: self.select_trade(i))

        # Symbol
        tk.Label(frame, text=trade["symbol"],
                 fg=TEXT, bg=CARD,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")

        # Profit
        pnl_color = GREEN if trade["profit"] > 0 else RED

        tk.Label(frame,
                 text=f"{round(trade['profit'],2)}",
                 fg=pnl_color,
                 bg=CARD).pack(anchor="w")

        # NEW badge
        if not trade["journal"]["pre_trade"]:
            tk.Label(frame, text="NEW", bg="#333", fg="white",
                     font=("Segoe UI", 8)).pack(anchor="e")

    # ---------------- SELECT ----------------
    def select_trade(self, index):
        self.selected_trade = self.data[index]
        t = self.selected_trade
        j = t["journal"]

        self.title.config(
            text=f"{t['symbol']} | {'WIN' if t['profit']>0 else 'LOSS'}"
        )

        self.fill_text(self.pre, j["pre_trade"])
        self.fill_text(self.post, j["post_trade"])
        self.fill_text(self.emotions, j["emotions"])
        self.fill_text(self.lessons, j["lessons"])

        self.rr.delete(0, tk.END)
        self.rr.insert(0, j["risk_reward"])

        self.tags.delete(0, tk.END)
        self.tags.insert(0, j["tags"])

        self.rating.set(j["rating"])

    def fill_text(self, widget, value):
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, value)

    # ---------------- SAVE ----------------
    def save_trade(self):
        if not self.selected_trade:
            return

        j = self.selected_trade["journal"]

        j["pre_trade"] = self.pre.get("1.0", tk.END).strip()
        j["post_trade"] = self.post.get("1.0", tk.END).strip()
        j["risk_reward"] = self.rr.get()
        j["emotions"] = self.emotions.get("1.0", tk.END).strip()
        j["lessons"] = self.lessons.get("1.0", tk.END).strip()
        j["tags"] = self.tags.get()
        j["rating"] = self.rating.get()

        save_db(self.data)
        self.load_trade_list()

    # ---------------- SYNC ----------------
    def sync(self):
        self.data = sync_trades()
        self.load_trade_list()


root = tk.Tk()
app = JournalApp(root)
root.mainloop()