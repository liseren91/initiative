import { apiClient } from "@/api/client";

export interface HypothesisResponse {
  id: number;
  guild_id: number | null;
  project_id: number | null;
  title: string;
  description: string | null;
  status: HypothesisStatus;
  created_by_id: number | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by: {
    id: number;
    email: string;
    full_name: string | null;
    avatar_base64: string | null;
    avatar_url: string | null;
  } | null;
}

export type HypothesisStatus =
  | "idea"
  | "evaluation"
  | "research"
  | "decision"
  | "project"
  | "rejected"
  | "paused";

export interface HypothesisCreate {
  title: string;
  description?: string | null;
  status?: HypothesisStatus;
}

export interface HypothesisUpdate {
  title?: string | null;
  description?: string | null;
  status?: HypothesisStatus | null;
}

export interface HypothesisPromoteResponse {
  hypothesis: HypothesisResponse;
  project: { id: number; name: string; [key: string]: unknown };
}

export const listHypotheses = async (status?: HypothesisStatus): Promise<HypothesisResponse[]> => {
  const params: Record<string, string> = {};
  if (status) params.status = status;
  const { data } = await apiClient.get<HypothesisResponse[]>("/hypotheses/", { params });
  return data;
};

export const getHypothesis = async (id: number): Promise<HypothesisResponse> => {
  const { data } = await apiClient.get<HypothesisResponse>(`/hypotheses/${id}`);
  return data;
};

export const createHypothesis = async (payload: HypothesisCreate): Promise<HypothesisResponse> => {
  const { data } = await apiClient.post<HypothesisResponse>("/hypotheses/", payload);
  return data;
};

export const updateHypothesis = async (
  id: number,
  payload: HypothesisUpdate
): Promise<HypothesisResponse> => {
  const { data } = await apiClient.patch<HypothesisResponse>(`/hypotheses/${id}`, payload);
  return data;
};

export const deleteHypothesis = async (id: number): Promise<void> => {
  await apiClient.delete(`/hypotheses/${id}`);
};

export const promoteHypothesis = async (
  id: number,
  initiativeId: number
): Promise<HypothesisPromoteResponse> => {
  const { data } = await apiClient.post<HypothesisPromoteResponse>(
    `/hypotheses/${id}/promote`,
    null,
    { params: { initiative_id: initiativeId } }
  );
  return data;
};
