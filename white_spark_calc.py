import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------------------
# Probability models for white skill spark generation
# ---------------------------------------------------------------------------
# Each model maps (category, lineage_count) -> probability that the skill
# generates as a white spark on the offspring.
#   category      : "white" (single circle), "double" (double circle), "gold"
#   lineage_count : how many ancestors carry that spark (0-6; max lineage is
#                   2 parents + 4 grandparents)

BASE = {"white": 0.20, "double": 0.25, "gold": 0.40}


def p_exponential(cat, n):
    # aoneko_pochi (2024): base_rate * 1.1^lineage_count. Fits all three (p >= 0.84).
    return BASE[cat] * (1.10 ** n)


def p_piecewise(cat, n):
    # Empirical piecewise-at-2: +first per copy for copies 1-2, +rest after.
    first = {"white": 0.02,   "double": 0.025,    "gold": 0.04}[cat]
    rest  = {"white": 0.0275, "double": 0.034375, "gold": 0.055}[cat]
    a = min(n, 2)
    b = max(0, n - 2)
    return BASE[cat] + first * a + rest * b


def p_community(cat, n):
    # Original community hypothesis: linear boost per copy.
    boost = {"white": 0.025, "double": 0.025, "gold": 0.05}[cat]
    return BASE[cat] + boost * n


MODELS = {
    "Exponential  base x 1.1^n  (recommended)": p_exponential,
    "Piecewise-at-2  (best empirical fit)":     p_piecewise,
    "Community linear  (reference)":            p_community,
}


def poisson_binomial(probs):
    """probs -> list where index k holds P(exactly k of the trials succeed)."""
    dist = [1.0]
    for p in probs:
        nxt = [0.0] * (len(dist) + 1)
        for k, v in enumerate(dist):
            nxt[k]     += v * (1 - p)
            nxt[k + 1] += v * p
        dist = nxt
    return dist


CATEGORIES = [("White (single)", "white"),
              ("Double circle", "double"),
              ("Gold", "gold")]
LABEL_TO_KEY = {label: key for label, key in CATEGORIES}
KEY_TO_LABEL = {key: label for label, key in CATEGORIES}


class Calc:
    def __init__(self, root):
        self.root = root
        root.title("White Spark Generation Calc")

        self.sparks = []   # each: {"name": str, "cat": key, "count": int}
        self.model_name = tk.StringVar(value=list(MODELS)[0])

        # --- input row -------------------------------------------------------
        inp = tk.Frame(root)
        inp.grid(row=0, column=0, sticky="w", padx=10, pady=8)

        tk.Label(inp, text="Skill").grid(row=0, column=0, padx=(0, 4))
        self.name_entry = tk.Entry(inp, width=22)
        self.name_entry.grid(row=0, column=1, padx=4)
        self.name_entry.bind("<Return>", lambda e: self.add_spark())

        tk.Label(inp, text="Type").grid(row=0, column=2, padx=4)
        self.cat_menu = ttk.Combobox(inp, width=13, state="readonly",
                                     values=[c[0] for c in CATEGORIES])
        self.cat_menu.current(0)
        self.cat_menu.grid(row=0, column=3, padx=4)

        tk.Label(inp, text="In lineage").grid(row=0, column=4, padx=4)
        self.count_var = tk.IntVar(value=1)
        tk.Spinbox(inp, from_=0, to=6, width=3,
                   textvariable=self.count_var).grid(row=0, column=5, padx=4)

        tk.Button(inp, text="Add Spark",
                  command=self.add_spark).grid(row=0, column=6, padx=6)

        # --- model selector --------------------------------------------------
        mf = tk.LabelFrame(root, text="Model")
        mf.grid(row=1, column=0, sticky="we", padx=10)
        for m in MODELS:
            tk.Radiobutton(mf, text=m, value=m, variable=self.model_name,
                           command=self.refresh).pack(anchor="w")

        # --- tracked spark list ---------------------------------------------
        self.list_frame = tk.LabelFrame(root, text="Tracked sparks")
        self.list_frame.grid(row=2, column=0, sticky="we", padx=10, pady=8)

        # --- results ---------------------------------------------------------
        self.result = tk.Label(root, justify="left", anchor="w",
                               font=("TkFixedFont", 10))
        self.result.grid(row=3, column=0, sticky="we", padx=10, pady=(0, 10))

        self.refresh()

    # ------------------------------------------------------------------ logic
    def add_spark(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        self.sparks.append({
            "name":  name,
            "cat":   LABEL_TO_KEY[self.cat_menu.get()],
            "count": int(self.count_var.get()),
        })
        self.name_entry.delete(0, tk.END)
        self.refresh()

    def remove_spark(self, idx):
        del self.sparks[idx]
        self.refresh()

    def refresh(self):
        model = MODELS[self.model_name.get()]

        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.sparks:
            tk.Label(self.list_frame, text="(none yet \u2014 add a skill above)",
                     fg="grey").grid(row=0, column=0, padx=6, pady=4)
            self.result.config(text="")
            return

        header = ("Skill", "Type", "Copies", "Generate %")
        for c, h in enumerate(header):
            tk.Label(self.list_frame, text=h, font=("TkDefaultFont", 9, "bold")
                     ).grid(row=0, column=c, sticky="w", padx=6)

        probs = []
        for i, s in enumerate(self.sparks):
            p = min(model(s["cat"], s["count"]), 1.0)
            probs.append(p)
            tk.Label(self.list_frame, text=s["name"]).grid(
                row=i + 1, column=0, sticky="w", padx=6)
            tk.Label(self.list_frame, text=KEY_TO_LABEL[s["cat"]]).grid(
                row=i + 1, column=1, sticky="w", padx=6)
            tk.Label(self.list_frame, text=str(s["count"])).grid(
                row=i + 1, column=2, padx=6)
            tk.Label(self.list_frame, text=f"{p * 100:.2f}%").grid(
                row=i + 1, column=3, sticky="w", padx=6)
            tk.Button(self.list_frame, text="x", width=2,
                      command=lambda idx=i: self.remove_spark(idx)).grid(
                row=i + 1, column=4, padx=6)

        self.update_results(probs)

    def update_results(self, probs):
        n = len(probs)
        dist = poisson_binomial(probs)
        expected = sum(probs)

        atleast = [0.0] * (n + 2)
        for k in range(n, -1, -1):
            atleast[k] = atleast[k + 1] + dist[k]

        lines = [f"Expected white sparks:  {expected:.2f}  (of {n} tracked)",
                 "",
                 "How many will actually generate:"]
        for k in range(n + 1):
            lines.append(
                f"  {k:>2}:  exactly {dist[k] * 100:6.2f}%"
                f"     at least {atleast[k] * 100:6.2f}%")
        self.result.config(text="\n".join(lines))


if __name__ == "__main__":
    root = tk.Tk()
    app = Calc(root)
    root.mainloop()
