import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class NQueenSolver:
    def __init__(self, N, initial_queens=None):
        self.N = N
        self.cols = set()
        self.diag1 = set()
        self.diag2 = set()
        self.queens = [-1] * N
        self.initial_queens = initial_queens if initial_queens else []
        if self.initial_queens:
            for (r, c) in self.initial_queens:
                self.place_queen(r, c)

    def place_queen(self, r, c):
        self.queens[r] = c
        self.cols.add(c)
        self.diag1.add(r - c)
        self.diag2.add(r + c)

    def remove_queen(self, r, c):
        self.queens[r] = -1
        self.cols.remove(c)
        self.diag1.remove(r - c)
        self.diag2.remove(r + c)

    def is_safe(self, r, c):
        return c not in self.cols and (r - c) not in self.diag1 and (r + c) not in self.diag2

    def solve_generator(self, row=0):
        while row < self.N and self.queens[row] != -1:
            row += 1
        if row == self.N:
            yield ("solution", self.queens[:])
            return
        for col in range(self.N):
            if self.is_safe(row, col):
                self.place_queen(row, col)
                yield ("place", row, col)
                yield from self.solve_generator(row + 1)
                self.remove_queen(row, col)
                yield ("remove", row, col)

class NQueenGUI:
    def __init__(self, root):
        self.root = root
        root.title("♛ N-Queens Visualizer - Chess Style ♛")
        self.size_var = tk.IntVar(value=8)

        # Top Controls
        control = tk.Frame(root, pady=10)
        control.pack()
        tk.Label(control, text="Board Size:", font=("Helvetica", 12)).pack(side=tk.LEFT)
        tk.Spinbox(control, from_=4, to=16, textvariable=self.size_var, width=5).pack(side=tk.LEFT)
        tk.Button(control, text="Start Solving", command=self.start_solver, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        self.next_button = tk.Button(control, text="Next Solution", command=self.next_solution, state=tk.DISABLED, bg="#008CBA", fg="white")
        self.next_button.pack(side=tk.LEFT)
        tk.Button(control, text="Reset", command=self.reset_board, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)
        self.status_label = tk.Label(control, text="Solutions: 0", font=("Helvetica", 11, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=10)

        # Instruction
        tk.Label(root, text="Click to manually place queen. Then click Start.", fg="gray").pack()

        # Canvas
        self.canvas = tk.Canvas(root, bd=0, highlightthickness=0)
        self.canvas.pack(pady=10)

        # History
        self.history_listbox = tk.Listbox(root, height=6, font=("Consolas", 10))
        self.history_listbox.pack(fill=tk.X, padx=30)

        # Load Image
        self.queen_img = self.load_queen_image()

        self.queen_items = {}
        self.solver = None
        self.solver_gen = None
        self.solution_counter = 0
        self.step_delay = 200
        self.N = self.size_var.get()
        self.draw_board(self.N)

    def load_queen_image(self):
        if os.path.exists("queen.png"):
            img = Image.open("queen.png").resize((40, 40), Image.ANTIALIAS)
            return ImageTk.PhotoImage(img)
        return None

    def draw_board(self, N):
        self.canvas.delete("all")
        self.N = N
        self.cell_size = 60
        self.canvas.config(width=N * self.cell_size, height=N * self.cell_size)
        self.queen_items.clear()
        for r in range(N):
            for c in range(N):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                color = "#f0d9b5" if (r + c) % 2 == 0 else "#b58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", tags=f"cell{r}_{c}")
                self.canvas.tag_bind(f"cell{r}_{c}", "<Button-1>", lambda e, rr=r, cc=c: self.on_cell_click(rr, cc))

    def on_cell_click(self, r, c):
        if (r, c) in self.queen_items:
            self.canvas.delete(self.queen_items[(r, c)])
            del self.queen_items[(r, c)]
        else:
            if self.is_manual_safe(r, c):
                x, y = c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2
                if self.queen_img:
                    self.queen_items[(r, c)] = self.canvas.create_image(x, y, image=self.queen_img)
                else:
                    self.queen_items[(r, c)] = self.canvas.create_text(x, y, text="♛", font=("Arial", 24), fill="blue")

    def is_manual_safe(self, r, c):
        for (qr, qc) in self.queen_items.keys():
            if qr == r or qc == c or (qr - qc) == (r - c) or (qr + qc) == (r + c):
                return False
        return True

    def start_solver(self):
        N = self.size_var.get()
        if self.N != N:
            self.draw_board(N)

        initial = list(self.queen_items.keys())
        self.solver = NQueenSolver(N, initial_queens=initial)
        self.solver_gen = self.solver.solve_generator()
        self.next_button.config(state=tk.DISABLED)
        self.solution_counter = 0
        self.status_label.config(text="Solutions: 0")
        self.history_listbox.delete(0, tk.END)
        self.animate_step()

    def animate_step(self):
        try:
            event = next(self.solver_gen)
        except StopIteration:
            if self.solution_counter == 0:
                messagebox.showinfo("No Solution", "No solution is possible with current board setup.")
            else:
                messagebox.showinfo("Done", "No more solutions possible.")
            self.next_button.config(state=tk.DISABLED)
            return

        action = event[0]
        if action == "place":
            _, r, c = event
            x, y = c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2
            if self.queen_img:
                self.queen_items[(r, c)] = self.canvas.create_image(x, y, image=self.queen_img)
            else:
                self.queen_items[(r, c)] = self.canvas.create_text(x, y, text="♛", font=("Arial", 24), fill="black")
        elif action == "remove":
            _, r, c = event
            if (r, c) in self.queen_items:
                self.canvas.delete(self.queen_items[(r, c)])
                del self.queen_items[(r, c)]
        elif action == "solution":
            self.solution_counter += 1
            self.status_label.config(text=f"Solutions: {self.solution_counter}")
            self.history_listbox.insert(tk.END, f"{self.solution_counter}: {event[1]}")
            self.next_button.config(state=tk.NORMAL)
            return

        self.root.after(self.step_delay, self.animate_step)

    def next_solution(self):
        self.next_button.config(state=tk.DISABLED)
        self.animate_step()

    def reset_board(self):
        self.draw_board(self.size_var.get())
        self.history_listbox.delete(0, tk.END)
        self.status_label.config(text="Solutions: 0")
        self.next_button.config(state=tk.DISABLED)
        self.queen_items.clear()

if __name__ == "__main__":
    root = tk.Tk()
    app = NQueenGUI(root)
    root.mainloop()
