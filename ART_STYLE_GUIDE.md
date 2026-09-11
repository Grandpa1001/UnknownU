# 🎨 UNKNOWN — Art Style Guide

**Version**: 1.0  
**Status**: Master Reference  
**Last Updated**: 2026-09-11  
**Inspiration**: Throungles, Game Boy Advanced era pixel art

---

## 📋 TABLE OF CONTENTS

1. Design Philosophy
2. Color Palette
3. Typography
4. Pixel Grid & Sizing
5. Character Design
6. Terrain & Environment
7. Objects & Interactions
8. Animation Guidelines
9. UI Design System
10. Asset Specifications
11. Do's and Don'ts
12. Implementation Checklist

---

## 1. DESIGN PHILOSOPHY

### Core Principles

**Clarity Over Complexity**
- Every pixel has purpose
- No decorative elements without function
- Visual hierarchy is explicit
- Readability is paramount

**Coherent Ecosystem**
- All elements share visual language
- Consistent depth perception
- Unified color harmony
- Harmonious animation timing

**Retro Authenticity**
- 16-bit era inspiration (GBA, SNES)
- Pixel-perfect implementation
- Limited but rich color palette
- Hand-crafted, not generated

**Emotional Resonance**
- World feels alive (not static)
- Characters have personality
- Environment tells story
- Movement feels natural

### Visual Tone

```
NOT:  Cutesy, cartoon, overly simplified
NOT:  Dark, gritty, dystopian
NOT:  Hyper-detailed, photorealistic
NOT:  Psychedelic, neon, cyberpunk

YES:  Warm, inviting, naturalistic
YES:  Calm but alive
YES:  Readable at any scale
YES:  Throungles-like (peaceful world with character)
```

---

## 2. COLOR PALETTE

### Primary Palette (Terrain & Base)

```
GRASS GREEN:       #4a7c59  (RGB: 74, 124, 89)   - Primary vegetation
DARK GREEN:        #2d5016  (RGB: 45, 80, 22)    - Tree foliage, shadows
LIGHT GREEN:       #6ba75a  (RGB: 107, 167, 90)  - Light grass, highlights
BROWN DIRT:        #8b6f47  (RGB: 139, 111, 71)  - Soil, earth tones
DARK BROWN:        #6b4423  (RGB: 107, 68, 35)   - Tree trunks, shadows
LIGHT TAN:         #c4a57b  (RGB: 196, 165, 123) - Light dirt, sand
PALE GREEN:        #a4c595  (RGB: 164, 197, 149) - Flower fields
SKY BLUE:          #87ceeb  (RGB: 135, 206, 235) - Sky (future)
```

### Creature Palette (Organisms)

```
CREATURE BLUE:     #2b5aa0  (RGB: 43, 90, 160)   - Base body color
DARK BLUE:         #1e4073  (RGB: 30, 64, 115)   - Shadows, depth
LIGHT BLUE:        #4a7cba  (RGB: 74, 124, 186)  - Highlights
ACCENT BLUE:       #5a9fd4  (RGB: 90, 159, 212)  - Details, features

WHITE:             #ffffff  (RGB: 255, 255, 255) - Eyes, highlights
BLACK:             #000000  (RGB: 0, 0, 0)       - Pupils, outlines
```

### Feature Colors (Mutable Elements)

```
ANTENA RED:        #e63946  (RGB: 230, 57, 70)   - Antena feature
HORN BROWN:        #8b4513  (RGB: 139, 69, 19)   - Horn feature
LEG TEAL:          #5a7a8a  (RGB: 90, 122, 138)  - Leg feature
BUMP SHADE:        #3a6aa0  (RGB: 58, 106, 160)  - Bump texture
WING CYAN:         #4a90e2  (RGB: 74, 144, 226)  - Wing feature
```

### Flower Palette (Decoration)

```
PINK FLOWER:       #ffb4d6  (RGB: 255, 180, 214)
GOLDEN FLOWER:     #ffd700  (RGB: 255, 215, 0)
PURPLE FLOWER:     #b19cd9  (RGB: 177, 156, 217)
MAGENTA FLOWER:    #ff69b4  (RGB: 255, 105, 180)
FLOWER CENTER:     #ffeb3b  (RGB: 255, 235, 59)
```

### Tree Palette

