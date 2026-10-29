# Juking Style 3D UI

## Amendment to the existing Juku Style protocol

This does **not replace Juku Style**. We already have an existing Juku Style design protocol. Treat everything below as an **additional spatial/interaction layer within Juku Style**, preserving all existing Juku Style rules unless they directly conflict with a later Chairman ruling.

## Reference implementation

Use **HyperSolid** as the primary live reference for this added spatial layer:

**https://tarasovvitalii.com/demos/hypersolid/**

Keep that full URL in our documentation so future agents can revisit the actual site and inspect the visual language, depth, transitions, movement, pacing, and overall construction rather than relying on a written description alone.

## Added Juku Style spatial layer

The goal is to make our products feel like **lightweight interactive 3D environments**, closer to a lightweight game or cinematic spatial interface than a conventional website.

Core principles:

- Build primarily as a **lightweight PWA/web app** unless native capabilities are genuinely required.
- Use HyperSolid as the reference for **depth, cinematic movement, layered environments and the feeling of travelling through an interface**.
- Go beyond HyperSolid by adding **game-like direct manipulation**:
  - one-finger swipe/drag to pan, rotate or move through space
  - pinch to zoom in and out
  - tap objects to select them or move toward them
  - momentum/inertia where useful
  - optional subtle device-motion/parallax
- Use **Three.js/WebGL/WebGPU where appropriate**, but avoid unnecessarily heavy 3D rendering.
- Prefer a **hybrid architecture**:
  - 3D for space, navigation, depth, transitions and atmosphere
  - HTML/CSS for text, forms, controls and detailed interface elements
- Performance is a hard constraint:
  - lightweight assets
  - compressed textures
  - sensible geometry
  - progressive loading
  - reduced effects on weaker hardware
  - graceful fallback where appropriate
- Create the **maximum perception of depth and spatial sophistication with the minimum rendering cost**.
- One core product should adapt across iPhone, Android, tablet and desktop.

## Relationship to Juku Style

Think of Juku Style as the broader design system.

This new rule is the **spatial/game-like layer inside Juku Style**, not a new replacement design system.

When implementing it:

1. preserve existing Juku Style principles;
2. add this spatial layer where it improves the product;
3. never sacrifice usability, clarity or performance simply to make something 3D.

## Phena River

Apply this layer strongly to the **Phena River**.

The River should feel like an **explorable information space**, not a page or conventional dashboard.

Users should be able to:

- zoom out to see the broad landscape and major patterns;
- move spatially between clusters and themes;
- zoom progressively into individual experiences;
- continue into individual people, claims, transcripts, audio and supporting evidence;
- understand information hierarchy partly through physical depth, scale and position.

The experience should feel as though the user is **travelling through the information itself**.

Use HyperSolid as the live visual reference, but do not copy it literally. The Juku Style implementation should be **more interactive, more touch-native, more useful as an application, and still extremely lightweight**.
