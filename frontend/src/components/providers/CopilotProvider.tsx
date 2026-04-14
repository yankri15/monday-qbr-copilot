"use client";

import { CopilotKit } from "@copilotkit/react-core";
import type { ReactNode } from "react";

type CopilotProviderProps = {
  children: ReactNode;
  runtimeUrl: string;
};

export function CopilotProvider({
  children,
  runtimeUrl,
}: CopilotProviderProps) {
  return (
    <CopilotKit runtimeUrl={runtimeUrl} showDevConsole={false} enableInspector={false}>
      {children}
    </CopilotKit>
  );
}
