// src/layouts/AgentLayout.tsx
import React from "react";
import AgentNavbar from "@/components/AgentNavbar";
import { getBankLogo, getTheme } from "../utils/bankTheme"

const AgentLayout = ({ children, agent }) => {
    const theme = getTheme(agent.bankId);

    return (
        <div
            className="min-h-screen"
            style={{
                backgroundImage: `linear-gradient(to bottom, white 0%, #f3f4f6 70%, ${theme.hex}50 100%)`,
            }}
        >
            <AgentNavbar
                agentName={agent.name}
                agentEmail={agent.email}
                agentBankId={agent.bankId}
                themePrimary={theme.primary}
                themeSecondary={theme.secondary}
                getBankLogo={getBankLogo}
            />

            <div className="p-6 max-w-7xl mx-auto">
                {children}
            </div>
        </div>
    );
};

export default AgentLayout;
