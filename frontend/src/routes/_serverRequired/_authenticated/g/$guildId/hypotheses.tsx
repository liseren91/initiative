import { createFileRoute, lazyRouteComponent } from "@tanstack/react-router";

export const Route = createFileRoute("/_serverRequired/_authenticated/g/$guildId/hypotheses")({
  component: lazyRouteComponent(() =>
    import("@/pages/HypothesesPage").then((m) => ({ default: m.HypothesesPage }))
  ),
});
