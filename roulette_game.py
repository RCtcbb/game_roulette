import pygame
import sqlite3
import random
import math
import time

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

# Setup screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roulette Game")
font = pygame.font.Font(None, FONT_SIZE)

# Database setup
DB_FILE = "player_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY,
            balance INTEGER
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM player")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO player (balance) VALUES (?)", (1000,))  # Default balance
    conn.commit()
    conn.close()

def get_balance():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM player WHERE id = 1")
    balance = cursor.fetchone()[0]
    conn.close()
    return balance

def update_balance(new_balance):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE player SET balance = ? WHERE id = 1", (new_balance,))
    conn.commit()
    conn.close()

def draw_roulette_wheel(result_number):
    # Draw roulette wheel with 37 segments
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

    # Highlight winning number
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
    # Simulate spinning the roulette wheel
    total_spins = random.randint(720, 1080)  # Total degrees the wheel will spin
    segments = 37
    angle_step = 360 / segments
    for angle in range(0, total_spins, 10):
        screen.fill(WHITE)
        draw_roulette_wheel(angle // angle_step % segments)
        pygame.display.flip()
        pygame.time.delay(30)

    return (total_spins // angle_step) % segments

# Game logic
def spin_roulette():
    result_number = spin_roulette_animation()
    result_color = "red" if result_number % 2 == 0 else "black"

    # Display the final result for 3 seconds
    screen.fill(WHITE)
    draw_roulette_wheel(result_number)
    result_text = font.render(f"Result: {result_number} ({result_color})", True, BLACK)
    screen.blit(result_text, (CENTER_X - result_text.get_width() // 2, CENTER_Y + ROULETTE_RADIUS + 20))
    pygame.display.flip()
    time.sleep(3)

    return result_number, result_color

def main():
    init_db()
    balance = get_balance()

    running = True
    bet_amount = 10  # Default bet amount
    bet_choice = ""  # Bet choice: number or color
    result_message = ""

    while running:
        screen.fill(WHITE)

        # Display balance
        balance_text = font.render(f"Balance: ${balance}", True, BLACK)
        screen.blit(balance_text, (20, 20))

        # Display instructions
        instructions = font.render(
            "Use UP/DOWN to adjust bet amount, ENTER to bet, R for red, B for black, N for number", True, BLACK
        )
        screen.blit(instructions, (20, 60))

        dev_instructions = font.render(
            "Press D for unlimited cash (DEV mode)", True, BLACK
        )
        screen.blit(dev_instructions, (20, 100))

        # Display bet amount and choice
        bet_amount_text = font.render(f"Bet Amount: ${bet_amount}", True, BLACK)
        screen.blit(bet_amount_text, (20, 160))

        bet_choice_text = font.render(f"Bet Choice: {bet_choice}", True, BLACK)
        screen.blit(bet_choice_text, (20, 200))

        # Display result message
        result_text = font.render(result_message, True, RED if "lost" in result_message else GREEN)
        screen.blit(result_text, (20, 260))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and bet_choice:
                    try:
                        result_number, result_color = spin_roulette()

                        if bet_amount > balance:
                            result_message = "Insufficient balance!"
                        elif bet_choice == "red" or bet_choice == "black":
                            if bet_choice == result_color:
                                winnings = int(bet_amount * 1.5)
                                balance += winnings
                                result_message = f"You won! Color: {result_color}. Winnings: ${winnings}"
                            else:
                                balance -= bet_amount
                                result_message = f"You lost! Color: {result_color}. Lost: ${bet_amount}"
                        elif bet_choice.isdigit():
                            bet_number = int(bet_choice)
                            if bet_number < 0 or bet_number > 36:
                                result_message = "Invalid number! Choose between 0 and 36."
                            elif bet_number == result_number:
                                winnings = bet_amount * 2
                                balance += winnings
                                result_message = f"You won! Number: {result_number}. Winnings: ${winnings}"
                            else:
                                balance -= bet_amount
                                result_message = f"You lost! Number: {result_number}. Lost: ${bet_amount}"
                        else:
                            result_message = "Invalid bet choice!"
                        update_balance(balance)

                    except ValueError:
                        result_message = "Invalid input!"

                elif event.key == pygame.K_UP:
                    bet_amount += 10

                elif event.key == pygame.K_DOWN:
                    bet_amount = max(10, bet_amount - 10)

                elif event.key == pygame.K_r:
                    bet_choice = "red"

                elif event.key == pygame.K_b:
                    bet_choice = "black"

                elif event.key == pygame.K_n:
                    bet_choice = ""
                    result_message = "Enter a number using LEFT/RIGHT keys."

                elif event.key == pygame.K_RIGHT and bet_choice == "":
                    bet_choice = str((int(bet_choice) + 1) % 37 if bet_choice.isdigit() else 0)

                elif event.key == pygame.K_LEFT and bet_choice == "":
                    bet_choice = str((int(bet_choice) - 1) % 37 if bet_choice.isdigit() else 36)

                elif event.key == pygame.K_d:  # Developer key for unlimited cash
                    balance = 999999
                    result_message = "DEV mode activated: Unlimited cash!"
                    update_balance(balance)

        # Update screen
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
