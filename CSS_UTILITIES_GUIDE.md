# ZConnect CSS Utilities Guide

## Overview
This document lists all Bootstrap-like utility classes now available in ZConnect's CSS framework. These utilities follow Bootstrap conventions and can be used throughout the application to quickly style elements without writing custom CSS.

---

## Spacing Utilities

### Margins
- `m-0` to `m-5` — Apply equal margin on all sides
- `mt-0` to `mt-5` — Top margin
- `mb-0` to `mb-5` — Bottom margin
- `ml-1` to `ml-4` — Left margin
- `mr-1` to `mr-4` — Right margin
- `mx-auto` — Center horizontally

**Values:** 0=0px, 1=4px, 2=8px, 3=12px, 4=16px, 5=20px

### Padding
- `p-0` to `p-5` — All sides
- `pt-1` to `pt-4` — Top padding
- `pb-1` to `pb-4` — Bottom padding
- `pl-1` to `pl-4` — Left padding
- `pr-1` to `pr-4` — Right padding
- `px-2` to `px-4` — Horizontal (left + right)
- `py-1` to `py-4` — Vertical (top + bottom)

---

## Display & Layout

### Display Properties
- `d-none` — Hide element (display: none)
- `d-block` — Block element
- `d-inline` — Inline element
- `d-inline-block` — Inline-block
- `d-flex` — Flexbox container
- `d-grid` — Grid container

### Flex Direction
- `d-flex-row` — Row direction (default)
- `d-flex-col` — Column direction

### Flex Alignment (Justify)
- `justify-start` — Align to start
- `justify-center` — Center content
- `justify-end` — Align to end
- `justify-between` — Space between
- `justify-around` — Space around
- `justify-evenly` — Space evenly

### Flex Alignment (Align)
- `align-start` — Align items to start
- `align-center` — Center items vertically
- `align-end` — Align items to end
- `align-stretch` — Stretch items
- `items-center` — Shortcut for align-center

### Gaps
- `gap-0` to `gap-5` — Space between flex items
  - 0=0px, 1=4px, 2=8px, 3=12px, 4=16px, 5=20px

### Flex Growth
- `flex-1` — Grow to fill available space
- `flex-grow` — Enable flex-grow: 1
- `flex-shrink` — Enable flex-shrink: 1
- `flex-wrap` — Allow wrapping
- `flex-nowrap` — Prevent wrapping

---

## Text Utilities

### Text Size
- `text-xs` — 11px
- `text-sm` — 12px
- `text-base` — 14px
- `text-lg` — 16px
- `text-xl` — 18px
- `text-2xl` — 20px
- `text-3xl` — 24px

### Text Color
- `text-1` — Primary text color (var(--text-1))
- `text-2` — Secondary text color (var(--text-2))
- `text-3` — Tertiary text color (var(--text-3))
- `text-muted` — Muted/gray text
- `text-accent` — Accent color
- `text-success` — Success color (green)
- `text-danger` — Error color (red)
- `text-warn` — Warning color (yellow)
- `text-white` — White text
- `text-dark` — Dark text

### Text Alignment
- `text-left` — Left align
- `text-center` — Center align
- `text-right` — Right align
- `text-justify` — Justify

### Font Weight
- `fw-normal` — 400
- `fw-500` — 500 (medium)
- `fw-600` — 600 (semibold)
- `fw-bold` — 700 (bold)
- `fw-900` — 900 (very bold)

### Text Decoration
- `italic` — Italic text
- `not-italic` — Normal style
- `underline` — Underlined text
- `no-underline` — Remove underline
- `line-through` — Strikethrough text

### Text Transform
- `uppercase` — ALL CAPS
- `lowercase` — lowercase
- `capitalize` — Capitalize First
- `normal-case` — None

### Letter Spacing
- `tracking-tight` — -0.5px
- `tracking-normal` — 0px
- `tracking-wide` — 0.5px

---

## Width & Height

### Width
- `w-full` — 100%
- `w-auto` — auto
- `w-1/2` — 50%
- `w-1/3` — 33.333%
- `w-2/3` — 66.666%
- `w-1/4` — 25%
- `w-3/4` — 75%

### Height
- `h-full` — 100%
- `h-auto` — auto
- `h-screen` — 100vh (full viewport)

### Max/Min
- `min-h-screen` — min-height: 100vh
- `max-w-full` — max-width: 100%
- `max-w-sm` — 384px
- `max-w-md` — 512px
- `max-w-lg` — 640px
- `max-w-xl` — 768px

---

## Background Colors

### Solid Colors
- `bg-base` — Main background (var(--bg-base))
- `bg-sidebar-l` — Left sidebar
- `bg-sidebar-r` — Right sidebar
- `bg-content` — Content area
- `bg-hover` — Hover state
- `bg-active` — Active state
- `bg-accent` — Accent color (purple)
- `bg-danger` — Error red
- `bg-success` — Success green
- `bg-warn` — Warning yellow
- `bg-white` — White
- `bg-black` — Black
- `bg-transparent` — Transparent
- `bg-accent-light` — Light accent variant

---

## Border Utilities

