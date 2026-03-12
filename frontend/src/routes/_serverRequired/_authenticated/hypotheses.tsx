import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_serverRequired/_authenticated/hypotheses")({
  beforeLoad: ({ context }) => {
    const guildId = context.guilds?.activeGuildId;
    if (guildId) {
      throw redirect({
        to: "/g/$guildId/hypotheses",
        params: { guildId: String(guildId) },
      });
    }
    throw redirect({ to: "/" });
  },
});
