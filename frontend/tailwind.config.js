/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // Ensure all your file paths are correct here (your existing setup)
    "./src/**/*.{js,ts,jsx,tsx}", 
  ],
  theme: {
    extend: {
      // --- CUSTOM COLORS EXTENSION ---
      colors: {
        // Core Colors (CORRECTED to object notation for robustness)
        border: { DEFAULT: 'var(--border)' },
        input: { DEFAULT: 'var(--input)' },
        
        'ring': {
           // This is correct for handling opacity like 'ring/50'
           DEFAULT: 'var(--ring)', 
        },
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        
        // Card/Popover Colors
        card: 'var(--card)',
        'card-foreground': 'var(--card-foreground)',
        popover: 'var(--popover)',
        'popover-foreground': 'var(--popover-foreground)',
        
        // Primary/Secondary/Accent/Muted Colors
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)',
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)',
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)',
        },
        destructive: 'var(--destructive)',

        // Sidebar Colors
        sidebar: {
          DEFAULT: 'var(--sidebar)',
          foreground: 'var(--sidebar-foreground)',
          primary: {
            DEFAULT: 'var(--sidebar-primary)',
            foreground: 'var(--sidebar-primary-foreground)',
          },
          accent: {
            DEFAULT: 'var(--sidebar-accent)',
            foreground: 'var(--sidebar-accent-foreground)',
          },
          border: 'var(--sidebar-border)',
          ring: 'var(--sidebar-ring)',
        },

        // Chart Colors
        chart: {
          1: 'var(--chart-1)',
          2: 'var(--chart-2)',
          3: 'var(--chart-3)',
          4: 'var(--chart-4)',
          5: 'var(--chart-5)',
        },
      },
      // --- END: CUSTOM COLORS EXTENSION ---

      // --- CUSTOM FONT-FAMILY EXTENSION ---
      fontFamily: {
        'anago': ['Anago', 'sans-serif'], 
      },
      // --- CRITICAL FIX: Add 'outline' and 'ring' to theme extensions ---
      outline: {
        // This ensures classes like 'outline-ring' are generated
        ring: 'var(--ring)', 
      },
      ring: {
        // This ensures classes like 'ring-ring' are generated
        ring: 'var(--ring)',
      },
      // --- END: CUSTOM FONT-FAMILY EXTENSION ---
    },
  },
  
  // --- PLUGINS ---
  plugins: [
    require('tailwindcss-animate'),
    // Ensure other plugins (like tw-animate-css) are listed here if needed.
  ],
};