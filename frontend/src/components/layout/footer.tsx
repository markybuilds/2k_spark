/**
 * Footer component for the application.
 */

export function Footer() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-14 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          &copy; {new Date().getFullYear()} 2K Flash. All rights reserved.
        </p>
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-right">
          NBA 2K25 eSports Match Prediction System
        </p>
      </div>
    </footer>
  );
}
