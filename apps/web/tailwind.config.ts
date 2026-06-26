import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      "colors": {
          "on-background": "#191c1e",
          "secondary-fixed": "#cde5ff",
          "surface-container-highest": "#e0e3e5",
          "secondary-fixed-dim": "#94ccff",
          "on-error": "#ffffff",
          "tertiary-fixed-dim": "#45d8ed",
          "inverse-primary": "#b7c4ff",
          "on-surface-variant": "#444653",
          "primary-fixed-dim": "#b7c4ff",
          "secondary-container": "#6cbdfe",
          "inverse-surface": "#2d3133",
          "surface-container-lowest": "#ffffff",
          "surface-variant": "#e0e3e5",
          "surface-container": "#eceef0",
          "surface": "#f7f9fb",
          "tertiary-container": "#00606b",
          "tertiary-fixed": "#98f0ff",
          "surface-bright": "#f7f9fb",
          "error-container": "#ffdad6",
          "secondary": "#006398",
          "background": "#f7f9fb",
          "outline": "#747685",
          "primary": "#0131a6",
          "surface-container-low": "#f2f4f6",
          "on-secondary-fixed-variant": "#004b74",
          "primary-fixed": "#dde1ff",
          "error": "#ba1a1a",
          "surface-container-high": "#e6e8ea",
          "on-primary": "#ffffff",
          "tertiary": "#00474f",
          "on-secondary-container": "#004b75",
          "inverse-on-surface": "#eff1f3",
          "on-tertiary-fixed": "#001f24",
          "on-primary-container": "#bfcaff",
          "on-error-container": "#93000a",
          "surface-tint": "#3554c6",
          "surface-dim": "#d8dadc",
          "primary-container": "#2b4cbe",
          "on-secondary": "#ffffff",
          "on-primary-fixed-variant": "#133aae",
          "outline-variant": "#c4c5d6",
          "on-surface": "#191c1e",
          "on-primary-fixed": "#001453",
          "on-tertiary": "#ffffff",
          "on-secondary-fixed": "#001d32",
          "on-tertiary-container": "#4edff3",
          "on-tertiary-fixed-variant": "#004f58"
      },
      "borderRadius": {
          "DEFAULT": "0.25rem",
          "lg": "0.5rem",
          "xl": "0.75rem",
          "full": "9999px"
      },
      "spacing": {
          "xs": "8px",
          "xl": "64px",
          "md": "24px",
          "base": "4px",
          "lg": "40px",
          "gutter": "24px",
          "container-max": "1280px",
          "sm": "16px"
      },
      "fontFamily": {
          "label-lg": ["var(--font-inter)", "Inter"],
          "headline-lg": ["var(--font-inter)", "Inter"],
          "label-sm": ["var(--font-inter)", "Inter"],
          "display-lg": ["var(--font-inter)", "Inter"],
          "body-lg": ["var(--font-inter)", "Inter"],
          "headline-lg-mobile": ["var(--font-inter)", "Inter"],
          "headline-md": ["var(--font-inter)", "Inter"],
          "body-md": ["var(--font-inter)", "Inter"]
      },
      "fontSize": {
          "label-lg": ["14px", {"lineHeight": "20px", "letterSpacing": "0.01em", "fontWeight": "600"}],
          "headline-lg": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.01em", "fontWeight": "600"}],
          "label-sm": ["12px", {"lineHeight": "16px", "fontWeight": "500"}],
          "display-lg": ["48px", {"lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "700"}],
          "body-lg": ["18px", {"lineHeight": "28px", "fontWeight": "400"}],
          "headline-lg-mobile": ["28px", {"lineHeight": "36px", "fontWeight": "600"}],
          "headline-md": ["24px", {"lineHeight": "32px", "fontWeight": "600"}],
          "body-md": ["16px", {"lineHeight": "24px", "fontWeight": "400"}]
      }
    },
  },
  plugins: [],
};

export default config;