```
TRUNK DARK:        #6b4423  (RGB: 107, 68, 35)
TRUNK LIGHT:       #8b5a3c  (RGB: 139, 90, 60)
FOLIAGE DARK:      #2d5016  (RGB: 45, 80, 22)
FOLIAGE MID:       #3d6b1f  (RGB: 61, 107, 31)
APPLE RED:         #e63946  (RGB: 230, 57, 70)
```

### UI Palette (Observatory)

```
UI BACKGROUND:     #1a1a1a  (RGB: 26, 26, 26)    - Dark background
UI SURFACE:        #2a2a2a  (RGB: 42, 42, 42)    - Card/panel background
UI BORDER:         #404040  (RGB: 64, 64, 64)    - Borders
UI TEXT:           #e0e0e0  (RGB: 224, 224, 224) - Primary text
UI MUTED:          #a0a0a0  (RGB: 160, 160, 160) - Secondary text
ACCENT:            #2b5aa0  (RGB: 43, 90, 160)   - Interactive elements
```

### Palette Usage Rules

**Terrain Tiles**
- Use primary palette for base (GRASS GREEN, BROWN DIRT, PALE GREEN)
- Add texture with dark variants
- Variation through shadow placement

**Creatures**
- Base: CREATURE BLUE (100% of body)
- Shadows: DARK BLUE (20-30% of surface)
- Highlights: LIGHT BLUE (10-15% of surface)
- Details: ACCENT BLUE (features, pupils)
- Eyes: WHITE + BLACK (always)

**Features**
- Each feature has ONE accent color
- Blend with base creature blue for integration
- Use color to signal different genetic traits

**Environment Objects**
- Trees: Browns + Dark Greens (always)
- Flowers: Each flower ONE color (from flower palette)
- Apples: APPLE RED (always)
- Stones: Grays + Browns (future)

---

## 3. TYPOGRAPHY

### Font Specifications

**UI Font**: Pixelated / Pixel-style font (7-8px bitmap)
```
Family: "Commodore 64 Pixel" or equivalent
Sizes:  8px (small), 10px (normal), 12px (headings)
Weight: Regular (no bold in pixel font)
```

**Rendered Text Size**:
```
8px  - Stats, descriptions, small labels
10px - Normal UI text, event log
12px - Titles, important numbers
```

### Text Rendering Rules

