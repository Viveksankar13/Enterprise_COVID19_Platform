import React from "react";

export const Footer: React.FC = () => {
  return (
    <footer className="py-4 px-6 border-t border-border mt-auto flex flex-col md:flex-row items-center justify-between text-xs text-muted-foreground glass-panel">
      <div>
        <span>© {new Date().getFullYear()} Enterprise COVID-19 Analytics Portal. All rights reserved.</span>
      </div>
      <div className="flex gap-4 mt-2 md:mt-0">
        <a href="#terms" className="hover:text-primary transition-colors duration-200">Terms of Service</a>
        <a href="#privacy" className="hover:text-primary transition-colors duration-200">Privacy Policy</a>
        <a href="#help" className="hover:text-primary transition-colors duration-200">Technical Support</a>
      </div>
    </footer>
  );
};
