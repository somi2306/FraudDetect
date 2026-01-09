import * as React from "react"

// Ensure the utility path is consistent with the rest of your components
import { cn } from '../../lib/utils' 

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  // Include style prop from HEAD for maximum compatibility, though inline styles should be avoided
  ({ className, type, style, ...props }, ref) => { 
    // Default style included from HEAD (often used for quick debugging/overrides)
    const defaultStyle: React.CSSProperties = {
      backgroundColor: "#ffffff",
      color: "#0f1724",
    }

    return (
      <input
        type={type}
        data-slot="input" // Data slot from HEAD
        // Apply inline styles from HEAD
        style={{ ...defaultStyle, ...(style || {}) }} 
        className={cn(
          // COMBINED STYLES: Using the robust focus and invalid state styling from HEAD
          "file:text-foreground placeholder:text-zinc-400 selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex h-9 w-full min-w-0 rounded-md border px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
          
          // Focus/Ring state styling from HEAD
          "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
          
          // ARIA Invalid state styling from HEAD
          "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }