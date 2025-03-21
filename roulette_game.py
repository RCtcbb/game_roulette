import pygame
import csv
import random
import math
import os

# Initialize Pygame
pygame.init()

# Constants for screen dimensions and colors
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FONT_SIZE = 24
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
ROULETTE_RADIUS = 200
CSV_FILE = "player_data.csv"

# Setup screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roulette Game")
font = pygame.font.Font(None, FONT_SIZE)

def init_csv():
    """Initialize the CSV file with starting balance if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["balance"])  # Column for balance
            writer.writerow([1000])  # Initial balance

def get_balance():
    """Read the current balance from the CSV file."""
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        return int(next(reader)[0])  # Return the balance value

def update_balance(new_balance):
    """Update the balance in the CSV file."""
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["balance"])  # Column for balance
        writer.writerow([new_balance])  # Update with new balance

def draw_roulette_wheel(result_number):
    """Draw the roulette wheel with the winning number indicated."""
    segments = 33
    angle_step = 360 / segments
    colors = [RED if i % 2 == 0 else BLACK for i in range(segments)]  # Alternate red and black
    for i in range(segments):
        start_angle = math.radians(i * angle_step)
        end_angle = math.radians((i + 1) * angle_step)
        pygame.draw.arc(
            screen,
            colors[i],  # Color for each segment
            (CENTER_X - ROULETTE_RADIUS, CENTER_Y - ROULETTE_RADIUS, ROULETTE_RADIUS * 2, ROULETTE_RADIUS * 2),
            start_angle,
            end_angle,
            5  # Width of the arc line
        )
    # Draw the line indicating the winning segment
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
    """Animate the roulette wheel spinning."""
    total_spins = random.randint(720, 1080)  # Spin the wheel multiple times
    segments = 33
    angle_step = 360 / segments
    for angle in range(0, total_spins, 10):  # Update every 10 degrees
        screen.fill(WHITE)  # Clear screen
        draw_roulette_wheel(angle // angle_step % segments)  # Draw current state of the wheel
        pygame.display.flip()
        pygame.time.delay(30)  # Delay between frames to animate the spinning
    return (total_spins // angle_step) % segments  # Return the final segment as the result

def spin_roulette():
    """Spin the roulette wheel and return the winning number and color."""
    return spin_roulette_animation(), random.choice(["red", "black"])  # Randomly choose red or black

def draw_arrow_button(rect, direction):
    """Draw an arrow button for adjusting the selected number."""
    pygame.draw.rect(screen, BLACK, rect, 2)
    if direction == 'up':  # Draw upward arrow
        pygame.draw.polygon(screen, BLACK, [
            (rect.centerx, rect.y + 5),
            (rect.x + 5, rect.bottom - 5),
            (rect.right - 5, rect.bottom - 5)
        ])
    elif direction == 'down':  # Draw downward arrow
        pygame.draw.polygon(screen, BLACK, [
            (rect.centerx, rect.bottom - 5),
            (rect.x + 5, rect.y + 5),
            (rect.right - 5, rect.y + 5)
        ])

def main():
    """Main function for the game loop."""
    init_csv()  # Initialize the CSV file
    balance = get_balance()  # Get the current balance
    running = True
    bet_amount = ""  # Player's bet amount (string to handle input)
    bet_choice = ""  # Player's bet choice (red or black)
    result_message = ""  # Message to display the result
    selected_number = None  # Store the selected number or None if not selected
    selecting_number = False  # Flag to indicate whether the player is selecting a number
    buttons = {str(i): pygame.Rect(50 + (i % 5) * 80, 500 + (i // 5) * 60, 60, 50) for i in range(10)}  # Number buttons
    red_button = pygame.Rect(600, 500, 100, 50)  # Red button for color choice
    black_button = pygame.Rect(720, 500, 100, 50)  # Black button for color choice
    next_button = pygame.Rect(850, 500, 100, 50)  # Next button to proceed with the game

    # Arrow buttons for selecting a number
    up_arrow_button = pygame.Rect(440, 480, 50, 50)
    down_arrow_button = pygame.Rect(440, 560, 50, 50)
    
    while running:
        screen.fill(WHITE)  # Fill screen with white background
        balance_text = font.render(f"Balance: ${balance}", True, BLACK)
        screen.blit(balance_text, (20, 20))
        instructions = font.render("Click numbers for bet, then NEXT to choose number", True, BLACK)
        screen.blit(instructions, (20, 60))
        bet_amount_text = font.render(f"Bet Amount: {bet_amount if bet_amount else 'None'}", True, BLACK)
        screen.blit(bet_amount_text, (20, 100))
        bet_choice_text = font.render(f"Bet Choice: {bet_choice if bet_choice else 'None'}", True, BLACK)
        screen.blit(bet_choice_text, (20, 140))
        result_text = font.render(result_message, True, RED if "lost" in result_message else GREEN)
        screen.blit(result_text, (20, 180))

        # Show selected number if one is chosen
        if selected_number is not None:
            selected_number_text = font.render(f"Selected Number: {selected_number}", True, BLACK)
            screen.blit(selected_number_text, (20, 220))
        
        for key, rect in buttons.items():
            # Disable number buttons if a color is selected
            if bet_choice:
                pygame.draw.rect(screen, (200, 200, 200), rect, 2)  # Gray out number buttons
            else:
                pygame.draw.rect(screen, BLACK, rect, 2)
            
            text = font.render(key, True, BLACK)
            screen.blit(text, (rect.x + 20, rect.y + 10))

        # Draw color buttons if no number is selected
        if not selected_number:
            pygame.draw.rect(screen, RED, red_button)
            pygame.draw.rect(screen, BLACK, black_button)
            screen.blit(font.render("Red", True, WHITE), (red_button.x + 25, red_button.y + 10))
            screen.blit(font.render("Black", True, WHITE), (black_button.x + 25, black_button.y + 10))
        
        pygame.draw.rect(screen, GREEN, next_button)
        screen.blit(font.render("Next", True, WHITE), (next_button.x + 25, next_button.y + 10))
        
        # Draw the arrow buttons for selecting a number
        draw_arrow_button(up_arrow_button, 'up')
        draw_arrow_button(down_arrow_button, 'down')

        # Handle events such as button clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not selecting_number:
                    # Number button interactions
                    for key, rect in buttons.items():
                        if rect.collidepoint(event.pos) and not bet_choice:
                            bet_amount += key  # Add the clicked number to the bet amount
                    if next_button.collidepoint(event.pos) and bet_amount:
                        selecting_number = True  # Move to the next stage of selection
                else:
                    # Handle color selection
                    if not selected_number:
                        if red_button.collidepoint(event.pos):
                            bet_choice = "red"
                        elif black_button.collidepoint(event.pos):
                            bet_choice = "black"
            
            # Arrow button interactions for adjusting selected number
            if event.type == pygame.MOUSEBUTTONDOWN:
                if up_arrow_button.collidepoint(event.pos) and selected_number is not None and selected_number < 32:
                    selected_number += 1
                elif down_arrow_button.collidepoint(event.pos) and selected_number is not None and selected_number > 0:
                    selected_number -= 1

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and bet_amount.isdigit() and bet_choice:
                bet_amount = int(bet_amount)
                if bet_amount > balance:
                    result_message = "Insufficient balance!"  # Error message for insufficient funds
                else:
                    result_number, result_color = spin_roulette()  # Get the spin result
                    if (bet_choice == "red" or bet_choice == "black") and bet_choice == result_color:
                        winnings = int(bet_amount * 1.5)  # Winnings for correct color
                        balance += winnings
                        result_message = f"You won! Color: {result_color}. Winnings: ${winnings}"
                    elif selected_number is not None and selected_number == result_number:
                        winnings = bet_amount * 35  # Winnings for correct number
                        balance += winnings
                        result_message = f"You won! Number: {result_number}. Winnings: ${winnings}"
                    else:
                        balance -= bet_amount  # Deduct bet amount if player loses
                        result_message = f"You lost! Result: {result_number}. Lost: ${bet_amount}"
                    update_balance(balance)  # Update balance in CSV
                bet_amount, bet_choice, selected_number, selecting_number = "", "", None, False

        pygame.display.flip()  # Update the display
    pygame.quit()  # Close the game when the loop ends

if __name__ == "__main__":
    main()  # Run the game
