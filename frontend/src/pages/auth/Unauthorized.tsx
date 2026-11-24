import React from "react";
import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";
import { Button } from "../../components/ui/Button";

export const Unauthorized: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
      <div className="text-rose-500 mb-4 animate-bounce">
        <ShieldAlert size={64} />
      </div>
      <h1 className="text-3xl font-bold tracking-tight text-foreground">Access Denied</h1>
      <p className="text-muted-foreground mt-2 max-w-md">
        You do not possess the required RBAC privileges to access this resource. Please contact system administration to request access.
      </p>
      <Link to="/" className="mt-6">
        <Button>Return to Dashboard</Button>
      </Link>
    </div>
  );
};
