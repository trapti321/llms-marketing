# Premium Website Redesign — LLM’s Marketing

A visual redesign of the **LLM’s Marketing** consultancy platform. Inspired by high-end design systems (Linear, Vercel, Stripe), this project elevates the website into a minimal, editorial, and sophisticated digital marketing consultancy footprint while fully preserving the original business information, services, posts, and form structures.

---

## 🛠 Tech Stack

- **Core Structure**: Semantic HTML5 (optimized for SEO and structured crawler indexing).
- **Styling (CSS)**: Custom Vanilla CSS variables, dark-mode tokens (`#09090b` charcoal background / `#fafafa` warm white text), balanced text alignment (`text-wrap: balance`), asymmetric card grids, and smooth transitions.
- **Interactions (JS)**: Vanilla JavaScript with no heavy external UI dependencies.
  - **Hero Background Graph**: Interactive HTML5 floating node canvas drawing connecting signals that react to mouse hover gravity.
  - **Scroll Reveals**: `IntersectionObserver` triggered fade-ins and staggered slide-ups.
  - **Dynamic Counters**: Viewport-triggered numerical counters that count up to targets (e.g. `390+`, `90%`).
  - **Live Resolver Simulator**: Tab-switched timeline demonstrating brand indexing flows.
  - **Accordion & Carousel**: Single-open FAQ answers and auto-playing testimonial sliders.
- **Build Engine**: **Vite** (provides instant hot-reloading for development and optimizes the static multi-page bundle for deployment).

---

## 📂 Project Structure

```text
llms-marketing/
├── package.json              # Scripts & Vite dependencies
├── vite.config.js            # Rollup multi-page inputs config
├── index.html                # Home Page Redesign
├── about-us/
│   └── index.html            # About & Team Section (5 team members)
├── our-services/
│   └── index.html            # Core capabilities & optimized engines
├── services/
│   └── digital-strategy-marketing/
│       └── index.html        # Service detail template (preserves original copy)
├── blog/
│   ├── index.html            # Insights listing page
│   ├── seo-is-changing-how-ai-platforms-like-chatgpt-are-redefining-search-visibility/
│   │   └── index.html        # First blog post detailed reading layout
│   └── what-is-llm-marketing-a-complete-guide-to-getting-discovered-on-ai-platforms/
│       └── index.html        # Second blog post detailed reading layout
├── contact/
│   └── index.html            # Form page preserving original WPForms inputs
└── assets/
    ├── css/
    │   └── style.css         # Typography, layout system, and responsive rules
    └── js/
        └── main.js           # Scroll reveals, timeline, slider, and canvas graph logic
```

---

## 🚀 Running Locally

Follow these quick steps to get the local website running from your workspace:

### 1. Prerequisite
Ensure you have **Node.js** (v18+) installed on your machine.

### 2. Install Dependencies
Open your terminal in this project directory and install Vite:
```bash
npm install
```

### 3. Start Development Server
Run the local dev command:
```bash
npm run dev
```
Vite will output a local URL (e.g., `http://localhost:5173/` or `http://localhost:3000/`). Open this link in your browser to inspect the animations, transitions, and layout responsiveness.

### 4. Build for Production
To build a highly optimized static bundle ready for deployment:
```bash
npm run build
```
This generates a production-ready `dist/` directory containing minified HTML, CSS, and JS assets.

### 5. Preview the Production Build
To test the output of the production compilation locally:
```bash
npm run preview
```

---

## ✉️ Contact Form Submission Details

The contact form in `contact/index.html` preserves the identical class validations, input naming conventions (`wpforms[fields][1]`, etc.), and hidden WordPress metadata to prevent breaking any active server-side listeners.

- **Mock Action (Default)**: Form submissions are intercepted via JavaScript, displaying a custom loading indicator and a successful status message before resetting inputs.
- **API Activation**: To integrate with static services (like **Web3Forms**), you can modify the hidden `access_key` field in `contact/index.html`:
  ```html
  <input type="hidden" name="access_key" value="YOUR_ACCESS_KEY">
  ```
