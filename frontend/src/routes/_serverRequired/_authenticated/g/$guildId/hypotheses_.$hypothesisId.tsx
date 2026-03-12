import { createFileRoute, lazyRouteComponent } from "@tanstack/react-router";

export const Route = createFileRoute(
  "/_serverRequired/_authenticated/g/$guildId/hypotheses_/$hypothesisId"
)({
  component: lazyRouteComponent(() =>
    import("@/pages/HypothesisDetailPage").then((m) => ({
      default: m.HypothesisDetailPage,
    }))
  ),
});
