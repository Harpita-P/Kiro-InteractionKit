@echo off
REM Kiro Motion Kit Setup Script for Windows

echo ==================================
echo Kiro Motion Kit Setup
echo ==================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo.

REM Test camera
echo Testing camera access...
python -c "import cv2; cap = cv2.VideoCapture(0); success = cap.isOpened(); cap.release(); print('Camera accessible' if success else 'Camera not accessible')"
echo.

REM Ask to create example game
set /p create_example="Would you like to create an example game? (y/n): "

if /i "%create_example%"=="y" (
    set /p game_name="Enter game name (e.g., my-game): "
    
    mkdir "my_apps\%game_name%\assets" 2>nul
    
    (
        echo import os, sys, cv2, pygame
        echo.
        echo PROJECT_ROOT = os.path.dirname^(os.path.dirname^(os.path.dirname^(os.path.abspath^(__file__^)^)^)^)
        echo sys.path.insert^(0, PROJECT_ROOT^)
        echo.
        echo from kiro_motion_kit.controllers.hand_controller import HandTracker
        echo.
        echo def main^(^):
        echo     pygame.init^(^)
        echo     screen = pygame.display.set_mode^(^(800, 600^)^)
        echo     clock = pygame.time.Clock^(^)
        echo     cap = cv2.VideoCapture^(0^)
        echo     tracker = HandTracker^(^)
        echo     score = 0
        echo     prev_pinch = False
        echo     running = True
        echo     while running:
        echo         for event in pygame.event.get^(^):
        echo             if event.type == pygame.QUIT:
        echo                 running = False
        echo             elif event.type == pygame.KEYDOWN:
        echo                 if event.key == pygame.K_ESCAPE:
        echo                     running = False
        echo         success, frame = cap.read^(^)
        echo         if success:
        echo             _, state = tracker.process_frame^(frame^)
        echo             if state.is_pinch and not prev_pinch:
        echo                 score += 1
        echo             prev_pinch = state.is_pinch
        echo         screen.fill^(^(30, 30, 30^)^)
        echo         font = pygame.font.Font^(None, 72^)
        echo         text = font.render^(f"Score: {score}", True, ^(255, 255, 255^)^)
        echo         screen.blit^(text, ^(250, 250^)^)
        echo         instruction = pygame.font.Font^(None, 36^).render^("Pinch to score!", True, ^(200, 200, 200^)^)
        echo         screen.blit^(instruction, ^(280, 350^)^)
        echo         pygame.display.flip^(^)
        echo         clock.tick^(30^)
        echo     cap.release^(^)
        echo     tracker.close^(^)
        echo     pygame.quit^(^)
        echo.
        echo if __name__ == "__main__":
        echo     main^(^)
    ) > "my_apps\%game_name%\main.py"
    
    (
        echo # %game_name%
        echo.
        echo A simple gesture-controlled game.
        echo.
        echo ## Controls
        echo.
        echo - **Pinch**: Increment score
        echo - **ESC**: Quit
        echo.
        echo ## Run
        echo.
        echo ```bash
        echo python my_apps\%game_name%\main.py
        echo ```
    ) > "my_apps\%game_name%\README.md"
    
    echo Created example game at my_apps\%game_name%
    echo.
)

echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Test gestures: python tests\CV-Test-Hands.py
echo 2. Read the guide: .kiro\steering\game-development.md
if /i "%create_example%"=="y" (
    echo 3. Run your game: python my_apps\%game_name%\main.py
)
echo.
echo Happy coding! 🎮
pause
