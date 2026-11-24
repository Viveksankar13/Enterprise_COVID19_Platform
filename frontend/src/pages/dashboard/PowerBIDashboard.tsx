import React from "react";
import { PowerBIEmbed } from "../../components/powerbi/PowerBIEmbed";

export const PowerBIDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
          Power BI Embedded Analytics
        </h1>
        <p className="text-muted-foreground mt-1">
          Interactive enterprise reports rendered via Microsoft Azure capacity services.
        </p>
      </div>

      <PowerBIEmbed />
    </div>
  );
};
