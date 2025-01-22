import os
import pygame
from typing import List, Tuple
import random

class Card:
    def __init__(self, color: str, symbol: str, shading: str, number: int, filename: str):
        self.color = color
        self.symbol = symbol
        self.shading = shading
        self.number = number
        self.filename = filename  # Store the original filename

    @staticmethod
    def from_filename(filename: str):
        # Parse properties from filenames like "redsquiggleempty3.gif"
        color_map = {'red': 'red', 'gre': 'green', 'pur': 'purple'}
        symbol = 'squiggle' if 'squiggle' in filename else \
                 'oval' if 'oval' in filename else 'diamond'
        parts = filename[:-4].split(symbol)
        color_abbreviation = parts[0][:3]  # Extract abbreviation (e.g., 'red', 'gre', 'pur')
        color = color_map[color_abbreviation]  # Map to full color name
        shading = parts[1][:-1]  # Extract shading (e.g., 'empty', 'filled', or 'shaded')
        number = int(parts[1][-1])  # Extract number (e.g., 1, 2, or 3)

        return Card(color, symbol, shading, number, filename)

    def __repr__(self):
        return f"Card({self.color}, {self.symbol}, {self.shading}, {self.number})"

    def as_vector(self) -> Tuple[int, int, int, int]:
        # Convert card properties into a mathematical vector representation
        colors = {'red': 0, 'green': 1, 'purple': 2}
        symbols = {'diamond': 0, 'squiggle': 1, 'oval': 2}
        shadings = {'empty': 0, 'filled': 1, 'shaded': 2}
        return (colors[self.color], symbols[self.symbol], shadings[self.shading], self.number - 1)

def is_set(card1: Card, card2: Card, card3: Card) -> bool:
    """Check if three cards form a valid SET."""
    vectors = [card1.as_vector(), card2.as_vector(), card3.as_vector()]
    for i in range(4):
        values = {v[i] for v in vectors}
        if len(values) not in {1, 3}:  # Must be all same or all different
            return False
    return True

def find_one_set(cards: List[Card]) -> Tuple[int, int, int]:
    """Find one valid set from the cards, if it exists."""
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            for k in range(j + 1, len(cards)):
                if is_set(cards[i], cards[j], cards[k]):
                    return (i, j, k)
    return None

def find_all_sets(cards: List[Card]) -> List[Tuple[int, int, int]]:
    """Find all possible sets from the given cards."""
    sets = []
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            for k in range(j + 1, len(cards)):
                if is_set(cards[i], cards[j], cards[k]):
                    sets.append((i, j, k))
    return sets

def load_cards_from_folder(folder: str) -> List[Card]:
    """Load cards from the specified folder."""
    card_files = os.listdir(folder)
    return [Card.from_filename(f) for f in card_files if f.endswith('.gif')]

