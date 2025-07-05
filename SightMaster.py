# SightMaster 


import tkinter as tk
from tkinter import messagebox

GRID_SIZE = 31
PIXEL_SIZE = 20
CENTER = GRID_SIZE // 2

class SightMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SightMaster")
        self.root.configure(bg='black')

        self.canvas = tk.Canvas(root, width=GRID_SIZE * PIXEL_SIZE, height=GRID_SIZE * PIXEL_SIZE, bg="black")
        self.canvas.pack()

        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.history = []
        self.symmetry_mode = False

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Control-z>", self.undo)
        self.root.bind("s", self.toggle_symmetry)
        self.root.bind("<Left>", lambda e: self.move_cursor(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_cursor(1, 0))
        self.root.bind("<Up>", lambda e: self.move_cursor(0, -1))
        self.root.bind("<Down>", lambda e: self.move_cursor(0, 1))

        self.cursor_x = CENTER
        self.cursor_y = CENTER

        self.code_box = tk.Entry(self.root, width=80, bg='black', fg='lime')
        self.code_box.pack(pady=10)

        self.ratio_label = tk.Label(self.root, text="", fg='white', bg='black')
        self.ratio_label.pack(pady=2)

        self.status_label = tk.Label(self.root, text="Click pixels to draw your crosshair", fg='white', bg='black')
        self.status_label.pack(pady=5)

        self.symmetry_label = tk.Label(self.root, text="Symmetry: OFF", fg='gray', bg='black')
        self.symmetry_label.pack()

        export_btn = tk.Button(self.root, text="Export & Copy Crosshair Code", command=self.export_code, bg='#222', fg='lime', padx=10)
        export_btn.pack(pady=5)

        self.draw_grid()
        self.update_code_display()

    def toggle_symmetry(self, event=None):
        self.symmetry_mode = not self.symmetry_mode
        self.symmetry_label.config(text=f"Symmetry: {'ON' if self.symmetry_mode else 'OFF'}", fg='lime' if self.symmetry_mode else 'gray')

    def move_cursor(self, dx, dy):
        new_x = self.cursor_x + dx
        new_y = self.cursor_y + dy
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            self.cursor_x = new_x
            self.cursor_y = new_y
            self.toggle_pixel(new_x, new_y)

    def toggle_pixel(self, x, y):
        self.history.append([row[:] for row in self.grid])
        self.grid[y][x] ^= 1
        if self.symmetry_mode:
            sx, sy = CENTER * 2 - x, CENTER * 2 - y
            if 0 <= sx < GRID_SIZE and 0 <= sy < GRID_SIZE:
                self.grid[sy][sx] ^= 1
        self.draw_grid()
        self.update_code_display()

    def on_click(self, event):
        x = event.x // PIXEL_SIZE
        y = event.y // PIXEL_SIZE
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.cursor_x, self.cursor_y = x, y
            self.toggle_pixel(x, y)

    def undo(self, event=None):
        if self.history:
            self.grid = self.history.pop()
            self.draw_grid()
            self.update_code_display()

    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if x == CENTER and y == CENTER:
                    if self.grid[y][x]:
                        self.canvas.create_oval(
                            x * PIXEL_SIZE + 4, y * PIXEL_SIZE + 4,
                            (x + 1) * PIXEL_SIZE - 4, (y + 1) * PIXEL_SIZE - 4,
                            fill="#00ff88", outline="#00ff88"
                        )
                        continue
                    else:
                        color = "#440000"
                else:
                    color = "#00ff88" if self.grid[y][x] else "#111"

                self.canvas.create_rectangle(
                    x * PIXEL_SIZE, y * PIXEL_SIZE,
                    (x + 1) * PIXEL_SIZE, (y + 1) * PIXEL_SIZE,
                    fill=color, outline="#222"
                )

        self.canvas.create_rectangle(
            self.cursor_x * PIXEL_SIZE, self.cursor_y * PIXEL_SIZE,
            (self.cursor_x + 1) * PIXEL_SIZE, (self.cursor_y + 1) * PIXEL_SIZE,
            outline="yellow", width=2
        )

    def measure_line(self, axis):
        length = offset = thickness = 0

        if axis == 'horizontal':
            left_len = right_len = left_gap = right_gap = 0
            for dx in range(1, CENTER):
                if CENTER - dx >= 0 and not self.grid[CENTER][CENTER - dx]:
                    left_gap += 1
                else:
                    break
            for dx in range(1, GRID_SIZE - CENTER):
                if CENTER + dx < GRID_SIZE and not self.grid[CENTER][CENTER + dx]:
                    right_gap += 1
                else:
                    break
            min_gap = min(left_gap, right_gap)
            for dx in range(min_gap + 1, GRID_SIZE // 2):
                if CENTER + dx < GRID_SIZE and self.grid[CENTER][CENTER + dx]:
                    right_len += 1
                else:
                    break
            for dx in range(min_gap + 1, GRID_SIZE // 2):
                if CENTER - dx >= 0 and self.grid[CENTER][CENTER - dx]:
                    left_len += 1
                else:
                    break
            length = max(left_len, right_len)
            offset = min_gap
            for dy in range(-1, 2):
                if 0 <= CENTER + dy < GRID_SIZE and self.grid[CENTER + dy][CENTER + offset + 1]:
                    thickness += 1

        elif axis == 'vertical':
            up_len = down_len = up_gap = down_gap = 0
            for dy in range(1, CENTER):
                if CENTER - dy >= 0 and not self.grid[CENTER - dy][CENTER]:
                    up_gap += 1
                else:
                    break
            for dy in range(1, GRID_SIZE - CENTER):
                if CENTER + dy < GRID_SIZE and not self.grid[CENTER + dy][CENTER]:
                    down_gap += 1
                else:
                    break
            min_gap = min(up_gap, down_gap)
            for dy in range(min_gap + 1, GRID_SIZE // 2):
                if CENTER + dy < GRID_SIZE and self.grid[CENTER + dy][CENTER]:
                    down_len += 1
                else:
                    break
            for dy in range(min_gap + 1, GRID_SIZE // 2):
                if CENTER - dy >= 0 and self.grid[CENTER - dy][CENTER]:
                    up_len += 1
                else:
                    break
            length = max(up_len, down_len)
            offset = min_gap
            for dx in range(-1, 2):
                if 0 <= CENTER + dx < GRID_SIZE and self.grid[CENTER + offset + 1][CENTER + dx]:
                    thickness += 1

        return length, offset, max(1, thickness)

    def calculate_code(self):
        center_dot = self.grid[CENTER][CENTER] == 1

        h_len, h_offset, h_thick = self.measure_line('horizontal')
        v_len, v_offset, v_thick = self.measure_line('vertical')

        final_offset = (h_offset + v_offset) // 2
        final_length = (h_len + v_len) // 2
        final_thick = (h_thick + v_thick) // 2

        ratio = f"H: Len={h_len}, Off={h_offset}, Thick={h_thick} | V: Len={v_len}, Off={v_offset}, Thick={v_thick}"
        self.ratio_label.config(text=f"Line Stats — {ratio}")

        code_parts = [
            "0",
            "s;1",
            "P",
            "c;5",
            "h;1",
            "o;1",
            "t;1",
            f"d;{int(center_dot)}",
            f"z;{3 if center_dot else 0}",
            "a;1",
            "f;0",
            "m;0",
            f"0b;1",
            f"0a;1",
            f"0l;{final_length}",
            f"0o;{final_offset}",
            f"0t;{final_thick}",
            "0f;0",
            "0m;0",
            "0s;1",
            "S;c;4;o;1;s;1"
        ]

        return ";".join(code_parts)

    def update_code_display(self):
        current_code = self.calculate_code()
        self.code_box.delete(0, tk.END)
        self.code_box.insert(0, current_code)

    def export_code(self):
        final_code = self.calculate_code()
        self.code_box.delete(0, tk.END)
        self.code_box.insert(0, final_code)
        self.root.clipboard_clear()
        self.root.clipboard_append(final_code)
        self.root.update()
        messagebox.showinfo("Copied", "Crosshair code copied to clipboard!")

if __name__ == '__main__':
    root = tk.Tk()
    app = SightMasterApp(root)
    root.mainloop()
