# Holo-Board Changelog

## Latest Update (v6 - Professional Polish)

### Professional UI Refinements

**Removed Clutter:**
- Removed Y/N keyboard shortcuts (buttons are sufficient)
- Removed all emoji symbols (📁, 🖼️, 📷) for professional appearance
- Simplified instructions to be clearer and more concise

**Y/N Dialog:**
- Clean hint: "Click a button or press ESC to cancel"
- Better description: "Add an image to draw over during your recording"
- No redundant keyboard shortcuts

**File Browser:**
- "Folder: Annotate" instead of "📁 Annotate"
- Clean file names without emoji icons
- Clear instructions: "Use arrow keys to navigate, ENTER to select, or click on a file"
- Professional, minimalist appearance

**Documentation:**
- Added README.md in Recordings folder
- Added README.md in Annotate folder
- Clear explanations of folder purposes

## Previous Update (v5 - Beautiful Light Theme)

### UI Redesign - Light Theme with Turquoise

**Color Scheme:**
- Light blue-gray background (245, 248, 250)
- Clean white cards with subtle shadows
- Dark turquoise accents (0, 128, 128) for titles and selections
- Dark text (40, 50, 60) for excellent readability
- Light gray for secondary text and buttons

**Typography:**
- System font (Arial) for better rendering
- Bold titles for emphasis
- Proper font sizes for hierarchy
- Clean, professional appearance

**Y/N Dialog:**
- Light background with white card
- Turquoise title and "Yes" button
- Subtle shadow for depth
- Gray "No" button
- Excellent contrast and readability

**File Browser:**
- Light theme with white card
- Turquoise title and selected items
- Light gray item backgrounds with hover effects
- File type icons (🖼️ 📷)
- Turquoise scroll indicator
- Clean, modern appearance

## Previous Update (v4 - Organized Folders)

### Folder Organization

**Annotate Folder:**
- File browser now starts in the `Annotate` folder instead of `Assets`
- All annotation images should be placed in `my_apps/Holo-Board/Annotate/`
- Both tkinter and pygame file browsers use this folder as default

**Recordings Folder:**
- All recordings are now saved to `my_apps/Holo-Board/Recordings/`
- Folder is automatically created if it doesn't exist
- Keeps recordings organized and separate from other files
- No more recordings scattered in the main directory

## Previous Update (v3 - Modern UI)

### Modern UI Redesign

**Y/N Dialog:**
- Sleek card-based design with rounded corners
- Modern color scheme (dark theme with blue accents)
- Interactive buttons with hover effects
- Clickable buttons (mouse support) + keyboard shortcuts
- Smooth 60 FPS animations
- Professional typography with better spacing

**File Browser:**
- Beautiful card-based layout with rounded corners
- File items with hover effects and smooth transitions
- Visual file type icons (🖼️ for PNG, 📷 for JPG)
- Mouse click support for file selection
- Scroll indicator for long file lists
- Modern dark theme with blue accents
- Better visual hierarchy and spacing
- 60 FPS smooth rendering

## Previous Update (v2)

### UI Improvements

1. **Launch Screen Scaling**
   - Launch background image scaled down to 70% for better visibility
   - Prevents the image from being too zoomed in
   - Better centered composition on screen

2. **Start Button Redesign**
   - Start button dramatically reduced to 25% of original size
   - Much more subtle and professional appearance
   - Still features smooth pulsing animation (90% to 110% of base scale)
   - Positioned at bottom center of screen

3. **GUI File Picker**
   - Replaced command-line file input with GUI file browser
   - **Primary method**: Uses tkinter's native file dialog (if available)
   - **Fallback method**: Custom pygame-based file browser with keyboard navigation
   - Features:
     - Arrow keys to navigate files
     - ENTER to select, ESC to cancel
     - Shows only image files (PNG, JPG, JPEG)
     - Starts in Assets directory by default
   - Much more user-friendly than command-line input

4. **Expanded Color Palette**
   - Added 2 new pen colors to the existing palette
   - **New colors:**
     - Pink (255, 45, 85)
     - Cyan (0, 199, 190)
   - **Total colors:** 8 (Red, Blue, Green, Orange, Yellow, Purple, Pink, Cyan)
   - Use thumbs up gesture to cycle through all colors

### User Flow

1. App launches → Launch screen appears with scaled background
2. User clicks small animated start button at bottom
3. Camera initializes
4. GUI file picker opens for optional image annotation
5. Main drawing interface loads with all features

### Technical Changes

- Added optional `tkinter` and `filedialog` imports with graceful fallback
- Created `_show_pygame_file_browser()` as fallback file picker using pygame
- Modified `_show_launch_screen()` with 70% background scaling and 25% button base scale
- Updated `_prompt_for_image_annotation()` to use GUI file selection (tkinter or pygame fallback)
- Expanded `DrawingManager.COLOR_PALETTE` from 6 to 8 colors
- Added `TKINTER_AVAILABLE` flag to handle environments without tkinter support
