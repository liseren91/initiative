import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/_serverRequired/_authenticated/hypotheses_/$hypothesisId")({
  beforeLoad: ({ context, params }) => {
    const guildId = context.guilds?.activeGuildId;
    if (guildId) {
      throw redirect({
        to: "/g/$guildId/hypotheses/$hypothesisId",
        params: { guildId: String(guildId), hypothesisId: params.hypothesisId },
      });
    }
    throw redirect({ to: "/" });
  },
});
