import { useParams, Link } from 'react-router-dom'
import { AlertCircle, ArrowLeft } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useDraft } from '@/lib/hooks/useDraft'
import { DraftWorkflowLayout } from '@/components/workflow/DraftWorkflowLayout'
import { DraftSkeleton } from '@/components/workflow/DraftSkeleton'

export default function DraftReviewPage() {
  const { threadId } = useParams<{ threadId: string }>()
  const { data: draft, isLoading, isError, error } = useDraft(threadId!)

  if (isLoading) {
    return (
      <div className="mx-auto max-w-6xl px-4 py-10">
        <DraftSkeleton />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-10 space-y-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error instanceof Error ? error.message : 'Impossible de charger ce draft.'}
          </AlertDescription>
        </Alert>
        <Link to="/new" className={cn(buttonVariants({ variant: 'outline' }), 'gap-2')}>
          <ArrowLeft className="h-4 w-4" />
          Retour au formulaire
        </Link>
      </div>
    )
  }

  if (!draft) return null

  return <DraftWorkflowLayout draft={draft} />
}
