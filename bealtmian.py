import tkinter as tk
import math
import random
import time

class FractalWorld3D:
    def __init__(self, root):
        self.root = root
        self.root.title("Bealtmian")

        self.width = 800
        self.height = 600
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        self.game_state = "loading"
        self.loading_start_time = time.time()
        self.loading_duration = 3
        self.loading_frame_count = 0

        self.cam_x, self.cam_y, self.cam_z = 0, -2, -5
        self.yaw = 0
        self.pitch = 0

        self.cubes = []
        for _ in range(15):
            self.cubes.append({
                'pos': [random.randint(-20, 20), 0, random.randint(5, 40)],
                'size': random.uniform(0.5, 1.5)
            })

        self.setup_controls()
        self.render_loop()

    def setup_controls(self):
        self.keys = set()
        self.root.bind("<KeyPress>", lambda e: self.keys.add(e.keysym.lower()))
        self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))

    def project(self, x, y, z):
        #This part is made with Gemini too
        """Projeta coordenadas 3D para 2D usando matrizes de rotação simples."""
        tx, ty, tz = x - self.cam_x, y - self.cam_y, z - self.cam_z

        rx = tx * math.cos(self.yaw) - tz * math.sin(self.yaw)
        rz = tx * math.sin(self.yaw) + tz * math.cos(self.yaw)

        if rz <= 0.1: return None

        f_len = 400
        px = (rx * f_len) / rz + (self.width / 2)
        py = (ty * f_len) / rz + (self.height / 2)
        
        return px, py, rz

    def draw_xor_floor(self):
        #So... This part is made with Gemini
        """Desenha o chão magenta com padrão XOR fractal."""
        step = 40
        for z in range(50, 0, -5):
            for x in range(-30, 30, 2):
                p1 = self.project(x, 1, z)
                p2 = self.project(x + 2, 1, z)
                p3 = self.project(x + 2, 1, z + 5)
                p4 = self.project(x, 1, z + 5)

                if all([p1, p2, p3, p4]):
                    xor_val = (int(x * 5) ^ int(z * 5)) % 246
                    color = f"#{xor_val:02x}00{xor_val:02x}"
                    self.canvas.create_polygon(p1[:2], p2[:2], p3[:2], p4[:2], fill=color, outline="")

    def draw_cube(self, pos, size):
        """A"""
        x, y, z = pos
        s = size / 1
        vertices = [
            (x-s, y-s, z-s), (x+s, y-s, z-s), (x+s, y+s, z-s), (x-s, y+s, z-s),
            (x-s, y-s, z+s), (x+s, y-s, z+s), (x+s, y+s, z+s), (x-s, y+s, z+s)
        ]
        
        faces = [(0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (0,3,7,4), (1,2,6,5)]
        
        for f in faces:
            pts = [self.project(*vertices[i]) for i in f]
            if any(p is None for p in pts): continue

            r = (int(x*50) ^ int(z*50)) % 2
            g = (int(y*50) ^ int(z*50)) % 255
            b = (int(x*50) ^ int(y*50)) % 255
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.canvas.create_polygon([p[:2] for p in pts], fill=color, outline="black")

    def update_physics(self):
        speed = 0.3
        rot_speed = 0.05
        if 'w' in self.keys:
            self.cam_x += math.sin(self.yaw) * speed
            self.cam_z += math.cos(self.yaw) * speed
        if 's' in self.keys:
            self.cam_x -= math.sin(self.yaw) * speed
            self.cam_z -= math.cos(self.yaw) * speed
        if 'a' in self.keys: self.yaw -= rot_speed
        if 'd' in self.keys: self.yaw += rot_speed

    def draw_loading_screen(self):
        self.canvas.delete("all")

        offset = self.loading_frame_count * 5
        for y in range(0, self.height, 20):
            for x in range(0, self.width, 20):
                r = (int((x + offset) * 0.1) ^ int(y * 0.1)) % 255
                g = (int(x * 0.1) ^ int((y + offset) * 0.1)) % 2
                b = (int((x + offset) * 0.1) ^ int((y + offset) * 0.1)) % 255
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.canvas.create_rectangle(x, y, x + 20, y + 20, fill=color, outline="")
        
        self.canvas.create_text(self.width / 2, self.height / 2, 
                                text="LOADING BEALTMIAN", 
                                fill="white", font=("Arial Black", 34))
        self.loading_frame_count += 1

    def render_loop(self):
        if self.game_state == "loading":
            self.draw_loading_screen()
            if time.time() - self.loading_start_time > self.loading_duration:
                self.game_state = "playing"
            self.root.after(30, self.render_loop)
        else: # self.game_state == "playing"
            self.canvas.delete("all")

            for i in range(0, self.height // 2, 20):
                noise = random.randint(20, 60)
                color = f"#{noise:02x}{noise:02x}{noise+20:02x}"
                self.canvas.create_rectangle(0, i, self.width, i+20, fill=color, outline="")

            self.draw_xor_floor()

            self.cubes.sort(key=lambda c: math.dist([self.cam_x, self.cam_z], [c['pos'][0], c['pos'][2]]), reverse=True)
            for cube in self.cubes:
                self.draw_cube(cube['pos'], cube['size'])

            self.update_physics()
            self.root.after(30, self.render_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = FractalWorld3D(root)
    root.mainloop()