- **Always anti-aliased**: No
- **Pixel-perfect alignment**: Yes (snap to grid)
- **Color**: Match UI palette (e.g., UI TEXT #e0e0e0)
- **Contrast**: Minimum 4.5:1 ratio
- **No shadows**: Keep text clean

---

## 4. PIXEL GRID & SIZING

### Base Unit

```
TILE SIZE:     32x32 pixels (standard environment tile)
CREATURE BASE: 24x32 pixels (normal organism)
SCALE FACTOR:  2x (display at 2x original size in viewport)
```

### Size Categories

```
MICRO:      4x4 px   (pupils, small details)
TINY:       6x6 px   (apples, small features)
SMALL:      8x8 px   (flowers, decorations)
MEDIUM:     12x12 px (rocks, small objects)
STANDARD:   16x16 px (tiles, medium objects)
LARGE:      24x32 px (creatures - normal)
XLARGE:     32x40 px (creatures - large)
MEGA:       48x48 px (trees)
```

### Grid Rules

- **Always snap to 4-pixel grid** minimum
- **Prefer powers of 2** (8, 16, 32, 64)
- **Proportional scaling**: If 24x32 → scale to 12x16 (half)
- **No sub-pixel rendering**: Crisp edges only
- **Consistent padding**: 2-4px between elements

### Animation Frame Dimensions

```
Creature walk cycles:  24x32 px (8 directions × 8 frames)
Tree sway:            48x48 px (3-4 frames)
Flower tremor:        8x8 px (2 frames)
Spinner (thinking):   8x8 px (8 frames)
```

---

## 5. CHARACTER DESIGN

### Organism - Base Template

**Dimensions**: 24x32 pixels (standard)

**Structure** (top to bottom):

```
┌──────────────────────┐  Row 0
│    [Eyes Space]      │  Rows 1-4   (head region)
├──────────────────────┤
│   [Body Main]        │  Rows 5-18  (torso)
├──────────────────────┤
│   [Legs/Base]        │  Rows 19-31 (lower body)
└──────────────────────┘
```

### Body Composition

**Eyes** (Row 2-3):
```
Pattern: [WH] [BP] [2px gap] [WH] [BP]
- WH = 2x2 white pixel
- BP = 1x1 black pupil
- Position: X=4-5 and X=10-11
- Y = 6-7
- Pupils can move ±1 pixel based on animation
```

**Main Body** (Rows 5-18):
```
Shape: Rounded blob, 16px wide at widest
- Row 5-6:   8px wide (top)
- Row 7-16:  16px wide (main body)
- Row 17-18: 12px wide (tapering)

Color: Base CREATURE BLUE
Shadow: DARK BLUE on left/bottom (2-3 pixels)
Highlight: LIGHT BLUE on top/right (1-2 pixels)

Detail: Small curved segments showing "muscle" ridges
- 4-5 horizontal shadow lines for texture
- Spacing: every 2-3 rows
```

**Lower Body** (Rows 19-31):
```
Small base or legs - 12px wide
Taper to point at bottom
Color: CREATURE BLUE + DARK BLUE shadows
```

### Feature Specifications

#### Antena
```
Type:      EXTRUDED
Size:      2px wide × 3-4px tall
Color:     ANTENA RED (#e63946)
Position:  Top-center (X=11-12, Y=-2 to 1)
Animation: FLEX - sways ±1px left/right
Frames:    2 (left, right)
Timing:    1 frame = 0.1s, loops
```

#### Horns
```
Type:      SIDE PROTRUSION
Size:      2x2 px each
Color:     HORN BROWN (#8b4513)
Position:  Left (X=-1, Y=3) and Right (X=23, Y=3)
Animation: STATIC (no movement)
Purpose:   Visual distinction, turn speed bonus
```

#### Long Legs
```
Type:      LOWER EXTENSION
Size:      2px wide × 3px tall each
Color:     LEG TEAL (#5a7a8a)
Position:  X=3 and X=11 (below body)
Animation: SYNCED with walk cycle
- Frames:  2 (up, down)
- Timing:  Alternates with movement
Purpose:   Movement speed visual indicator
```

#### Bumps (Guzki)
```
Type:      TEXTURE OVERLAY
Size:      2x2 px each
Color:     BUMP SHADE (#3a6aa0)
Count:     3-4 bumps scattered on body
Position:  X=3, X=8, X=12 at Y=8-12
Animation: PULSE (fades in/out)
- Frames:  2 (visible, faded)
- Timing:  0.15s per frame
Purpose:   Energy capacity visual
```

#### Wings
```
Type:      SIDE APPENDAGE
Size:      1px wide × 6px tall
Color:     WING CYAN (#4a90e2)
Position:  Left (X=-2, Y=6) and Right (X=25, Y=6)
Animation: FLUTTER
- Frames:  3 (up, mid, down)
- Timing:  0.2s per frame
Purpose:   Detection range visual indicator
```

### Size Variants

**Small (16x24)**
- All features 75% size
- Eyes: 1px pupils instead of 1x1
- Body proportions maintained
- Used for younger/smaller creatures

**Normal (24x32)** ← STANDARD
- All features as specified above
- Recommended default

**Large (32x40)**
- All features 133% size
- Eyes: 3x3 instead of 2x2 (bigger presence)
- More visible texture detail
- Used for elder/dominant creatures

---

## 6. TERRAIN & ENVIRONMENT

### Terrain Tiles (16x16 standard)

#### Grass Tile
```
Base:     GRASS GREEN (#4a7c59) - full 16x16
Detail:   DARK GREEN (#2d5016) spots (random placement)
- Size:   2x2 to 3x3 px each
- Count:  3-4 per tile
- Purpose: Break uniformity, add texture

Variant: Add LIGHT GREEN (#6ba75a) highlight
- Size:   1-2px
- Position: Top-left corner
- Purpose: Subtle directional light

Animation: Grass sway (2 frames)
- Frame 1: Base + detail at Y=0
- Frame 2: Detail offset +1px left
- Timing: 0.2s per frame
```

#### Dirt Tile
```
Base:     BROWN DIRT (#8b6f47) - full 16x16
Detail:   DARK BROWN (#6b4423) cracks
- Size:   1-2px, irregular patterns
- Count:  4-6 per tile
- Purpose: Show earth/soil texture

Highlight: LIGHT TAN (#c4a57b)
- Size:   1-2px
- Position: Scattered corners
- Purpose: Subtle depth

Variant: Mix LIGHT TAN + BROWN DIRT 50/50
```

#### Flower Field Tile
```
Base:     PALE GREEN (#a4c595) - full 16x16
Detail:   Small flower dots (1-2px each)
- Colors: Mix of flower palette colors
- Count:  4-6 flowers per tile
- Pattern: Scattered, not aligned

Animation: Optional subtle shimmer
- Slight color variation frame-to-frame
```

#### Hill/Slope Tile
```
Base:     MIX of GRASS GREEN + BROWN DIRT
- Pattern: Diagonal gradient (bottom-left darker)
- Top-right: Lighter (LIGHT GREEN or LIGHT TAN)
- Purpose: Visual indication of height

Shadow:   DARK GREEN (#2d5016) bottom edge (2px)
- Gives 3D depth feeling
- Shows light direction
```

### Environmental Objects

#### Trees (48x48 px)

**Trunk** (12px wide × 16px tall):
```
Color:    TRUNK DARK (#6b4423) main
Shade:    TRUNK LIGHT (#8b5a3c) for right edge (1-2px)
Position: Center-bottom (X=18, Y=32)
Shape:    Vertical rectangle with slight taper
```

**Foliage** (32px wide × 20px tall):
```
Base:     FOLIAGE DARK (#2d5016)
Shape:    Rounded blob (think classic GBA tree)
- Row 0-4:   20px wide (top)
- Row 5-14:  28px wide (bulge)
- Row 15-19: 24px wide (taper)

Mid-tone:  FOLIAGE MID (#3d6b1f)
- Internal shading (right side, 2-3px wide)
- Gives dimensional look

Animation: Leaf sway (3-4 frames)
- Frame 1: Base position
- Frame 2: Offset -1px left
- Frame 3: Offset +1px right
- Frame 4: Return to base
- Timing: 0.15s per frame
```

**Apples on Tree** (6x6 each):
```
Color:    APPLE RED (#e63946)
Count:    3-5 per tree (scatter placement)
Position: On foliage, visible gaps
- Apple 1: X=6, Y=8
- Apple 2: X=18, Y=10
- Apple 3: X=28, Y=12
- Etc. (vary placement)

Shine:    1px white highlight (top-left)
Animation: Subtle rotation (2 frames)
- Frame 1: Normal
- Frame 2: Rotated +45° perspective (1px offset)
- Timing: 0.3s per frame
```

**Tree Shadow** (32x4 px below):
```
Color:    DARK GREEN (#2d5016) at 40% opacity
Shape:    Ellipse-like (rounded rectangle)
Position: Directly under foliage
Purpose:  Ground anchoring, depth

Animation: Matches tree sway
- Offset with parent tree movement
```

#### Flowers (8x8 px)

**Base Pattern** (all flower types):
```
Center:   Yellow core (2x2 px, FLOWER CENTER #ffeb3b)
Petals:   5 petals around center
- Size:   2x2 px each
- Arrangement: Circle around center
- Offset: ±1px from center

Animation: Tremor (2 frames)
- Frame 1: Normal position
- Frame 2: Offset ±0.5px (all petals)
- Timing: 0.2s per frame
```

**Flower Color Variants**:
```
Type 1: PINK      (#ffb4d6) - 20% of flowers
Type 2: GOLDEN    (#ffd700) - 20% of flowers
Type 3: PURPLE    (#b19cd9) - 20% of flowers
Type 4: MAGENTA   (#ff69b4) - 20% of flowers
Type 5: CREAM     (#fffacd) - 20% of flowers
```

#### Stones (Placeholder for v2)

```
Size:     12x12 px (small) or 32x32 px (large)
Color:    Grays + dark browns (future implementation)
Purpose:  Obstacles, visual interest
Timeline: Post-MVP
```

---

## 7. ANIMATION GUIDELINES

### Creature Walk Cycle (8 directions, 8 frames each)

**Directions** (8-directional):
```
Right:        0°
Down-Right:   45°
Down:         90°
Down-Left:    135°
Left:         180°
Up-Left:      225°
Up:           270°
Up-Right:     315°
```

**Frame Sequence per Direction**:
```
Frame 0: Neutral pose (standing)
Frame 1: Leg 1 extended (30% forward)
Frame 2: Legs separated (60% stride)
Frame 3: Leg 2 extended (85% forward)
Frame 4: Neutral (opposite leg position)
Frame 5: Leg 2 extended (30% forward)
Frame 6: Legs separated (60% stride)
Frame 7: Leg 1 extended (85% forward)

[Returns to Frame 0 - loop continuous]
```

**Body Animation**:
```
Bob up/down: ±1px per stride
- Frame 0,4: Y=0 (center)
- Frame 2,6: Y=-1 (slight jump)
- Frame 1,3,5,7: Y=-0.5 (in-between)

Rotation: None (maintain facing direction)
Scale: None (consistent size)
```

**Timing**:
```
Frame duration: 125ms (8 frames per second)
Overlap with world ticks: Smooth transition
- World tick = 100ms
- Animation frame = 125ms
- Slight mismatch creates smooth feel (no jitter)
```

### Thinking Animation (Spinner/Krętiolek)

**Design**:
```
Type:     Spinning circle
Size:     8x8 px
Color:    GOLDEN (#ffd700) with glow effect
Position: Above creature head (-4px offset)

Glow:     GOLDEN at 50% opacity
- Radiates 2px around spinner
```

**Frames** (8 frames):
```
Frame 0: Top-right (45°)
Frame 1: Right (90°)
Frame 2: Bottom-right (135°)
Frame 3: Bottom (180°)
Frame 4: Bottom-left (225°)
Frame 5: Left (270°)
Frame 6: Top-left (315°)
Frame 7: Top (360° / 0°)

Rotation: 45° per frame
```

**Timing**:
```
Frame duration: 100ms (10 frames per second)
Continuous rotation (no pause)
Visible for 1-5 world ticks (100-500ms)
```

### Eating Animation

**Frames** (3 frames):
```
Frame 0: Mouth closed (normal)
Frame 1: Mouth open (30% expansion)
Frame 2: Mouth opening (60% expansion)

Mouth: Horizontal ellipse expansion
- Center: Bottom of creature face
- Max width: 80% of creature width
```

**Timing**:
```
Frame duration: 150ms
Sequence: 0 → 1 → 2 → 0 (loop 2x)
Total: 900ms eating animation
```

### Reproduction Animation

**Frames** (4 frames):
```
Frame 0: Normal size
Frame 1: 110% scale
Frame 2: 120% scale (maximum swell)
Frame 3: 110% scale

Pulse effect: Body expands/contracts
Center: Creature center (no movement)
```

**Timing**:
```
Frame duration: 200ms
Sequence: 0 → 1 → 2 → 3 → 0 (no loop, play once)
Total: 800ms reproduction animation
```

**Glow Effect**:
```
Color:    Creature's feature color
Opacity:  0% → 100% → 100% → 50% → 0%
Duration: Matches pulse frames
Purpose:  Highlight moment of reproduction
```

### Dying Animation

**Frames** (6 frames):
```
Frame 0: Normal color (start)
Frame 1: 80% opacity, slight desaturation
Frame 2: 60% opacity, more desaturation
Frame 3: 40% opacity, grayscale beginning
Frame 4: 20% opacity, full grayscale
Frame 5: 0% opacity (invisible)
```

**Color Shift**:
```
Desaturation curve:
- Frame 0: 0% gray (full color)
- Frame 3: 50% gray (half desaturated)
- Frame 5: 100% gray (full grayscale)
```

**Particle Effect**:
```
Type:     Fade-out sparkles
Count:    4-6 particles
Direction: Scatter outward
Duration: Matches animation frames
Color:    Feature color → white → transparent
```

**Timing**:
```
Frame duration: 150ms
Sequence: 0 → 1 → 2 → 3 → 4 → 5 (play once, no loop)
Total: 900ms dying animation
```

### Feature Animations

#### Antena Flex
```
Animation: Side-to-side sway
Movement: ±1px horizontal
Frames:   2 (left, right)
Timing:   0.15s per frame
```

#### Legs Synced Walk
```
Animation: Moves with walk cycle
Movement: Up/down following stride
Frames:   2 (high, low)
Timing:   Synced with walk frames 1,2,3,5,6,7
```

#### Bumps Pulse
```
Animation: Fade in/out
Opacity:  100% → 40% → 100%
Frames:   2 (visible, faded)
Timing:   0.2s per frame
```

#### Wings Flutter
```
Animation: Up/down flapping
Movement: ±2px vertical
Frames:   3 (up, mid, down)
Timing:   0.15s per frame
```

---

## 8. UI DESIGN SYSTEM

### Observatory Interface

**Background**: Dark theme (UI BACKGROUND #1a1a1a)

**Components**:
- Panels: UI SURFACE (#2a2a2a) with UI BORDER (#404040)
- Text: UI TEXT (#e0e0e0) for primary, UI MUTED (#a0a0a0) for secondary
- Accents: CREATURE BLUE (#2b5aa0) for interactive elements

### World Viewport

**Canvas Background**: Solid color (approximate SKY - for future)
```
Sky color: #87ceeb (when implemented)
Currently: Match darkest terrain (#2a4a2a)
```

**Camera**:
- Pan: Smooth scrolling
- Zoom: 1x, 2x, 3x (no fractional)
- Follow: Creature-centered with smooth tracking

### Stats Panels

**Metric Cards**:
```
Layout:  4-column grid
Card:    UI SURFACE + 1px UI BORDER
Font:    10px pixel font, UI TEXT
Spacing: 8px gap between cards

Content:
- Label (small, UI MUTED)
- Number (larger, UI TEXT, bold-equivalent)
- Unit (tiny, UI MUTED)
```

**Event Log**:
```
Font:    8px pixel font
Color:   UI TEXT
Max width: 40 characters
Max height: 10 lines (scrollable)
Timestamp: [HH:MM] format
```

---

## 9. ASSET SPECIFICATIONS

### Character Sprites

**Creature Base**:
```
File:      creature_base_normal.png
Dimensions: 24x32 px (1x scale)
Format:    PNG with transparency
Variants:  3 sizes (small 16x24, normal 24x32, large 32x40)
Frames:    8 directions × 8 walk frames = 64 frames total
Layout:    Horizontal strip (64 wide, 32 tall minimum)
```

**Creature Features**:
```
Files:     creature_feature_antena.png
           creature_feature_horns.png
           creature_feature_legs.png
           creature_feature_bumps.png
           creature_feature_wings.png

Dimensions: 24x32 px per feature (matches base)
Format:    PNG with transparency
Frames:    Per feature specification
Layout:    Horizontal strip (frames width × 32 px)
```

**Creature Animations**:
```
Files:     creature_state_thinking.png (spinner)
           creature_state_eating.png
           creature_state_reproducing.png
           creature_state_dying.png

Dimensions: 8x8 px (thinking), 24x32 px (others)
Frames:    Per animation specification
```

### Environment Sprites

**Terrain Tiles**:
```
File:       terrain_tiles.png
Dimensions: 16x16 px per tile
Types:      Grass, Dirt, Flowers, Hills (4 types)
Variants:   3-4 variations per type (for visual variety)
Layout:     Grid: 4 types × 4 variants = 16 tiles (64x64 total)
Format:     PNG with no transparency
```

**Terrain Animation**:
```
File:       terrain_animation_grass.png
Dimensions: 16x16 px per frame
Frames:     2-4 frames (grass sway)
Layout:     Horizontal strip
```

**Trees**:
```
File:       environment_tree.png
Dimensions: 48x48 px (base tree)
Frames:     3-4 frames (leaf sway animation)
Layout:     Horizontal strip
Format:     PNG with transparency

Variants:   Future (different tree types)
```

**Flowers**:
```
File:       environment_flower_set.png
Dimensions: 8x8 px per flower
Types:      5 colors (pink, gold, purple, magenta, cream)
Frames:     2 frames per flower (tremor animation)
Layout:     5 flowers × 2 frames = 10 tiles (80x8 total)
Format:     PNG with transparency
```

**Apples**:
```
File:       environment_apple.png
Dimensions: 6x6 px
Frames:     2 frames (rotation animation)
Layout:     Horizontal strip (12x6 total)
Format:     PNG with transparency
```

### UI Assets

**Sprites**:
```
File:       ui_icons.png
Contents:   Cursor, selection ring, buttons, markers
Format:     PNG with transparency
```

---

## 10. DO'S AND DON'Ts

### DO ✅

- ✅ Use exact hex colors from palette (no approximations)
- ✅ Snap all pixels to 4px grid minimum
- ✅ Maintain consistent line thickness (1-2px)
- ✅ Use hard edges (crisp, no anti-aliasing)
- ✅ Layer colors for depth (shadows + highlights)
- ✅ Test at 1x and 2x scale
- ✅ Keep creature readable at 24x32
- ✅ Vary terrain with detail pixels
- ✅ Animate smoothly (no jarring jumps)
- ✅ Reference Throungles for inspiration
- ✅ Use simple shapes (circles, squares, triangles)
- ✅ Leave negative space (don't overcrowd)
- ✅ Make features immediately recognizable

### DON'T ❌

- ❌ Don't use colors outside palette (no custom mixing)
- ❌ Don't make creatures bigger than 32x40
- ❌ Don't use gradients or blending
- ❌ Don't add photorealistic details
- ❌ Don't animate too fast (>10 fps is jittery)
- ❌ Don't make features tiny/hard to see
- ❌ Don't copy Throungles exactly (inspired by, not clone)
- ❌ Don't add drop shadows or glows (too modern)
- ❌ Don't rotate creatures (snap to 8 directions)
- ❌ Don't scale features non-uniformly
- ❌ Don't add speech bubbles or text in sprites
- ❌ Don't make world too busy (breathing room matters)
- ❌ Don't use more than 4 colors per 16x16 tile

---

## 11. IMPLEMENTATION CHECKLIST

### Before Pixel Art Production

- [ ] Approve this style guide fully
- [ ] Print color palette reference
- [ ] Set up Aseprite/Piskel with palette
- [ ] Create template sprites (outline dimensions)
- [ ] Test color values on screen
- [ ] Reference Throungles assets

### Creature Creation

- [ ] Base character (24x32) created
  - [ ] Eyes designed
  - [ ] Body shape finalized
  - [ ] Shadow/highlight placement
- [ ] 8 walk directions (8 frames each) = 64 frames
- [ ] All 5 feature variants created
  - [ ] Antena (with flex animation)
  - [ ] Horns (static)
  - [ ] Legs (with walk sync)
  - [ ] Bumps (with pulse)
  - [ ] Wings (with flutter)
- [ ] All state animations created
  - [ ] Thinking (8 frames spinner)
  - [ ] Eating (3 frames)
  - [ ] Reproducing (4 frames + glow)
  - [ ] Dying (6 frames with fade)
- [ ] Size variants (small 16x24, large 32x40)
- [ ] All sprites tested in game engine

### Environment Creation

- [ ] Terrain tiles (4 types × 4 variants)
- [ ] Terrain animation (grass sway, 2-4 frames)
- [ ] Tree sprite (48x48, 3-4 frames)
- [ ] Tree shadow (32x4)
- [ ] Flowers (5 types × 2 frames)
- [ ] Apples (2 frames)
- [ ] All sprites tested for visual coherence

### Quality Assurance

- [ ] All colors match hex values exactly
- [ ] All sprites are pixel-perfect (no gaps)
- [ ] Animations are smooth (no jitter)
- [ ] Visual hierarchy is clear
- [ ] World feels cohesive (one style)
- [ ] Creatures are readable at all zoom levels
- [ ] Features are immediately recognizable
- [ ] Performance is acceptable (no lag from rendering)

---

## 12. FINAL SIGN-OFF

### Version History

| Version | Date       | Changes |
|---------|------------|---------|
| 1.0     | 2026-09-11 | Initial complete style guide |

### Approval

```
Design Approved:  [ ] YES  [ ] REVISIONS NEEDED
Designer:         ___________________
Date:             ___________________

Implementation Ready: [ ] YES  [ ] NO
Developer Lead:       ___________________
Date:                 ___________________
```

---

## APPENDIX: COLOR REFERENCE CARD

```
TERRAIN:
  Grass Green       #4a7c59
  Dark Green        #2d5016
  Light Green       #6ba75a
  Brown Dirt        #8b6f47
  Dark Brown        #6b4423
  Light Tan         #c4a57b

CREATURES:
  Creature Blue     #2b5aa0
  Dark Blue         #1e4073
  Light Blue        #4a7cba
  Accent Blue       #5a9fd4

FEATURES:
  Antena Red        #e63946
  Horn Brown        #8b4513
  Leg Teal          #5a7a8a
  Bump Shade        #3a6aa0
  Wing Cyan         #4a90e2

FLOWERS:
  Pink              #ffb4d6
  Golden            #ffd700
  Purple            #b19cd9
  Magenta           #ff69b4
  Cream             #fffacd

DETAILS:
  White             #ffffff
  Black             #000000
  Apple Red         #e63946
  Flower Center     #ffeb3b
```

---

**End of Art Style Guide**

This document is the master reference for all visual assets in UNKNOWN.
All pixel art production must adhere to this guide.
Changes require re-approval and version update.

