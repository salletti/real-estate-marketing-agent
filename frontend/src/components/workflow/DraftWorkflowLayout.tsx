import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { WorkflowTimeline } from './WorkflowTimeline'
import { HateoasActionBar } from './HateoasActionBar'
import { PublishedState } from './PublishedState'
import { RejectedState } from './RejectedState'
import { DraftCardGrid } from '@/components/drafts/DraftCardGrid'
import { getStoredPhotos } from '@/lib/hooks/useDraft'
import type { DraftResponse } from '@/lib/types/api'

function StatusBadge({ status }: { status: DraftResponse['status'] }) {
  if (status === 'published') {
    return <Badge className="bg-green-100 text-green-700 hover:bg-green-100">Publié</Badge>
  }
  if (status === 'rejected') {
    return <Badge variant="destructive">Rejeté</Badge>
  }
  return <Badge variant="secondary">Draft en attente</Badge>
}

interface DraftWorkflowLayoutProps {
  draft: DraftResponse
}

export function DraftWorkflowLayout({ draft }: DraftWorkflowLayoutProps) {
  const isPending = draft.status === 'draft' && draft.approval_status === 'pending'

  // Le backend retourne toujours images: [] dans aggregate_drafts_node.
  // On récupère les URLs saisies dans le formulaire depuis sessionStorage.
  const storedPhotos = getStoredPhotos(draft.thread_id)

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Révision du draft</h1>
          <p className="mt-1 font-mono text-xs text-muted-foreground">{draft.thread_id}</p>
        </div>
        <StatusBadge status={draft.status} />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[200px_1fr]">
        <Card className="h-fit">
          <CardHeader className="pb-3">
            <CardTitle className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Workflow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <WorkflowTimeline draft={draft} />
          </CardContent>
        </Card>

        <div className="space-y-6">
          {draft.status === 'published' && <PublishedState />}
          {draft.status === 'rejected' && <RejectedState />}
          {isPending && (
            <>
              <DraftCardGrid
                platforms={draft.content.data.platforms}
                photos={storedPhotos}
              />
              <HateoasActionBar links={draft._links} threadId={draft.thread_id} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
