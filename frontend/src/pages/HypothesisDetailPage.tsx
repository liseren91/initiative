import { useCallback, useState } from "react";
import { useNavigate, useParams } from "@tanstack/react-router";
import { ArrowLeft, Lightbulb, Loader2, Rocket, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";

import {
  useHypothesis,
  useUpdateHypothesis,
  useDeleteHypothesis,
  usePromoteHypothesis,
} from "@/hooks/useHypotheses";
import { useInitiatives } from "@/hooks/useInitiatives";
import { useGuildPath } from "@/lib/guildUrl";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
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

export const HypothesisDetailPage = () => {
  const { t } = useTranslation(["hypotheses", "common"]);
  const navigate = useNavigate();
  const gp = useGuildPath();
  const params = useParams({ strict: false }) as { hypothesisId?: string };
  const hypothesisId = params.hypothesisId ? Number(params.hypothesisId) : null;

  const [promoteOpen, setPromoteOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedInitiativeId, setSelectedInitiativeId] = useState<string>("");

  const hypothesisQuery = useHypothesis(hypothesisId);
  const initiativesQuery = useInitiatives({ enabled: promoteOpen });

  const updateMutation = useUpdateHypothesis({
    onSuccess: () => {
      toast.success(t("updated"));
    },
  });

  const deleteMutation = useDeleteHypothesis({
    onSuccess: () => {
      toast.success(t("deleted"));
      void navigate({ to: gp("/hypotheses") });
    },
  });

  const promoteMutation = usePromoteHypothesis({
    onSuccess: (data) => {
      toast.success(t("promoted"));
      setPromoteOpen(false);
      void navigate({ to: gp(`/projects/${data.project.id}`) });
    },
  });

  const handleStatusChange = useCallback(
    (newStatus: string) => {
      if (!hypothesisId) return;
      updateMutation.mutate({ id: hypothesisId, data: { status: newStatus as HypothesisStatus } });
    },
    [hypothesisId, updateMutation]
  );

  const handleDelete = useCallback(() => {
    if (!hypothesisId) return;
    deleteMutation.mutate(hypothesisId);
  }, [hypothesisId, deleteMutation]);

  const handlePromote = useCallback(() => {
    if (!hypothesisId || !selectedInitiativeId) return;
    promoteMutation.mutate({
      id: hypothesisId,
      initiativeId: Number(selectedInitiativeId),
    });
  }, [hypothesisId, selectedInitiativeId, promoteMutation]);

  if (hypothesisQuery.isLoading) {
    return (
      <div className="container mx-auto max-w-3xl space-y-6 p-4 md:p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (hypothesisQuery.isError || !hypothesisQuery.data) {
    return (
      <div className="container mx-auto max-w-3xl p-4 md:p-6">
        <Card>
          <CardContent className="text-destructive py-12 text-center">
            {t("detail.notFound")}
          </CardContent>
        </Card>
      </div>
    );
  }

  const hypothesis = hypothesisQuery.data;
  const isPromoted = hypothesis.status === "project";

  return (
    <div className="container mx-auto max-w-3xl space-y-6 p-4 md:p-6">
      {/* Back link */}
      <Button variant="ghost" size="sm" asChild>
        <a
          href={gp("/hypotheses")}
          onClick={(e) => {
            e.preventDefault();
            void navigate({ to: gp("/hypotheses") });
          }}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          {t("title")}
        </a>
      </Button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <Lightbulb className="text-primary h-6 w-6 shrink-0" />
          <h1 className="text-2xl font-bold">{hypothesis.title}</h1>
        </div>
        <Badge variant="secondary" className={STATUS_COLORS[hypothesis.status]}>
          {t(`status.${hypothesis.status}`)}
        </Badge>
      </div>

      {/* Description */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t("descriptionLabel")}</CardTitle>
        </CardHeader>
        <CardContent>
          {hypothesis.description ? (
            <p className="whitespace-pre-wrap">{hypothesis.description}</p>
          ) : (
            <p className="text-muted-foreground italic">{t("detail.noDescription")}</p>
          )}
        </CardContent>
      </Card>

      {/* Metadata */}
      <Card>
        <CardContent className="space-y-4 pt-6">
          {hypothesis.created_by && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground text-sm">{t("detail.createdBy")}</span>
              <span className="text-sm font-medium">
                {hypothesis.created_by.full_name ?? hypothesis.created_by.email}
              </span>
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground text-sm">{t("detail.createdAt")}</span>
            <span className="text-sm">{new Date(hypothesis.created_at).toLocaleDateString()}</span>
          </div>
          {hypothesis.project_id && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground text-sm">{t("detail.linkedProject")}</span>
              <Button variant="link" size="sm" className="h-auto p-0" asChild>
                <a
                  href={gp(`/projects/${hypothesis.project_id}`)}
                  onClick={(e) => {
                    e.preventDefault();
                    void navigate({ to: gp(`/projects/${hypothesis.project_id}`) });
                  }}
                >
                  {`#${hypothesis.project_id}`}
                </a>
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardContent className="space-y-4 pt-6">
          {/* Status change */}
          <div className="space-y-2">
            <Label>{t("statusLabel")}</Label>
            <Select
              value={hypothesis.status}
              onValueChange={handleStatusChange}
              disabled={isPromoted || updateMutation.isPending}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ALL_STATUSES.map((s) => (
                  <SelectItem key={s} value={s}>
                    {t(`status.${s}`)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2">
            {!isPromoted && (
              <Button onClick={() => setPromoteOpen(true)} className="flex-1">
                <Rocket className="mr-2 h-4 w-4" />
                {t("promoteToProject")}
              </Button>
            )}
            <Button variant="destructive" onClick={() => setDeleteOpen(true)}>
              <Trash2 className="mr-2 h-4 w-4" />
              {t("common:delete")}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Promote dialog */}
      <Dialog open={promoteOpen} onOpenChange={setPromoteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("promoteConfirmTitle")}</DialogTitle>
            <DialogDescription>{t("promoteConfirmDescription")}</DialogDescription>
          </DialogHeader>
          <div className="space-y-2 py-4">
            <Label>{t("promoteInitiativeLabel")}</Label>
            <Select value={selectedInitiativeId} onValueChange={setSelectedInitiativeId}>
              <SelectTrigger>
                <SelectValue placeholder={t("promoteInitiativePlaceholder")} />
              </SelectTrigger>
              <SelectContent>
                {(Array.isArray(initiativesQuery.data) ? initiativesQuery.data : []).map(
                  (initiative) => (
                    <SelectItem key={initiative.id} value={String(initiative.id)}>
                      {initiative.name}
                    </SelectItem>
                  )
                )}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPromoteOpen(false)}>
              {t("common:cancel")}
            </Button>
            <Button
              onClick={handlePromote}
              disabled={promoteMutation.isPending || !selectedInitiativeId}
            >
              {promoteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t("promoteToProject")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("deleteConfirmTitle")}</DialogTitle>
            <DialogDescription>{t("deleteConfirmDescription")}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              {t("common:cancel")}
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {t("common:delete")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};