### Border
- `border` — Full border (1px, all sides)
- `border-t` — Top border
- `border-r` — Right border
- `border-b` — Bottom border
- `border-l` — Left border
- `border-0` — No border

### Border Color
- `border-accent` — Accent color border
- `border-danger` — Red border
- `border-success` — Green border

### Border Radius
- `rounded` — 6px
- `rounded-sm` — 3px
- `rounded-md` — 8px
- `rounded-lg` — 12px
- `rounded-xl` — 16px
- `rounded-2xl` — 20px
- `rounded-full` — 50% (circle)

### Partial Radius
- `rounded-t` — Top corners
- `rounded-b` — Bottom corners
- `rounded-l` — Left corners
- `rounded-r` — Right corners

---

## Shadow Utilities

- `shadow` — Light shadow
- `shadow-sm` — Very light shadow
- `shadow-md` — Medium shadow
- `shadow-lg` — Large shadow
- `shadow-xl` — Extra large shadow
- `shadow-none` — No shadow

---

## Overflow

### Overflow Behavior
- `overflow-auto` — Show scrollbar when needed
- `overflow-hidden` — Hide overflow
- `overflow-visible` — Show overflow
- `overflow-scroll` — Always show scrollbar

### Axis-Specific
- `overflow-x-auto` — Horizontal scroll
- `overflow-x-hidden` — Hide horizontal overflow
- `overflow-y-auto` — Vertical scroll
- `overflow-y-hidden` — Hide vertical overflow

---

## Positioning

### Position Type
- `relative` — position: relative
- `absolute` — position: absolute
- `fixed` — position: fixed
- `sticky` — position: sticky

### Position Values
- `inset-0` — All sides to 0 (full coverage)
- `top-0` / `top-1` — Top position
- `right-0` / `right-1` — Right position
- `bottom-0` / `bottom-1` — Bottom position
- `left-0` / `left-1` — Left position

---

## Opacity

- `opacity-0` — 0% opacity (invisible)
- `opacity-25` — 25% opacity
- `opacity-50` — 50% opacity
- `opacity-75` — 75% opacity
- `opacity-100` — 100% opacity (fully visible)

---

## Transitions & Animations

### Transitions
- `transition` — Apply transition animation
- `transition-all` — Transition all properties

### Duration
- `duration-100` — 100ms
- `duration-200` — 200ms
- `duration-300` — 300ms

---

## Cursor & Interaction

- `cursor-pointer` — Pointer/hand cursor
- `cursor-default` — Default cursor
- `cursor-not-allowed` — Not-allowed/disabled cursor

---

## User Selection

- `select-none` — Disable text selection
- `select-text` — Allow text selection

---

## Visibility

- `visible` — Element is visible
- `invisible` — Element is invisible (but takes space)
- `hidden` — Element is hidden (display: none)

---

## Quick Examples

### Centered Container
```html
<div class="d-flex flex-center p-4 rounded-lg bg-content">
  <span class="text-center fw-bold">Centered Content</span>
</div>
```

### Card
```html
<div class="bg-sidebar-r rounded-lg p-4 shadow-md border-l-4 border-accent">
  <h3 class="text-lg fw-bold text-1 mb-2">Title</h3>
  <p class="text-sm text-muted">Description here</p>
</div>
```

### Flex Navigation
```html
<nav class="d-flex justify-between align-center p-3 bg-base border-b">
  <span class="fw-bold">Logo</span>
  <div class="d-flex gap-2">
    <a href="#" class="px-3 py-2 rounded hover:bg-hover">Link</a>
  </div>
</nav>
```

### Responsive Grid
```html
<div class="d-grid gap-4">
  <div class="bg-content rounded p-4">Item 1</div>
  <div class="bg-content rounded p-4">Item 2</div>
  <div class="bg-content rounded p-4">Item 3</div>
</div>
```

---

## Color Palette Reference

| Variable | Light Theme | Dark Theme |
|----------|-----------|-----------|
| --text-1 | Primary | #e0e2f0 |
| --text-2 | Secondary | #9da3b4 |
| --text-3 | Tertiary | #5c6070 |
| --accent | Purple | #7c5cbf |
| --success | Green | #23a55a |
| --danger | Red | #f23f43 |
| --warn | Yellow | #f0b232 |
| --bg-base | Background | #1a1c2a |
| --bg-sidebar-l | Sidebar L | #111220 |
| --bg-sidebar-r | Sidebar R | #1e2030 |
| --bg-content | Content | #252736 |

---

## Spacing Scale

```
0px  = m-0, p-0
4px  = m-1, p-1
8px  = m-2, p-2
12px = m-3, p-3
16px = m-4, p-4
20px = m-5, p-5
```

---

## Usage Tips

1. **Combine classes** - Stack multiple utilities: `d-flex justify-center align-center p-4`
2. **Responsive** - Use media queries with utility classes for responsive design
3. **Override** - More specific selectors always win
4. **Consistency** - Use the predefined scale for consistent spacing
5. **Readability** - Use semantic class names where clarity is important

---

**Last Updated:** June 8, 2026  
**Total Utilities:** 200+
