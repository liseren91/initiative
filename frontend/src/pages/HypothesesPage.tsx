import { FormEvent, useCallback, useState } from "react";
import { Link } from "@tanstack/react-router";
import { Lightbulb, Loader2, Plus } from "lucide-react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";

import { invalidateAllHypotheses } from "@/api/query-keys";
import { useHypotheses, useCreateHypothesis } from "@/hooks/useHypotheses";
import { PullToRefresh } from "@/components/PullToRefresh";
import { useGuildPath } from "@/lib/guildUrl";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import type { HypothesisStatus } from "@/api/hypotheses";

const STATUS_COLORS: Record<HypothesisStatus, string> = {
  idea: "bg-blue-500/15 text-blue-700 dark:text-blue-400",
  evaluation: "bg-amber-500/15 text-amber-700 dark:text-amber-400",
  research: "bg-purple-500/15 text-purple-700 dark:text-purple-400",
  decision: "bg-cyan-500/15 text-cyan-700 dark:text-cyan-400",
  project: "bg-green-500/15 text-green-700 dark:text-green-400",
  rejected: "bg-red-500/15 text-red-700 dark:text-red-400",
  paused: "bg-gray-500/15 text-gray-700 dark:text-gray-400",
};

const ALL_STATUSES: HypothesisStatus[] = [
  "idea",
  "evaluation",
  "research",
  "decision",
  "project",
  "rejected",
  "paused",
];

export const HypothesesPage = () => {
  const { t } = useTranslation(["hypotheses", "common"]);
  const gp = useGuildPath();

  const [activeFilter, setActiveFilter] = useState<HypothesisStatus | undefined>(undefined);
  const [createOpen, setCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const hypothesesQuery = useHypotheses(activeFilter);
  const createMutation = useCreateHypothesis({
    onSuccess: () => {
      toast.success(t("created"));
      setCreateOpen(false);
      setTitle("");
      setDescription("");
    },
  });

  const handleRefresh = useCallback(async () => {
    await invalidateAllHypotheses();
  }, []);

  const handleCreate = (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    createMutation.mutate({ title: title.trim(), description: description.trim() || undefined });
  };

  const hypotheses = hypothesesQuery.data ?? [];

  return (
    <PullToRefresh onRefresh={handleRefresh}>
      <div className="container mx-auto max-w-5xl space-y-6 p-4 md:p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Lightbulb className="text-primary h-6 w-6" />
            <h1 className="text-2xl font-bold">{t("title")}</h1>
          </div>
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            {t("newHypothesis")}
          </Button>
        </div>

        {/* Status filters */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={activeFilter === undefined ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveFilter(undefined)}
          >
            {t("allStatuses")}
          </Button>
          {ALL_STATUSES.map((s) => (
            <Button
              key={s}
              variant={activeFilter === s ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveFilter(s)}
            >
              {t(`status.${s}`)}
            </Button>
          ))}
        </div>

        {/* Content */}
        {hypothesesQuery.isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
            <Skeleton className="h-28 w-full" />
          </div>
        ) : hypothesesQuery.isError ? (
          <Card>
            <CardContent className="text-destructive py-8 text-center">
              {t("loadError")}
            </CardContent>
          </Card>
        ) : hypotheses.length === 0 ? (
          <Card>
            <CardContent className="text-muted-foreground py-12 text-center">
              {activeFilter ? t("noHypothesesFiltered") : t("noHypotheses")}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {hypotheses.map((h) => (
              <Link key={h.id} to={gp(`/hypotheses/${h.id}`)}>
                <Card className="hover:border-primary/50 h-full transition-colors">
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="line-clamp-2 text-base">{h.title}</CardTitle>
                      <Badge variant="secondary" className={STATUS_COLORS[h.status]}>
                        {t(`status.${h.status}`)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {h.description ? (
                      <CardDescription className="line-clamp-3">{h.description}</CardDescription>
                    ) : (
                      <CardDescription className="italic">
                        {t("detail.noDescription")}
                      </CardDescription>
                    )}
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}

        {/* Create dialog */}
        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogContent>
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle>{t("createTitle")}</DialogTitle>
                <DialogDescription>{t("createDescription")}</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="hypothesis-title">{t("titleLabel")}</Label>
                  <Input
                    id="hypothesis-title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder={t("titlePlaceholder")}
                    required
                    autoFocus
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hypothesis-description">{t("descriptionLabel")}</Label>
                  <Textarea
                    id="hypothesis-description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder={t("descriptionPlaceholder")}
                    rows={4}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setCreateOpen(false)}>
                  {t("common:cancel")}
                </Button>
                <Button type="submit" disabled={createMutation.isPending || !title.trim()}>
                  {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  {t("common:create")}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>
    </PullToRefresh>
  );
};