def main():
    # Set up the folder structure
    card_folder = os.path.join(os.path.dirname(__file__), 'kaarten')
    all_cards = load_cards_from_folder(card_folder)
    random.shuffle(all_cards)

    # Initialize pygame
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("SET Game")

    # Fonts
    font = pygame.font.Font(None, 36)
    large_font = pygame.font.Font(None, 72)

    # Load card images
    card_images = {card.filename: pygame.image.load(os.path.join(card_folder, card.filename)) for card in all_cards}

    # Game states
    game_state = "home"  # Can be "home", "playing", or "end"
    home_timer = 30  # Default time in home screen
    timer = home_timer
    player_score = 0
    computer_score = 0
    displayed_cards = []
    remaining_deck = []
    selected_cards = []
    clock = pygame.time.Clock()

    def draw_home_screen():
        screen.fill((255, 255, 255))
        title = large_font.render("SET Game", True, (0, 0, 0))
        timer_text = font.render(f"Time per round: {home_timer} seconds", True, (0, 0, 0))
        start_button = font.render("Start Playing", True, (0, 0, 255))

        screen.blit(title, (400, 100))
        screen.blit(timer_text, (400, 300))
        screen.blit(start_button, (450, 400))

        # Draw buttons
        pygame.draw.rect(screen, (0, 255, 0), (600, 350, 40, 40))  # Up button
        pygame.draw.rect(screen, (255, 0, 0), (650, 350, 40, 40))  # Down button

        # Arrows
        pygame.draw.polygon(screen, (0, 0, 0), [(610, 360), (630, 360), (620, 340)])  # Up arrow
        pygame.draw.polygon(screen, (0, 0, 0), [(660, 380), (680, 380), (670, 400)])  # Down arrow

    def draw_end_screen():
        screen.fill((255, 255, 255))
        result = "YOU WIN" if player_score > computer_score else "YOU LOSE"
        result_color = (0, 255, 0) if player_score > computer_score else (255, 0, 0)
        result_text = large_font.render(result, True, result_color)
        player_score_text = font.render(f"Your Score: {player_score}", True, (0, 0, 0))
        computer_score_text = font.render(f"Computer Score: {computer_score}", True, (0, 0, 0))
        replay_button = font.render("Play Again", True, (0, 0, 255))

        screen.blit(result_text, (400, 100))
        screen.blit(player_score_text, (400, 300))
        screen.blit(computer_score_text, (400, 350))
        screen.blit(replay_button, (450, 500))

    def draw_game_state():
        screen.fill((255, 255, 255))

        # Display cards
        for i, card in enumerate(displayed_cards):
            if card is not None:
                img = card_images[card.filename]
                x = (i % 4) * 250 + 10
                y = (i // 4) * 200 + 10
                screen.blit(img, (x, y))
                if i in selected_cards:
                    pygame.draw.rect(screen, (0, 255, 0), (x, y, 150, 100), 5)

        # Display timer, scores, and remaining cards
        timer_text = font.render(f"Time: {timer}s", True, (0, 0, 0))
        player_score_text = font.render(f"Player: {player_score}", True, (0, 0, 0))
        computer_score_text = font.render(f"Computer: {computer_score}", True, (0, 0, 0))
        remaining_cards_text = font.render(f"Cards left: {len(remaining_deck)}", True, (0, 0, 0))
        
        screen.blit(timer_text, (10, 700))
        screen.blit(player_score_text, (200, 700))
        screen.blit(computer_score_text, (400, 700))
        screen.blit(remaining_cards_text, (600, 700))

    def replace_cards(indices):
        for idx in indices:
            if remaining_deck:
                displayed_cards[idx] = remaining_deck.pop(0)
            else:
                displayed_cards[idx] = None

    def reset_game():
        nonlocal all_cards, displayed_cards, remaining_deck, player_score, computer_score, timer, home_timer
        random.shuffle(all_cards)
        displayed_cards = all_cards[:12]
        remaining_deck = all_cards[12:]
        player_score = 0
        computer_score = 0
        timer = home_timer  # Reset the timer to the user-set value
        pygame.time.set_timer(pygame.USEREVENT, 1000)  # Start the timer in the game

    reset_game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if game_state == "home":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 600 <= x <= 640 and 350 <= y <= 390:  # Up button
                        home_timer += 1
                    elif 650 <= x <= 690 and 350 <= y <= 390:  # Down button
                        home_timer = max(1, home_timer - 1)
                    elif 450 <= x <= 600 and 400 <= y <= 440:  # Start button
                        reset_game()
                        game_state = "playing"

            elif game_state == "playing":
                if event.type == pygame.USEREVENT:
                    timer -= 1
                    if timer <= 0:
                        found_set = find_one_set([card for card in displayed_cards if card is not None])
                        if found_set:
                            computer_score += 1
                            replace_cards(found_set)
                        else:
                            replace_cards([0, 1, 2])
                        timer = home_timer  # Reset timer to user-defined value

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    clicked_index = (mouse_y // 200) * 4 + (mouse_x // 250)
                    if 0 <= clicked_index < len(displayed_cards) and displayed_cards[clicked_index] is not None:
                        if clicked_index in selected_cards:
                            selected_cards.remove(clicked_index)
                        else:
                            selected_cards.append(clicked_index)
                        if len(selected_cards) == 3:
                            cards = [displayed_cards[i] for i in selected_cards]
                            if is_set(*cards):
                                player_score += 1
                                replace_cards(selected_cards)
                                timer = home_timer  # Reset timer when player finds a set
                            selected_cards = []

                # Check for game end conditions
                if not find_all_sets([card for card in displayed_cards if card is not None]) and not remaining_deck:
                    game_state = "end"

            elif game_state == "end":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 450 <= x <= 600 and 500 <= y <= 540:  # Play again button
                        game_state = "home"

        if game_state == "home":
            draw_home_screen()
        elif game_state == "playing":
            draw_game_state()
        elif game_state == "end":
            draw_end_screen()

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
