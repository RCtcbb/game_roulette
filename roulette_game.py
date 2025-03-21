import pygame
import csv
import random
import math
import time
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000  # Increased screen width
SCREEN_HEIGHT = 700  # Increased screen height
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 24  # Reduced font size for better readability
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
ROULETTE_RADIUS = 200
CSV_FILE = "player_data.csv"

# Setup screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roulette Game")
font = pygame.font.Font(None, FONT_SIZE)

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["balance"])
            writer.writerow([1000])

def get_balance():
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        return int(next(reader)[0])

def update_balance(new_balance):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["balance"])
        writer.writerow([new_balance])

def draw_roulette_wheel(result_number):
    segments = 37
    angle_step = 360 / segments
    colors = [RED if i % 2 == 0 else BLACK for i in range(segments)]
    for i in range(segments):
        start_angle = math.radians(i * angle_step)
        end_angle = math.radians((i + 1) * angle_step)
        pygame.draw.arc(
            screen,
            colors[i],
            (CENTER_X - ROULETTE_RADIUS, CENTER_Y - ROULETTE_RADIUS, ROULETTE_RADIUS * 2, ROULETTE_RADIUS * 2),
            start_angle,
            end_angle,
            5
        )
    winning_angle = math.radians(result_number * angle_step - angle_step / 2)
    pygame.draw.line(
        screen,
        GREEN,
        (CENTER_X, CENTER_Y),
        (
            CENTER_X + ROULETTE_RADIUS * math.cos(winning_angle),
            CENTER_Y - ROULETTE_RADIUS * math.sin(winning_angle),
        ),
        5,
    )

def spin_roulette_animation():
    total_spins = random.randint(720, 1080)
    segments = 37
    angle_step = 360 / segments
    for angle in range(0, total_spins, 10):
        screen.fill(WHITE)
        draw_roulette_wheel(angle // angle_step % segments)
        pygame.display.flip()
        pygame.time.delay(30)
    return (total_spins // angle_step) % segments

def spin_roulette():
    result_number = spin_roulette_animation()
    result_color = "red" if result_number % 2 == 0 else "black"
    screen.fill(WHITE)
    draw_roulette_wheel(result_number)
    result_text = font.render(f"Result: {result_number} ({result_color})", True, BLACK)
    screen.blit(result_text, (CENTER_X - result_text.get_width() // 2, CENTER_Y + ROULETTE_RADIUS + 20))
    pygame.display.flip()
    time.sleep(3)
    return result_number, result_color

def main():
    init_csv()
    balance = get_balance()
    running = True
    bet_amount = 10
    bet_choice = None  # None = no selection, "red", "black", int for number
    result_message = ""
    number_input = ""
    
    while running:
        screen.fill(WHITE)
        balance_text = font.render(f"Balance: ${balance}", True, BLACK)
        screen.blit(balance_text, (20, 20))
        instructions = font.render("UP/DOWN to adjust bet, ENTER to bet, R/B for color, Type number to bet", True, BLACK)
        screen.blit(instructions, (20, 60))
        bet_amount_text = font.render(f"Bet Amount: ${bet_amount}", True, BLACK)
        screen.blit(bet_amount_text, (20, 100))
        bet_choice_text = font.render(f"Bet Choice: {bet_choice if bet_choice is not None else 'None'}", True, BLACK)
        screen.blit(bet_choice_text, (20, 140))
        result_text = font.render(result_message, True, RED if "lost" in result_message else GREEN)
        screen.blit(result_text, (20, 180))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and bet_choice is not None:
                    result_number, result_color = spin_roulette()
                    if bet_amount > balance:
                        result_message = "Insufficient balance!"
                    elif isinstance(bet_choice, str):  # Bet on color
                        if bet_choice == result_color:
                            winnings = int(bet_amount * 1.5)
                            balance += winnings
                            result_message = f"You won! Color: {result_color}. Winnings: ${winnings}"
                        else:
                            balance -= bet_amount
                            result_message = f"You lost! Color: {result_color}. Lost: ${bet_amount}"
                    elif isinstance(bet_choice, int):  # Bet on number
                        if bet_choice == result_number:
                            winnings = bet_amount * 2
                            balance += winnings
                            result_message = f"You won! Number: {result_number}. Winnings: ${winnings}"
                        else:
                            balance -= bet_amount
                            result_message = f"You lost! Number: {result_number}. Lost: ${bet_amount}"
                    update_balance(balance)
                elif event.key == pygame.K_UP:
                    bet_amount += 10
                elif event.key == pygame.K_DOWN:
                    bet_amount = max(10, bet_amount - 10)
                elif event.key == pygame.K_r:
                    bet_choice = "red"
                elif event.key == pygame.K_b:
                    bet_choice = "black"
                elif event.key == pygame.K_BACKSPACE:
                    number_input = number_input[:-1]
                elif event.unicode.isdigit():
                    number_input += event.unicode
                    if number_input.isdigit() and 0 <= int(number_input) <= 36:
                        bet_choice = int(number_input)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
