import * as React from "react"

// Assuming the relative path is correct based on other merged components
import { cn } from '../../lib/utils' 

// --- 1. Main Card Component (Using forwardRef from Beneficiary, Styling from HEAD) ---

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-slot="card" // Data slot from HEAD
    className={cn(
      // Combined styling for robust display
      "bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"


// --- 2. CardHeader (Using forwardRef) ---

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-slot="card-header" // Data slot from HEAD
    className={cn(
      // Advanced grid layout from HEAD for actions and title/description
      "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
      className
    )}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"


// --- 3. CardAction (Only exists in HEAD, must be kept) ---

function CardAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className
      )}
      {...props}
    />
  )
}
CardAction.displayName = "CardAction"


// --- 4. CardTitle (Using forwardRef) ---

const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-slot="card-title" // Data slot from HEAD
    className={cn("font-semibold leading-none tracking-tight", className)} // Styling combined
    {...props}
  />
))
CardTitle.displayName = "CardTitle"


// --- 5. CardDescription (Using forwardRef) ---

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-slot="card-description" // Data slot from HEAD
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"


// --- 6. CardContent (Using forwardRef, Styling from HEAD) ---

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} data-slot="card-content" className={cn("px-6", className)} {...props} /> // Styling from HEAD
))
CardContent.displayName = "CardContent"


// --- 7. CardFooter (Using forwardRef, Styling from HEAD) ---

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    data-slot="card-footer" // Data slot from HEAD
    className={cn("flex items-center px-6 [.border-t]:pt-6", className)} // Styling from HEAD
    {...props}
  />
))
CardFooter.displayName = "CardFooter"


// --- Export ---

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction, // Include the CardAction component
  CardDescription,
  CardContent,
}