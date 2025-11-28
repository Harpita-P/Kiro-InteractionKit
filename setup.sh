#!/bin/bash

# Kiro Motion Kit Setup Script
# This script helps you get started with Kiro Motion Kit

echo "=================================="
echo "Kiro Motion Kit Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo ""

# Test camera
echo "Testing camera access..."
python3 -c "import cv2; cap = cv2.VideoCapture(0); success = cap.isOpened(); cap.release(); print('✓ Camera accessible' if success else '✗ Camera not accessible')"
echo ""

# Create example game structure
echo "Would you like to create an example game? (y/n)"
read -r create_example

if [ "$create_example" = "y" ]; then
    echo "Enter game name (e.g., my-game):"
    read -r game_name
    
    game_dir="my_apps/$game_name"
    mkdir -p "$game_dir/assets"
    
    cat > "$game_dir/main.py" << 'EOF'
import os, sys, cv2, pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from kiro_motion_kit.controllers.hand_controller import HandTracker

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    
    score = 0
    prev_pinch = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        success, frame = cap.read()
        if success:
            _, state = tracker.process_frame(frame)
            
            if state.is_pinch and not prev_pinch:
                score += 1
            prev_pinch = state.is_pinch
        
        screen.fill((30, 30, 30))
        font = pygame.font.Font(None, 72)
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (250, 250))
        
        instruction = pygame.font.Font(None, 36).render("Pinch to score!", True, (200, 200, 200))
        screen.blit(instruction, (280, 350))
        
        pygame.display.flip()
        clock.tick(30)
    
    cap.release()
    tracker.close()
    pygame.quit()

if __name__ == "__main__":
    main()
EOF

    cat > "$game_dir/README.md" << EOF
# $game_name

A simple gesture-controlled game.

## Controls

- **Pinch**: Increment score
- **ESC**: Quit

## Run

\`\`\`bash
python my_apps/$game_name/main.py
\`\`\`
EOF

    echo "✓ Created example game at $game_dir"
    echo ""
fi

echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Test gestures: python3 tests/CV-Test-Hands.py"
echo "2. Read the guide: .kiro/steering/game-development.md"
if [ "$create_example" = "y" ]; then
    echo "3. Run your game: python3 my_apps/$game_name/main.py"
fi
echo ""
echo "Happy coding! 🎮"
