import pygame
import networkx as nx
import random
import math
import numpy as np
from queue import PriorityQueue
import time
import sys
import time
import pygame
import draw
class PopupManager:
    def __init__(self, font, screen, duration=3, bg_color=(255, 255, 0), text_color=(0, 0, 0)):
        self.font = font
        self.screen = screen
        self.duration = duration
        self.bg_color = bg_color
        self.text_color = text_color
        self.messages = []  # 存放多個 (message, start_time)

    def show(self, message):
        self.messages.append((message, time.time()))

    def update(self):
        current_time = time.time()
        self.messages = [
            (msg, start) for msg, start in self.messages
            if current_time - start < self.duration
        ]

    def draw(self):
        if not self.messages:
            return

        screen_width = self.screen.get_width()
        popup_width = screen_width // 2
        popup_height = 40
        padding = 10
        popup_y = 20

        for idx, (message, _) in enumerate(self.messages):
            y = popup_y + idx * (popup_height + padding)
            popup_x = (screen_width - popup_width) // 2

            pygame.draw.rect(self.screen, self.bg_color, (popup_x, y, popup_width, popup_height))
            pygame.draw.rect(self.screen, (0, 0, 0), (popup_x, y, popup_width, popup_height), 2)

            text_surf = self.font.render(message, True, self.text_color)
            text_rect = text_surf.get_rect(center=(screen_width // 2, y + popup_height // 2))
            self.screen.blit(text_surf, text_rect)

class Checkbox:
    def __init__(self, x, y, size, label, font, checked=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.font = font
        self.checked = checked

    def update_position(self, x, y, size):
        self.rect.update(x, y, size, size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.rect.collidepoint(mx, my):
                self.checked = not self.checked

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, (0, 0, 0),
                             (self.rect.left + 3, self.rect.centery),
                             (self.rect.centerx, self.rect.bottom - 3), 2)
            pygame.draw.line(screen, (0, 0, 0),
                             (self.rect.centerx, self.rect.bottom - 3),
                             (self.rect.right - 3, self.rect.top + 3), 2)
        label_surface = self.font.render(self.label, True, (0, 0, 0))
        screen.blit(label_surface, (self.rect.right + 5, self.rect.top))

class Slider:
    def __init__(self, x, y, width, height, font, label, value=0.0, color=(255, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.label = label
        self.value = value
        self.color = color
        self.dragging = False

    def update_position(self, x, y, width, height):
        self.rect.update(x, y, width, height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.rect.collidepoint(mx, my):
                self.dragging = True
                self.set_value_from_pos(mx)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx, _ = event.pos
                self.set_value_from_pos(mx)

    def set_value_from_pos(self, mx):
        relative_x = mx - self.rect.x
        self.value = max(0.0, min(relative_x / self.rect.width, 1.0))

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.rect)
        pygame.draw.rect(screen, self.color,
                         (self.rect.x, self.rect.y, int(self.value * self.rect.width), self.rect.height))
        text_surface = self.font.render(f"{self.label}: {self.value:.2f}", True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.right + 10, self.rect.y + 5))

class TextInput:
    def __init__(self, x, y, width, height, font, label="", default_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.label = label
        self.text = default_text
        self.active = False
        self.cursor_pos = len(default_text)
        self.cursor_visible = True
        self.cursor_timer = 0

    def update_position(self, x, y, width, height):
        self.rect.update(x, y, width, height)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            else:
                # event.unicode 可能是空字串，所以用 event.key 判斷
                if (event.unicode and event.unicode.isdigit()) or (pygame.K_KP0 <= event.key <= pygame.K_KP9):
                    char = event.unicode if event.unicode else chr(event.key - pygame.K_KP0 + ord('0'))
                    self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                    self.cursor_pos += 1

    def Update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        # 背景與邊框
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        # 標籤
        if self.label:
            label_surface = self.font.render(self.label, True, (0, 0, 0))
            screen.blit(label_surface, (self.rect.x, self.rect.y - self.font.get_height() - 5))

        # 文字
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + (self.rect.height - self.font.get_height()) // 2))

        # 游標
        if self.active and self.cursor_visible:
            cursor_x = self.font.size(self.text[:self.cursor_pos])[0]
            cursor_y = self.rect.y + (self.rect.height - self.font.get_height()) // 2
            pygame.draw.line(screen, (0, 0, 0),
                             (self.rect.x + 5 + cursor_x, cursor_y),
                             (self.rect.x + 5 + cursor_x, cursor_y + self.font.get_height()), 2)

    def get_value(self):
        try:
            return int(self.text)
        except ValueError:
            return 0




def scaled_pos(pos_dict, width, height, margin=100):
    new_pos = {}
    for node, (x, y) in pos_dict.items():
        sx = margin + x * (width - 2 * margin)
        sy = margin + y * (height - 2 * margin)
        new_pos[node] = (sx, sy)
    return new_pos

def draw_graph(pos):
    screen.fill(WHITE)

    # 畫邊（連線）
    for u, v in G.edges():
        # 先算放大縮小和平移後的座標
        x1 = pos[u][0] * zoom + offset[0]
        y1 = pos[u][1] * zoom + offset[1]
        x2 = pos[v][0] * zoom + offset[0]
        y2 = pos[v][1] * zoom + offset[1]
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)

    # 畫節點
    for node in G.nodes():
        x = pos[node][0] * zoom + offset[0]
        y = pos[node][1] * zoom + offset[1]

        if G.nodes[node].get('dead', False):
            color = BLACK 
        elif G.nodes[node].get('infected', False):
            color = RED
        else:
            color = GREEN

        radius = max(3, int(8 * zoom))  # 節點大小隨 zoom 變化
        pygame.draw.circle(screen, color, (int(x), int(y)), radius)
        pos_for_click[node] = (x, y)

def get_node_at_pos(mouse_pos, pos):
    for node, (x, y) in pos.items():
        if math.hypot(mouse_pos[0] - x, mouse_pos[1] - y) < 10:
            return node
    return None

def draw_info_panel(node, day, zoom):
    base_width = 350
    scale = zoom
    panel_width = int(base_width * scale)
    margin = int(10 * scale)
    font_size = max(12, int(18 * scale))
    info_font = pygame.font.SysFont("arial", font_size)
    line_height = font_size + 5

    lines = [f"Day {day}"]

    if node is not None:
        node_data = G.nodes[node]
        if not node_data.get('dead', False):
            status = "infected" if node_data.get('infected', False) else "healthy"
            if node_data.get('developing_cure', False) and not node_data.get('cure_completed', False):
                status += f", developing cure ({node_data.get('cure_progress', 0):.2f}%)"
            elif node_data.get('cure_completed', False):
                status += ", cure completed"
        else:
            status = "dead"
        lines.append(f"City {node_data['name']}: {status}")

        neighbors = list(G.neighbors(node))
        lines.append("Neighbors:")
        max_neighbors_display = 5
        for i, neighbor in enumerate(neighbors[:max_neighbors_display]):
            lines.append(f"  {G.nodes[neighbor]['name']}")
        if len(neighbors) > max_neighbors_display:
            lines.append(f"  ... and {len(neighbors) - max_neighbors_display} more")

    panel_height = int(len(lines) * line_height + 2 * margin)

    panel_x = WIDTH - panel_width - margin
    panel_y = margin

    s = pygame.Surface((panel_width, panel_height))
    s.set_alpha(180)
    s.fill((220, 220, 220))
    screen.blit(s, (panel_x, panel_y))

    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), max(1, int(2 * scale)))

    # 顯示文字
    for i, text in enumerate(lines):
        line_surf = info_font.render(text, True, BLACK)
        screen.blit(line_surf, (panel_x + margin, panel_y + margin + i * line_height))

def draw_speed_buttons(font, current_speed):
    for btn in speed_buttons:
        color = (200, 200, 200) if btn["scale"] != current_speed else (150, 200, 255)
        pygame.draw.rect(screen, color, btn["rect"])
        pygame.draw.rect(screen, (0, 0, 0), btn["rect"], 2)

        label_surface = font.render(btn["label"], True, (0, 0, 0))
        label_rect = label_surface.get_rect(center=btn["rect"].center)
        screen.blit(label_surface, label_rect)

def draw_virus_attributes_panel(A, B, fatality,use_mutation):
    panel_width, panel_height = 200, 110
    panel_x, panel_y = 10, 10

    s = pygame.Surface((panel_width, panel_height))
    s.set_alpha(180)
    s.fill((230, 230, 230))
    screen.blit(s, (panel_x, panel_y))

    # 邊框
    pygame.draw.rect(screen, (0, 0, 0), (panel_x, panel_y, panel_width, panel_height), 2)

    # 文字顯示
    a_text = font.render(f"空氣感染力: {A:.2f}", True, (0, 0, 0))
    b_text = font.render(f"水域感染力: {B:.2f}", True, (0, 0, 0))
    c_text = font.render(f"致死率: {fatality:.2f}", True, (0, 0, 0))
    mutation_text = font.render(f"突變: {'是' if use_mutation else '否'}", True, (0, 0, 0))
    
    screen.blit(a_text, (panel_x + 10, panel_y + 10))
    screen.blit(b_text, (panel_x + 10, panel_y + 35))
    screen.blit(c_text, (panel_x + 10, panel_y + 60))
    screen.blit(mutation_text, (panel_x + 10, panel_y + 85))

def setting_screen():
    selecting = True

    checkbox_size_ratio = 0.05
    bar_width_ratio = 0.6
    bar_height_ratio = 0.04
    checkbox_y_ratio = 0.2
    spacing_ratio = 0.17
    slider_spacing = 100  # 固定像素間距

    air_checkbox = Checkbox(0, 0, 0, "空氣恐懼", font)
    water_checkbox = Checkbox(0, 0, 0, "水域恐懼", font)
    mutation_checkbox = Checkbox(0, 0, 0, "病毒變異", font)
    cure_checkbox = Checkbox(0, 0, 0, "研製解藥", font)
    
    infection_input = TextInput(0, 0, 0, 0, font, "每日最多感染數", "3")
    cure_input = TextInput(0, 0, 0, 0, font, "每日最多治癒數", "3")

    slider_mutation = Slider(0, 0, 0, 0, font, "突變機率", color=(255, 165, 0))
    slider_air = Slider(0, 0, 0, 0, font, "空氣感染力", color=(255, 0, 0))
    slider_water = Slider(0, 0, 0, 0, font, "水域感染力", color=(0, 0, 255))
    slider_fatality = Slider(0, 0, 0, 0, font, "致死率", color=(0, 0, 0))
    slider_cure_chance = Slider(0, 0, 0, 0, font, "開始研發機率", color=(0, 128, 0))
    slider_cure_speed = Slider(0, 0, 0, 0, font, "單日研究成功機率", color=(128, 0, 128))

    while selecting:
        screen.fill((240, 240, 240))
        window_width, window_height = screen.get_size()

        margin = int(window_width * 0.05)
        bar_width = int(window_width * bar_width_ratio)
        bar_height = int(window_height * bar_height_ratio)
        checkbox_size = int(window_height * checkbox_size_ratio)
        checkbox_y = int(window_height * checkbox_y_ratio)
        spacing = int(window_width * spacing_ratio)
        slider_y = checkbox_y + checkbox_size + 20

        # 更新 Checkbox 位置
        air_checkbox.update_position(margin, checkbox_y, checkbox_size)
        water_checkbox.update_position(margin + spacing, checkbox_y, checkbox_size)
        mutation_checkbox.update_position(margin + spacing * 2, checkbox_y, checkbox_size)
        cure_checkbox.update_position(margin + spacing * 3, checkbox_y, checkbox_size)
        
        infection_input.update_position(margin + spacing * 4, checkbox_y, 100 ,30)
        # 更新 Sliders 位置
        current_y = slider_y

        slider_fatality.update_position(margin, current_y, bar_width, bar_height)
        current_y += slider_spacing

        if not air_checkbox.checked:
            slider_air.update_position(margin, current_y, bar_width, bar_height)
            current_y += slider_spacing

        # water 未勾選才顯示
        if not water_checkbox.checked:
            slider_water.update_position(margin, current_y, bar_width, bar_height)
            current_y += slider_spacing

        # mutation 有勾才顯示
        if mutation_checkbox.checked:
            slider_mutation.update_position(margin, current_y, bar_width, bar_height)
            current_y += slider_spacing

        # cure 有勾才顯示
        if cure_checkbox.checked:
            slider_cure_chance.update_position(margin, current_y, bar_width, bar_height)
            current_y += slider_spacing

            slider_cure_speed.update_position(margin, current_y, bar_width, bar_height)
            current_y += slider_spacing
            
            cure_input.update_position(margin + spacing * 5, checkbox_y,100 ,30)

        

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    selecting = False

            # TextInput 優先處理事件
            infection_input.handle_event(event)
            if cure_checkbox.checked:
                cure_input.handle_event(event)

            # 處理互斥 checkbox
            air_checkbox.handle_event(event)
            if air_checkbox.checked:
                water_checkbox.checked = False

            water_checkbox.handle_event(event)
            if water_checkbox.checked:
                air_checkbox.checked = False

            mutation_checkbox.handle_event(event)
            cure_checkbox.handle_event(event)

            # Slider
            if not air_checkbox.checked:
                slider_air.handle_event(event)
            if not water_checkbox.checked:
                slider_water.handle_event(event)

            slider_fatality.handle_event(event)

            if mutation_checkbox.checked:
                slider_mutation.handle_event(event)

            if cure_checkbox.checked:
                slider_cure_chance.handle_event(event)
                slider_cure_speed.handle_event(event)

        air_checkbox.draw(screen)
        water_checkbox.draw(screen)
        mutation_checkbox.draw(screen)
        cure_checkbox.draw(screen)
        infection_input.Update()
        infection_input.draw(screen)

        if not air_checkbox.checked:
            slider_air.draw(screen)
        if not water_checkbox.checked:
            slider_water.draw(screen)

        slider_fatality.draw(screen)

        if mutation_checkbox.checked:
            slider_mutation.draw(screen)

        if cure_checkbox.checked:
            slider_cure_chance.draw(screen)
            slider_cure_speed.draw(screen)
            cure_input.Update()
            cure_input.draw(screen)

        title = font_big.render("請調整屬性，按 Enter 開始", True, (0, 0, 0))
        title_rect = title.get_rect(center=(window_width // 2, int(window_height * 0.1)))
        screen.blit(title, title_rect)

        pygame.display.flip()
        clock.tick(60)


    return (
        slider_air.value, slider_water.value, slider_fatality.value,
        mutation_checkbox.checked, water_checkbox.checked, air_checkbox.checked,
        cure_checkbox.checked, slider_cure_chance.value, slider_cure_speed.value, infection_input.get_value(), cure_input.get_value()
    )

def select_start_node_screen(G, pos, dragging, last_mouse_pos, zoom, offset):
    selected_node = None
    selecting = True

    while selecting:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
            # 按下滑鼠左鍵開始拖曳
                if event.button == 1: # 左鍵
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 3:  # 右鍵
                    clicked_node = get_node_at_pos(event.pos, pos_for_click)
                    if clicked_node is not None:
                        if selected_node is not None:
                            G.nodes[selected_node]['infected'] = False
                        selected_node = clicked_node
                        G.nodes[selected_node]['infected'] = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and selected_node is not None:
                    selecting = False
                    infected_nodes.add(selected_node)
            elif event.type == pygame.MOUSEBUTTONUP:# 放開左鍵停止拖曳
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    dy = mouse_pos[1] - last_mouse_pos[1]
                    offset[0] += dx
                    offset[1] += dy
                    last_mouse_pos = mouse_pos
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom *= 1.1
                else:
                    zoom /= 1.1

        draw_graph(pos)
        msg = font.render("用右鍵點選節點，再按 Enter 確認", True, BLACK)
        screen.blit(msg, (20, 20))
        
        pygame.display.flip()
        clock.tick(60)

    return selected_node

def heuristic(u, v):
            pu, pv = original_pos[u], original_pos[v]
            dist = ((pu[0] - pv[0]) ** 2 + (pu[1] - pv[1]) ** 2) ** 0.5
            return 1.0 / (1.0 + dist)  # 距離越近，感染機率越高

def infect_neighbors(G, infected_nodes, A, B, fatality, heuristic, max_new_infections_per_day):
    new_infections = 0
    to_remove = set()

    for node in list(infected_nodes):
        if random.random() < fatality:
            G.nodes[node]['dead'] = True
            G.nodes[node]['infected'] = False
            to_remove.add(node)
    infected_nodes.difference_update(to_remove)

    uninfected = [
        node for node in G.nodes
        if not G.nodes[node].get('infected', False)
        and not G.nodes[node].get('dead', False)
        and not G.nodes[node].get('cure_completed', False)
    ]

    candidates = []
    for target in uninfected:
        total_score = 0
        for source in infected_nodes:
            if G.has_edge(source, target):
                w1 = G[source][target].get('w1', 1)
                w2 = G[source][target].get('w2', 1)
                weight = A * w1 + B * w2
                total_score += heuristic(source, target) * weight
        if total_score > 0:
            candidates.append((total_score, target))

    while new_infections < max_new_infections_per_day and candidates:
        total = sum(score for score, _ in candidates)
        r = random.uniform(0, total)
        acc = 0
        for i, (score, node) in enumerate(candidates):
            acc += score
            if acc >= r:
                G.nodes[node]['infected'] = True
                infected_nodes.add(node)
                new_infections += 1
                candidates.pop(i)  # 避免重複感染
                break

    return new_infections

    
def maybe_mutate(air, water, fatality, water_fear, air_fear, mutation_chance=0.1, mutation_strength=0.5):
    if random.random() < mutation_chance / 10:
        water_fear = not water_fear
    if random.random() < mutation_chance / 10:
        air_fear = not air_fear

    if not air_fear:
        if random.random() < mutation_chance:
            delta = random.uniform(-mutation_strength, mutation_strength)
            air = max(0.0, min(1.0, air + delta))
            popup.show(f"突變發生！ 空氣感染力調整為 {air:.2f}")
    if not water_fear:
        if random.random() < mutation_chance:
            delta = random.uniform(-mutation_strength, mutation_strength)
            water = max(0.0, min(1.0, water + delta))
            popup.show(f"突變發生！ 水域感染力調整為 {water:.2f}")
    if random.random() < mutation_chance:
            delta = random.uniform(-mutation_strength, mutation_strength)
            fatality = max(0.0, min(1.0, fatality + delta))
            popup.show(f"突變發生！ 致死率調整為 {fatality:.2f}")
    return air, water, fatality, water_fear, air_fear

def check_game_over(G):
    # 條件1：全部死掉
    if all(G.nodes[node].get('dead', False) for node in G.nodes):
        return 1
    # 條件2：有感染點，但沒有可以感染的鄰居
    alive_nodes = [n for n in G.nodes if not G.nodes[n].get('dead', False)]

    infected_nodes = [n for n in alive_nodes if G.nodes[n].get('infected', False)]
    healthy_nodes = [n for n in alive_nodes if not G.nodes[n].get('infected', False)]
    # 如果沒有感染的節點，遊戲結束
    if not infected_nodes:
        return 3
    if not healthy_nodes:
        return 0

    # 對每個感染中的節點檢查：是否有「還活著且未感染」的鄰居
    for node in infected_nodes:
        for neighbor in G.neighbors(node):
            neighbor_data = G.nodes[neighbor]
            if not neighbor_data.get('dead', False):
                return 0  # 還能擴散，不算結束

    return 2

def show_game_over_screen(end):
    screen.fill((30, 30, 30))
    
    title_font = pygame.font.SysFont("Microsoft JhengHei", 48)
    button_font = pygame.font.SysFont("Microsoft JhengHei", 32)
    if end == 1:
        title = title_font.render("全部城市死亡，你獲勝了！", True, WHITE)
    elif end == 2:
        title = title_font.render("遊戲結束！你失敗了！", True, WHITE)
    elif end == 3:
        title = title_font.render("遊戲結束！沒有感染點了！", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))

    # 按鈕設定
    restart_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2, 100, 50)
    quit_btn = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2, 100, 50)

    pygame.draw.rect(screen, (0, 200, 0), restart_btn)
    pygame.draw.rect(screen, (200, 0, 0), quit_btn)

    restart_text = button_font.render("重來", True, BLACK)
    quit_text = button_font.render("退出", True, BLACK)

    screen.blit(restart_text, (restart_btn.x + 15, restart_btn.y + 10))
    screen.blit(quit_text, (quit_btn.x + 15, quit_btn.y + 10))

    pygame.display.flip()

    # 等待玩家選擇
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if restart_btn.collidepoint(mx, my):
                    return "restart"
                elif quit_btn.collidepoint(mx, my):
                    pygame.quit()
                    exit()

def start_cure_development(G, probability=0.1):
    for node in G.nodes:
        node_data = G.nodes[node]
        if not node_data.get('dead', False) and not node_data.get('developing_cure', False) and not node_data.get('cure_completed', False):
            if random.random() < probability:
                node_data['developing_cure'] = True
                node_data['cure_progress'] = 0
                node_data['cure_completed'] = False
                popup.show(f"節點 {node} 開始研發解藥！")

def update_cure_development(G, daily_cure_progress=0.3, cure_threshold=1.0):
    for node in G.nodes:
        node_data = G.nodes[node]
        # 節點活著且正在開發解藥
        if not node_data.get('dead', False) and node_data.get('developing_cure', False):
            # 增加進度
            if random.random() < daily_cure_progress:
                node_data['cure_progress'] = node_data.get('cure_progress', 0) + random.random()

            if node_data['cure_progress'] >= cure_threshold:
                node_data['cure_progress'] = cure_threshold  # 避免超過
                node_data['cure_completed'] = True  # 代表完成解藥
                node_data['developing_cure'] = False
                popup.show(f"節點 {node} 解藥研發完成！")
                node_data['infected'] = False  # 完成解藥後，節點不再感染

def spread_cure(G, A, B, heuristic, max_new_cures_per_day):
    new_cures = 0
    cured_nodes = [n for n in G.nodes if G.nodes[n].get('cure_completed', False)]
    for source in cured_nodes:
        if new_cures >= max_new_cures_per_day:
            break

        candidates = []
        for neighbor in G.neighbors(source):
            if not G.nodes[neighbor].get('infected', False) and not G.nodes[neighbor].get('dead', False) and not G.nodes[neighbor].get('cure_completed', False):
                w1 = G[source][neighbor].get('w1', 1)
                w2 = G[source][neighbor].get('w2', 1)
                weight = A * w1
                score = heuristic(source, neighbor) * weight
                candidates.append((score, neighbor))

        if candidates:
            total = sum(score for score, _ in candidates)
            if total > 0:
                r = random.uniform(0, total)
                acc = 0
                for score, node in candidates:
                    acc += score
                    if acc >= r:
                        G.nodes[node]['infected'] = False
                        new_cures += 1
                        break

# 主迴圈
pygame.init()
pygame.display.set_caption("瘟疫模擬器")
font = pygame.font.SysFont("Microsoft JhengHei", 20)  # 微軟正黑體
font_big = pygame.font.SysFont("Microsoft JhengHei", 36)
#random.seed(21)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
speed_buttons = [
    {"label": "Pause", "rect": pygame.Rect(30, HEIGHT - 50, 60, 30), "scale": 0.0},
    {"label": "1x",    "rect": pygame.Rect(100, HEIGHT - 50, 60, 30), "scale": 1.0},
    {"label": "2x",    "rect": pygame.Rect(170, HEIGHT - 50, 60, 30), "scale": 2.0},
    {"label": "3x",    "rect": pygame.Rect(240, HEIGHT - 50, 60, 30), "scale": 3.0},
]

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)
while True:
    clock = pygame.time.Clock()
    zoom = 1.0
    time_scale = 1.0
    offset = [WIDTH // 2, HEIGHT // 2]
    dragging = False
    last_mouse_pos = None
    day = 0
    day_timer = 0  # 計時用
    pos_for_click = {}
    result = ""
    popup = PopupManager(font, screen)

    num_nodes = random.randint(10, 100)
    G = nx.connected_watts_strogatz_graph(n=num_nodes, k=4, p=0.3, seed=42)
    original_pos = nx.spring_layout(G, seed=42, k=2 / np.sqrt(len(G.nodes)), scale=1.0)
    for node in G.nodes:
        G.nodes[node]['name'] = f"{node}"
        G.nodes[node]['infected'] = False
        G.nodes[node]['dead'] = False
        G.nodes[node]['developing_cure'] = False
        G.nodes[node]['cure_progress'] = 0.0
        G.nodes[node]['cure_completed'] = False
    for u, v in G.edges():
        G[u][v]['w1'] = random.randint(1, 100)
        G[u][v]['w2'] = random.randint(1, 100)
    infected_nodes = set()

    selected_node = None
    pos = scaled_pos(original_pos, WIDTH, HEIGHT)
    air, water, fatality, use_mutation, water_fear, air_fear, cure, cure_chance, cure_speed, max_new_infections_per_day, max_new_cures_per_day= setting_screen()# 載入選單讓使用者調整病毒屬性
    select_start_node_screen(G, pos, dragging, last_mouse_pos, zoom, offset)  # 選擇起始感染節點
    running = True

    while running:
        popup.update()
        dt = clock.tick(60)
        if not check_game_over(G) == 0:
            result = show_game_over_screen(check_game_over(G))
            if result == "restart":
                running = False
                
        dt = clock.tick(60)
        day_timer += dt * time_scale
        if day_timer >= 2000:
            day += 1
            day_timer -= 2000
            if use_mutation:
                air, water, fatality, water_fear, air_fear = maybe_mutate(air, water, water_fear, air_fear, 0.2)
            infect_neighbors(G, infected_nodes, air, water, fatality, heuristic, max_new_infections_per_day)
            if cure:
                start_cure_development(G, cure_chance)  # 20% 機率開始研發
                update_cure_development(G, cure_speed, cure_threshold=1.0)
                spread_cure(G, air, water, heuristic, max_new_cures_per_day)

        pos = scaled_pos(original_pos, WIDTH, HEIGHT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                for i, btn in enumerate(speed_buttons):
                    btn["rect"].y = HEIGHT - 50
                    btn["rect"].x = 100 + i * 70

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 按下滑鼠左鍵開始拖曳
                if event.button == 1: # 左鍵
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
                    for btn in speed_buttons:
                        if btn["rect"].collidepoint(event.pos):
                            time_scale = btn["scale"]
                            popup.show(f"速度調整為 {btn['label']}")
                elif event.button == 3:  # 右鍵
                    node = get_node_at_pos(event.pos, pos_for_click)
                    if node is not None:
                        selected_node = node

            elif event.type == pygame.MOUSEBUTTONUP:# 放開左鍵停止拖曳
                if event.button == 1:
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    dy = mouse_pos[1] - last_mouse_pos[1]
                    offset[0] += dx
                    offset[1] += dy
                    last_mouse_pos = mouse_pos

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom *= 1.1
                else:
                    zoom /= 1.1

        draw_graph(pos)
        draw_info_panel(selected_node,day, zoom)
        draw_virus_attributes_panel(air, water, fatality,use_mutation)
        draw_speed_buttons(font, time_scale)

        popup.draw()

        pygame.display.flip()
    
