import { Loader2 } from 'lucide-react'

export function GeneratingOverlay() {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="flex flex-col items-center gap-4 rounded-xl border bg-card p-8 shadow-lg">
        <Loader2 className="h-10 w-10 animate-spin text-primary" />
        <div className="space-y-1 text-center">
          <p className="font-semibold">L&apos;agent génère vos drafts…</p>
          <p className="text-sm text-muted-foreground">
            Le workflow LangGraph est en cours d&apos;exécution (5-15 secondes)
          </p>
        </div>
      </div>
    </div>
  )
}
