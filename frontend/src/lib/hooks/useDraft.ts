import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { getDraft, executeDraftAction, generateDraft, buildGeneratePayload } from '@/lib/api/drafts'
import { isTerminalState } from '@/lib/types/api'
import type { DraftResponse } from '@/lib/types/api'
import type { PropertyFormValues } from '@/lib/validators/property.schema'

export const draftKeys = {
  detail: (threadId: string) => ['draft', threadId] as const,
}

// Photos stockées côté client par thread_id : le backend retourne images: []
// (aggregate_drafts_node hardcode toujours un tableau vide).
export function storePhotos(threadId: string, photos: string[]) {
  const urls = photos.filter(Boolean)
  if (urls.length > 0) {
    sessionStorage.setItem(`photos:${threadId}`, JSON.stringify(urls))
  }
}

export function getStoredPhotos(threadId: string): string[] {
  try {
    const raw = sessionStorage.getItem(`photos:${threadId}`)
    return raw ? (JSON.parse(raw) as string[]) : []
  } catch {
    return []
  }
}

export function useDraft(threadId: string) {
  return useQuery({
    queryKey: draftKeys.detail(threadId),
    queryFn: () => getDraft(threadId),
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return 2000
      return isTerminalState(data) ? false : 2000
    },
    staleTime: 0,
  })
}

export function useDraftAction(threadId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ href, method }: { href: string; method: string }) =>
      executeDraftAction(href, method),
    onSuccess: (updatedDraft: DraftResponse) => {
      queryClient.setQueryData(draftKeys.detail(threadId), updatedDraft)
    },
  })
}

export function useGenerateDraft() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (values: PropertyFormValues) =>
      generateDraft(buildGeneratePayload(values)),
    onSuccess: (draft: DraftResponse, values: PropertyFormValues) => {
      // Le backend ne remonte pas les photos dans le contenu généré.
      // On les persiste côté client pour les afficher dans la preview.
      storePhotos(draft.thread_id, values.photos)
      navigate(`/drafts/${draft.thread_id}`)
    },
  })
}
