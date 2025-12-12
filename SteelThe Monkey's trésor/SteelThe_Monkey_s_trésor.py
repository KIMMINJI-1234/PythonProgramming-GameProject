from tkinter import *
import pygame
import random
import time

STATE_TITLE = 0
STATE_PLAY = 1
STATE_GAME_OVER = 2

class SteelMonkeyGame:
    def __init__(self): #Tkinter 창 생성 
        self.window = Tk()
        self.window.title("SteelThe Monkey's trésor")
        self.window.geometry("1000x800")  # 창 크기 1000 x 800
        self.window.resizable(0, 0)

        self.keys = set()
        self.canvas = Canvas(self.window, bg="black")
        self.canvas.pack(expand=True, fill=BOTH)

        self.window.bind("<KeyPress>", self.keyPressHandler) 
        self.window.bind("<KeyRelease>", self.keyReleaseHandler)
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)

        # pygame 사운드 초기화
        pygame.mixer.init()

        self.snd_arrow = pygame.mixer.Sound("sound/arrow.wav")
        self.snd_player_hit = pygame.mixer.Sound("sound/playerdamage.wav")
        self.snd_rainbow = pygame.mixer.Sound("sound/banana_eat.wav")
        self.snd_gameover = pygame.mixer.Sound("sound/gameover.wav")
        self.snd_bgm = pygame.mixer.Sound("sound/backgroundsound.wav")

        # 이미지 파일
        self.img_bg = PhotoImage(file="image/gamebackground.png")
        self.img_player_right = PhotoImage(file="image/player_right.png")
        self.img_player_left = PhotoImage(file="image/player_left.png")
        self.img_arrow = PhotoImage(file="image/players_arrow.png")
        self.img_monkey = PhotoImage(file="image/monkey.png")
        self.img_banana_yellow = PhotoImage(file="image/banana_yellow.png")
        self.img_banana_rainbow = PhotoImage(file="image/banana_rainbow.png")

        # 상태 / 변수 
        self.state = STATE_TITLE
        self.frame = 0

        # 생존 시간
        self.start_time = 0.0
        self.survive_time = 0.0
        self.best_time = 0.0

        # 플레이어
        self.player = None
        self.player_hp = 5

        # 원숭이(여러 마리)
        self.monkeys = []
        self.monkey_dx = []
        self.monkey_dive = []
        self.monkey_dive_dir = []

        # 화살
        self.arrows = []
        self.arrow_vx = []
        self.arrow_vy = []

        # 바나나
        self.bananas = []
        self.banana_vx = []
        self.banana_vy = []
        self.banana_kind = []  # "yellow" or "rainbow"

        # 바나나 1/3/5개를 시간차로 던질 때 변수
        self.burst_left = 0              # 아직 던져야 할 개수
        self.burst_monkey_index = 0      # 어느 원숭이 기준인지
        self.burst_gap = 2               # 바나나 하나씩 나가는 프레임 간격

        # UI텍스트
        self.text_time = None
        self.text_best = None
        self.text_hp = None

        self.setTitleScreen()
        self.gameLoop()

    def onClose(self):
        try:
            pygame.mixer.quit()
        except:
            pass
        self.window.destroy()

    # 타이틀 화면 
    def setTitleScreen(self):
        self.canvas.delete("all")
        self.state = STATE_TITLE

        self.canvas.create_image(0, 0, anchor="nw", image=self.img_bg)

        self.canvas.create_text(503, 323,
                                text="SteelThe Monkey's trésor",
                                fill="orange",
                                font=("Arial", 50, "bold"))   #글자 입체감 느껴지도록..
        self.canvas.create_text(500, 320,
                                text="SteelThe Monkey's trésor",
                                fill="yellow",
                                font=("Arial", 50, "bold"))  
        self.canvas.create_text(500, 380,
                                text="원숭이의 바나나 공격을 피하며 오래 살아남으세요!",
                                fill="brown",
                                font=("Segoe UI", 18))
        self.canvas.create_text(680, 700,
                                text="작동방법",
                                fill="white",
                                font=("Arial", 14))
        self.canvas.create_text(800, 730,
                                text="시작: Space | 이동: ← → | 공격: Space",
                                fill="white",
                                font=("Arial", 14))
        self.canvas.create_text(500, 420,
                                text="Best Time: {:.1f}s".format(self.best_time),
                                fill="yellow",
                                font=("Arial", 15))

        self.snd_bgm.stop()

    # 게임 시작 
    def startGame(self):
        pygame.mixer.stop()
        self.canvas.delete("all")
        self.state = STATE_PLAY

        self.canvas.create_image(0, 0, anchor="nw", image=self.img_bg)

        self.start_time = time.time()
        self.survive_time = 0.0

        self.player_hp = 5

        self.arrows = []
        self.arrow_vx = []
        self.arrow_vy = []

        self.bananas = []
        self.banana_vx = []
        self.banana_vy = []
        self.banana_kind = []

        self.monkeys = []
        self.monkey_dx = []
        self.monkey_dive = []
        self.monkey_dive_dir = []

        self.burst_left = 0

        # 플레이어
        x = 500
        y = 720
        self.player = self.canvas.create_image(x, y, image=self.img_player_right)
        self.player_dir="right"

        # 원숭이 2마리
        positions = [350, 650]
        for i, mx in enumerate(positions):
            my = 200
            m = self.canvas.create_image(mx, my, image=self.img_monkey)
            self.monkeys.append(m)
            self.monkey_dx.append(5 if i == 0 else -5)
            self.monkey_dive.append(False)
            self.monkey_dive_dir.append(1)

        # UI
        self.text_time = self.canvas.create_text(500, 10,
                                                 anchor="n",
                                                 fill="yellow",
                                                 font=("Courier New", 18, "bold"),
                                                 text="Time: 0.0s")

        self.text_best = self.canvas.create_text(990, 10,
                                                 anchor="ne",
                                                 fill="white",
                                                 font=("Courier New", 12),
                                                 text="Best: {:.1f}s".format(self.best_time))

        self.text_hp = self.canvas.create_text(10, 790,
                                               anchor="sw",
                                               fill="red",
                                               font=("Courier New", 22, "bold"),
                                               text="♥" * self.player_hp)

        self.snd_bgm.play(-1)

    #  키 처리 
    def keyPressHandler(self, event):
        self.keys.add(event.keysym)
        if event.keysym == "space":
            if self.state == STATE_TITLE:
                self.startGame()
        if event.keysym in ("r", "R"):
            if self.state == STATE_GAME_OVER:
                self.setTitleScreen()

    def keyReleaseHandler(self, event):
        if event.keysym in self.keys:
            self.keys.remove(event.keysym)

    #  플레이어 
    def movePlayer(self):
        if self.state != STATE_PLAY or self.player is None:
            return
        dx = 0
        speed = 12
        if "Left" in self.keys:
            dx -= speed
            if self.player_dir != "left":
                self.canvas.itemconfig(self.player, image=self.img_player_left)
                self.player_dir = "left"

        if "Right" in self.keys:
            dx += speed
            if self.player_dir != "right":
                self.canvas.itemconfig(self.player, image=self.img_player_right)
                self.player_dir = "right"
        if dx != 0:
            x1, y1, x2, y2 = self.canvas.bbox(self.player)
            if x1 + dx < 0:
                dx = -x1
            if x2 + dx > 1000:
                dx = 1000 - x2
            self.canvas.move(self.player, dx, 0)

    # 화살 발사 
    def fireArrow(self):
        if self.state != STATE_PLAY:
            return
        if "space" not in self.keys:
            return
        if self.frame % 5 != 0:
            return
        if self.player is None:
            return

        x1, y1, x2, y2 = self.canvas.bbox(self.player)
        cx = (x1 + x2) / 2
        top = y1

        arrow = self.canvas.create_image(cx, top - 12, image=self.img_arrow)
        self.arrows.append(arrow)
        self.arrow_vx.append(0)
        self.arrow_vy.append(-20)

        self.snd_arrow.play()

    def moveArrows(self):
        for i in range(len(self.arrows) - 1, -1, -1):
            a = self.arrows[i]
            vx = self.arrow_vx[i]
            vy = self.arrow_vy[i]
            self.canvas.move(a, vx, vy)
            x1, y1, x2, y2 = self.canvas.bbox(a)
            if y2 < 0:
                self.canvas.delete(a)
                del self.arrows[i]
                del self.arrow_vx[i]
                del self.arrow_vy[i]

    #  원숭이 이동 + 돌진 
    def moveMonkeys(self):
        if self.state != STATE_PLAY:
            return
        for i in range(len(self.monkeys)):
            m = self.monkeys[i]
            dx = self.monkey_dx[i]
            dive = self.monkey_dive[i]
            dive_dir = self.monkey_dive_dir[i]

            x1, y1, x2, y2 = self.canvas.bbox(m)

            if dive:
                self.canvas.move(m, dx, 8 * dive_dir)
                x1, y1, x2, y2 = self.canvas.bbox(m)

                if x1 < 0:
                    self.canvas.move(m, -x1, 0)
                    dx = -dx
                elif x2 > 1000:
                    self.canvas.move(m, 1000 - x2, 0)
                    dx = -dx

                if y2 > 320:
                    dive_dir = -1
                if y1 < 80:
                    dive = False
                    dive_dir = 1
            else:
                self.canvas.move(m, dx, 0)
                x1, y1, x2, y2 = self.canvas.bbox(m)
                if x1 < 0 or x2 > 1000:
                    dx = -dx

            self.monkey_dx[i] = dx
            self.monkey_dive[i] = dive
            self.monkey_dive_dir[i] = dive_dir

    #  바나나 생성 (1/3/5, 한 알씩 시간차로) 
    def spawnBanana(self):
        if self.state != STATE_PLAY or len(self.monkeys) == 0:
            return

        difficulty = int(self.survive_time // 5)
        base_interval = 45
        base_speed = 8

        interval = max(12, base_interval - difficulty * 3)
        speed = base_speed + difficulty

        # 돌진 확률
        base_prob = 0.005
        prob = base_prob + difficulty * 0.002
        if prob > 0.03:
            prob = 0.03
        for i in range(len(self.monkeys)):
            if not self.monkey_dive[i] and random.random() < prob:
                self.monkey_dive[i] = True
                self.monkey_dive_dir[i] = 1

        # 새 버스트 시작
        if self.burst_left == 0 and self.frame % interval == 0:
            if difficulty < 2:
                choices = [1, 3]
            else:
                choices = [1, 3, 5]
            self.burst_left = random.choice(choices)
            self.burst_monkey_index = random.randrange(len(self.monkeys))

        if self.burst_left > 0 and self.frame % self.burst_gap == 0:
            m = self.monkeys[self.burst_monkey_index]
            mx1, my1, mx2, my2 = self.canvas.bbox(m)
            mx = (mx1 + mx2) / 2
            my = my2

            start_x = mx + random.randint(-80, 80)
            vy = speed + random.randint(0, 3)
            vx = 0

            if self.player is not None:
                px1, py1, px2, py2 = self.canvas.bbox(self.player)
                px = (px1 + px2) / 2
                dx = px - start_x
                denom = 80.0 - difficulty * 4
                if denom < 40:
                    denom = 40
                vx = dx / denom + random.uniform(-1.5, 1.5)

            #바나나 떨어지는 위치
            spawn_y=120
            banana = self.canvas.create_image(start_x, spawn_y,
                                              image=self.img_banana_yellow)
            self.bananas.append(banana)
            self.banana_vx.append(vx)
            self.banana_vy.append(vy)
            self.banana_kind.append("yellow")

            self.burst_left -= 1

            # 무지개 바나나: 확률 10%로 추가 생성
            if random.random() < 0.10:
                rx = random.randint(40, 960)
                spawn_y=110
                rainbow = self.canvas.create_image(rx, spawn_y,
                                                   image=self.img_banana_rainbow)
                self.bananas.append(rainbow)
                self.banana_vx.append(0)
                self.banana_vy.append(speed - 2)
                self.banana_kind.append("rainbow")

    #  바나나 이동 
    def moveBananas(self):
        for i in range(len(self.bananas) - 1, -1, -1):
            b = self.bananas[i]
            vx = self.banana_vx[i]
            vy = self.banana_vy[i] + 0.25
            self.banana_vy[i] = vy
            self.canvas.move(b, vx, vy)
            x1, y1, x2, y2 = self.canvas.bbox(b)
            if y1 > 800:
                self.canvas.delete(b)
                del self.bananas[i]
                del self.banana_vx[i]
                del self.banana_vy[i]
                del self.banana_kind[i]

    #  HP 텍스트 
    def updateHpText(self):
        if self.text_hp is not None:
            self.canvas.itemconfig(self.text_hp, text="♥" * self.player_hp)

    #  충돌 처리 
    def checkCollisions(self):
        # 화살 vs 바나나
        for ai in range(len(self.arrows) - 1, -1, -1):
            a = self.arrows[ai]
            ax1, ay1, ax2, ay2 = self.canvas.bbox(a)
            hit = False
            for bi in range(len(self.bananas) - 1, -1, -1):
                b = self.bananas[bi]
                bx1, by1, bx2, by2 = self.canvas.bbox(b)
                if not (ax2 < bx1 or ax1 > bx2 or ay2 < by1 or ay1 > by2):
                    kind = self.banana_kind[bi] #무지개바나나는 화살을 맞지않는다. 
                    if kind == "rainbow":
                        continue

                    self.canvas.delete(b)
                    del self.bananas[bi]
                    del self.banana_vx[bi]
                    del self.banana_vy[bi]
                    del self.banana_kind[bi]
                    hit = True
                    break
            if hit:
                self.canvas.delete(a)
                del self.arrows[ai]
                del self.arrow_vx[ai]
                del self.arrow_vy[ai]

        # 플레이어 vs 바나나
        if self.player is None:
            return
        px1, py1, px2, py2 = self.canvas.bbox(self.player)
        for i in range(len(self.bananas) - 1, -1, -1):
            b = self.bananas[i]
            bx1, by1, bx2, by2 = self.canvas.bbox(b)
            if not (px2 < bx1 or px1 > bx2 or py2 < by1 or py1 > by2):
                kind = self.banana_kind[i]
                self.canvas.delete(b)
                del self.bananas[i]
                del self.banana_vx[i]
                del self.banana_vy[i]
                del self.banana_kind[i]

                if kind == "yellow":
                    self.player_hp -= 1
                    if self.player_hp < 0:
                        self.player_hp = 0
                    self.updateHpText()
                    self.snd_player_hit.play()

                    if self.player_hp <= 0:
                        self.gameOver()
                        return
                elif kind == "rainbow":
                    if self.player_hp < 5:
                        self.player_hp += 1
                        self.updateHpText()
                    self.snd_rainbow.play()

    # 게임 over  
    def gameOver(self):
        self.state = STATE_GAME_OVER
        self.snd_bgm.stop()
        self.snd_gameover.play()

        if self.survive_time > self.best_time:
            self.best_time = self.survive_time

        self.canvas.create_text(503, 363,
                                text="GAME OVER",
                                fill="black",
                                font=("Arial Black", 40, "bold"))
        self.canvas.create_text(500, 360,
                                text="GAME OVER",
                                fill="red",
                                font=("Arial Black", 40, "bold"))
        self.canvas.create_text(500, 410,
                                text="생존시간: {:.1f} s".format(self.survive_time),
                                fill="blue",
                                font=("Arial Black New", 16))
        self.canvas.create_text(500, 440,
                                text="R 키: Restart",
                                fill="blue",
                                font=("Arial", 14))

    # 메인 루프 
    def gameLoop(self):
        self.frame += 1

        if self.state == STATE_PLAY:
            now = time.time()
            self.survive_time = now - self.start_time
            if self.text_time is not None:
                self.canvas.itemconfig(self.text_time,
                                       text="Time: {:.1f}s".format(self.survive_time))
            if self.text_best is not None:
                self.canvas.itemconfig(self.text_best,
                                       text="Best: {:.1f}s".format(self.best_time))

            self.movePlayer()
            self.moveMonkeys()
            self.fireArrow()
            self.moveArrows()
            self.spawnBanana()
            self.moveBananas()
            self.checkCollisions()

        self.window.after(30, self.gameLoop)

if __name__ == "__main__":
    game = SteelMonkeyGame()
    game.window.mainloop()
