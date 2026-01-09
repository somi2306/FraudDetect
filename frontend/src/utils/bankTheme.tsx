// src/utils/bankTheme.ts
export const BANK_LOGOS = {
    17: "/logos/Cih.png",
    18: "/logos/tijari.png",
    19: "/logos/bcp.png",
    0: "/logos/default.png",
};

export const BANK_THEMES = {
    17: {
        primary: "bg-cyan-600",
        secondary: "bg-cyan-800",
        text: "text-cyan-700",
        hex: "#06B6D4"
    },
    18: {
        primary: "bg-yellow-600",
        secondary: "bg-yellow-800",
        text: "text-yellow-700",
        hex: "#6b3e0b"
    },
    19: {
        primary: "bg-orange-300",
        secondary: "bg-orange-400",
        text: "text-orange-700",
        hex: "#d27722ff"
    },
    0: {
        primary: "bg-emerald-600",
        secondary: "bg-emerald-800",
        text: "text-emerald-700",
        hex: "#059669"
    }
};

export const getTheme = (bankId) =>
    BANK_THEMES[bankId || 0];

export const getBankLogo = (bankId) =>
    BANK_LOGOS[bankId || 0];
