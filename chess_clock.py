import pygame
import sys
import time

class ChessClock:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Screen Setup
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chess Clock Pro")

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (200, 200, 200)

        # Fonts
        self.large_font = pygame.font.Font(None, 100)
        self.medium_font = pygame.font.Font(None, 50)
        self.small_font = pygame.font.Font(None, 30)

        # Sound Effects
        self.click_sound = pygame.mixer.Sound('click.wav')
        self.alarm_sound = pygame.mixer.Sound('alarm.wav')

        # Time Control Configurations
        self.time_controls = {
            "Blitz": {'initial_time': 300, 'increment': 5},   # 5 minutes, 5 sec increment
            "Rapid": {'initial_time': 600, 'increment': 10},  # 10 minutes, 10 sec increment
            "Classical": {'initial_time': 1800, 'increment': 30}  # 30 minutes, 30 sec increment
        }

        # Game State
        self.current_control = "Blitz"
        self.player1_time = self.time_controls[self.current_control]['initial_time']
        self.player2_time = self.time_controls[self.current_control]['initial_time']
        self.current_player = None
        self.game_started = False
        self.last_tick = None

        # Animation and Visual Effects
        self.particles = []
        self.font_color_cycle = 0

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def create_particles(self, x, y):
        for _ in range(20):
            self.particles.append({
                'x': x, 
                'y': y, 
                'color': (
                    min(255, self.RED[0] + 50), 
                    max(0, self.RED[1] - 50), 
                    max(0, self.RED[2] - 50)
                ),
                'size': pygame.math.Vector2(5, 5),
                'velocity': pygame.math.Vector2(
                    pygame.math.Vector2(pygame.mouse.get_pos()) - pygame.math.Vector2(x, y)
                ).normalize() * 5
            })

    def update_particles(self):
        for particle in self.particles[:]:
            particle['x'] += particle['velocity'].x
            particle['y'] += particle['velocity'].y
            particle['size'] *= 0.9
            if particle['size'].x < 0.5:
                self.particles.remove(particle)

    def draw_particles(self):
        for particle in self.particles:
            pygame.draw.circle(
                self.screen, 
                particle['color'], 
                (int(particle['x']), int(particle['y'])), 
                int(particle['size'].x)
            )

    def draw_clock(self):
        self.screen.fill(self.WHITE)

        # Dynamic Background
        self.font_color_cycle = (self.font_color_cycle + 1) % 255
        dynamic_bg = pygame.Surface((self.WIDTH, self.HEIGHT//2))
        dynamic_bg.fill((
            abs(255 - self.font_color_cycle),
            abs(128 - self.font_color_cycle),
            self.font_color_cycle
        ))
        self.screen.blit(dynamic_bg, (0, 0))

        # Player 1 Time Display
        p1_time_text = self.large_font.render(
            self.format_time(self.player1_time), 
            True, 
            self.BLACK if self.current_player != 1 else self.RED
        )
        p1_rect = p1_time_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//4))
        self.screen.blit(p1_time_text, p1_rect)

        # Player 2 Time Display
        p2_time_text = self.large_font.render(
            self.format_time(self.player2_time), 
            True, 
            self.BLACK if self.current_player != 2 else self.RED
        )
        p2_rect = p2_time_text.get_rect(center=(self.WIDTH//2, 3*self.HEIGHT//4))
        self.screen.blit(p2_time_text, p2_rect)

        # Time Control Indicator
        control_text = self.small_font.render(
            f"Time Control: {self.current_control}", 
            True, 
            self.BLACK
        )
        self.screen.blit(control_text, (10, 10))

        # Draw Particles
        self.draw_particles()

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Space to start/switch
                if event.key == pygame.K_SPACE and self.game_started:
                    self.switch_player()
                
                # Different time controls
                if event.key == pygame.K_1:
                    self.current_control = "Blitz"
                    self.reset_game()
                
                if event.key == pygame.K_2:
                    self.current_control = "Rapid"
                    self.reset_game()
                
                if event.key == pygame.K_3:
                    self.current_control = "Classical"
                    self.reset_game()
                
                # Start game
                if event.key == pygame.K_s:
                    self.start_game()

        return True

    def switch_player(self):
        if not self.game_started:
            return

        increment = self.time_controls[self.current_control]['increment']
        
        if self.current_player == 1:
            self.player1_time += increment
            self.current_player = 2
        elif self.current_player == 2:
            self.player2_time += increment
            self.current_player = 1

        self.click_sound.play()
        self.create_particles(self.WIDTH//2, self.HEIGHT//2)
        self.last_tick = time.time()

    def start_game(self):
        if not self.game_started:
            self.game_started = True
            self.current_player = 1
            self.last_tick = time.time()

    def reset_game(self):
        initial_time = self.time_controls[self.current_control]['initial_time']
        self.player1_time = initial_time
        self.player2_time = initial_time
        self.current_player = None
        self.game_started = False
        self.last_tick = None

    def update_times(self):
        if not self.game_started or self.current_player is None:
            return

        current_time = time.time()
        time_elapsed = current_time - self.last_tick
        
        if self.current_player == 1:
            self.player1_time -= time_elapsed
        else:
            self.player2_time -= time_elapsed

        self.last_tick = current_time

        # Game over conditions
        if self.player1_time <= 0 or self.player2_time <= 0:
            self.alarm_sound.play()
            self.game_started = False

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            running = self.handle_events()
            
            if self.game_started:
                self.update_times()
            
            self.update_particles()
            self.draw_clock()
            
            clock.tick(120)  # 60 FPS

        pygame.quit()
        sys.exit()

def main():
    chess_clock = ChessClock()
    chess_clock.run()

if __name__ == "__main__":
    main()
