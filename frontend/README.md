# Authentic Lens Tool

Build a clean, modern, fully functional website for **GAIA Detector**, a platform that analyzes text, images, and videos to estimate whether content is AI-generated or human-created.

### 1. Mandatory Design Resources

Read and apply the relevant principles from both resources:

* UI/UX Pro Max: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
* Apple Design Skill: https://github.com/emilkowalski/skills/blob/main/skills/apple-design/SKILL.md

Use their guidance for layout, typography, spacing, accessibility, component design, and interactions. Do not simply mention these resources; apply their principles.

### 2. Visual Identity

Use a distinctive **Acid & Graphite** design.

* Background: Warm Chalk `#F2F0E8`
* Primary text: Carbon Black `#191B18`
* Accent: Acid Chartreuse `#D5F15B`
* Secondary surfaces: Pale Concrete `#E5E3D9`
* Borders: Stone Grey `#C9C8BE`
* Dark sections: Graphite `#242621`

Avoid galaxy colors, purple-blue gradients, excessive neon, glassmorphism, robotic visuals, and generic AI website aesthetics.

The design should feel natural, premium, minimal, and human-designed.

### 3. Extremely Minimal Text

**Use only essential text throughout the website.**

* No long paragraphs or unnecessary descriptions.
* No excessive marketing content, testimonials, statistics, or feature explanations.
* No oversized headings.
* Use moderate typography and generous whitespace.
* Keep navigation, labels, buttons, and instructions short.
* Do not repeat information across sections.

Suggested homepage:

**GAIA DETECTOR**

*Know what you're looking at.*

Analyze text, images, and videos.

`Start Analysis`

Nothing more is needed in the hero section.

### 4. Clean Layout and Alignment

* Use a consistent grid and maximum content width.
* Align navigation, headings, buttons, upload areas, and result panels.
* Maintain consistent spacing, margins, padding, and component heights.
* Avoid clutter, overlapping elements, unnecessary cards, and irregular gaps.
* Keep the analysis workspace centered and organized.
* Make every important action immediately accessible.
* Ensure results are prominently displayed without unnecessary scrolling.

The website must remain properly aligned on desktop, tablet, and mobile.

### 5. Functional Detection Workspace

Provide three simple modes:

**TEXT | IMAGE | VIDEO**

**Text:** A working text input, character or word count, Analyze button, and Clear action.

**Image:** Working file selection, drag-and-drop, preview, validation, and removal.

**Video:** Working file selection, drag-and-drop, preview where supported, validation, and removal.

Use the actual backend endpoints and supported formats whenever available.

### 6. Clear Results

Display the actual detection result prominently, followed by a meaningful score if the model provides one.

Use concise labels such as:

* Likely AI-generated
* Likely human-created
* Inconclusive, if supported

Include an `Analyze Another` button.

Do not invent scores, results, explanations, or confidence percentages. Never pretend a failed request succeeded.

### 7. Subtle Animations

Use a minimal chartreuse signal line as the website's signature visual.

Add smooth transitions for content selection, uploading, loading, and displaying results.

Keep animations subtle, functional, and fast. Respect reduced-motion preferences. Never let animations delay or obscure results.

### 8. Full Functionality

Inspect the existing project and backend capabilities before implementation.

* Connect all three detectors to real API endpoints when available.
* Implement input validation, file validation, loading states, and error handling.
* Ensure every button and navigation element works.
* Prevent duplicate submissions and stale results.
* Preserve existing authentication, routing, and working functionality.
* Never substitute fake analysis results for a missing backend.

If the backend is unavailable, build the interface with a clear integration structure and explicitly identify what remains unconnected.

### 9. Final Testing

Test every interaction, detector workflow, API request, result display, animation, and responsive layout. Fix alignment issues, broken buttons, console errors, and failed requests.

### FINAL PRIORITIES

1. Fully functional website.
2. Minimal text.
3. Perfect alignment and spacing.
4. Simple, intuitive navigation.
5. Clearly visible results.
6. Distinctive colors and subtle animations.
7. Responsive and accessible design.

**Final goal:** A clean, uncluttered, easy-to-use AI detection platform that feels premium and creative without looking robotic. Every element must have a purpose, and functionality must take priority over decoration.

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/c70ca3fd-ec41-48e0-a847-3bfcbd9bc5f8).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
