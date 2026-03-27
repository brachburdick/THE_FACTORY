# Node.js & Build Tools

- **Node version:** 20.18.x is the current runtime. Check with `node --version` before assuming compatibility.
- **Vite:** Use Vite 6.x or lower. Vite 7+ and 8+ require Node >=20.19. `npm create vite@6` is safe.
- **Tailwind CSS:** Use Tailwind 3.x with PostCSS plugin approach. Do NOT use Tailwind 4's Vite plugin — it is incompatible with the PostCSS configuration pattern and requires a different setup. Install: `npm install -D tailwindcss@3 postcss autoprefixer && npx tailwindcss init -p`.
- **TypeScript:** Always run `tsc --noEmit` before preview. Most rendering bugs are actually type errors.
