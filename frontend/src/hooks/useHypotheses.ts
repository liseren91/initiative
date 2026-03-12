import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  listHypotheses,
  getHypothesis,
  createHypothesis,
  updateHypothesis,
  deleteHypothesis,
  promoteHypothesis,
} from "@/api/hypotheses";
import type {
  HypothesisCreate,
  HypothesisPromoteResponse,
  HypothesisResponse,
  HypothesisStatus,
  HypothesisUpdate,
} from "@/api/hypotheses";
import { invalidateAllHypotheses } from "@/api/query-keys";
import { getErrorMessage } from "@/lib/errorMessage";
import type { MutationOpts } from "@/types/mutation";
import type { QueryOpts } from "@/types/query";

const HYPOTHESES_KEY = "/api/v1/hypotheses/";

export const useHypotheses = (
  status?: HypothesisStatus,
  options?: QueryOpts<HypothesisResponse[]>
) => {
  return useQuery<HypothesisResponse[]>({
    queryKey: status ? [HYPOTHESES_KEY, { status }] : [HYPOTHESES_KEY],
    queryFn: () => listHypotheses(status),
    ...options,
  });
};

export const useHypothesis = (id: number | null, options?: QueryOpts<HypothesisResponse>) => {
  const { enabled: userEnabled = true, ...rest } = options ?? {};
  return useQuery<HypothesisResponse>({
    queryKey: [`/api/v1/hypotheses/${id}`],
    queryFn: () => getHypothesis(id!),
    enabled: id !== null && Number.isFinite(id) && userEnabled,
    ...rest,
  });
};

export const useCreateHypothesis = (
  options?: MutationOpts<HypothesisResponse, HypothesisCreate>
) => {
  const { onSuccess, onError, onSettled, ...rest } = options ?? {};

  return useMutation({
    ...rest,
    mutationFn: (data: HypothesisCreate) => createHypothesis(data),
    onSuccess: (...args) => {
      void invalidateAllHypotheses();
      onSuccess?.(...args);
    },
    onError: (...args) => {
      toast.error(getErrorMessage(args[0], "hypotheses:createError"));
      onError?.(...args);
    },
    onSettled,
  });
};

export const useUpdateHypothesis = (
  options?: MutationOpts<HypothesisResponse, { id: number; data: HypothesisUpdate }>
) => {
  const { onSuccess, onError, onSettled, ...rest } = options ?? {};

  return useMutation({
    ...rest,
    mutationFn: ({ id, data }: { id: number; data: HypothesisUpdate }) =>
      updateHypothesis(id, data),
    onSuccess: (...args) => {
      void invalidateAllHypotheses();
      onSuccess?.(...args);
    },
    onError: (...args) => {
      toast.error(getErrorMessage(args[0], "hypotheses:updateError"));
      onError?.(...args);
    },
    onSettled,
  });
};

export const useDeleteHypothesis = (options?: MutationOpts<void, number>) => {
  const { onSuccess, onError, onSettled, ...rest } = options ?? {};

  return useMutation({
    ...rest,
    mutationFn: (id: number) => deleteHypothesis(id),
    onSuccess: (...args) => {
      void invalidateAllHypotheses();
      onSuccess?.(...args);
    },
    onError: (...args) => {
      toast.error(getErrorMessage(args[0], "hypotheses:deleteError"));
      onError?.(...args);
    },
    onSettled,
  });
};

export const usePromoteHypothesis = (
  options?: MutationOpts<HypothesisPromoteResponse, { id: number; initiativeId: number }>
) => {
  const { onSuccess, onError, onSettled, ...rest } = options ?? {};

  return useMutation({
    ...rest,
    mutationFn: ({ id, initiativeId }: { id: number; initiativeId: number }) =>
      promoteHypothesis(id, initiativeId),
    onSuccess: (...args) => {
      void invalidateAllHypotheses();
      onSuccess?.(...args);
    },
    onError: (...args) => {
      toast.error(getErrorMessage(args[0], "hypotheses:promoteError"));
      onError?.(...args);
    },
    onSettled,
  });
};
