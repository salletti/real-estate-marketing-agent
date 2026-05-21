import { CheckCircle2, Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export function PublishedState() {
  return (
    <div className="flex flex-col items-center gap-4 py-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <CheckCircle2 className="h-9 w-9 text-green-600" />
      </div>
      <div className="space-y-1">
        <h2 className="text-lg font-semibold">Publication réussie !</h2>
        <p className="text-sm text-muted-foreground">
          Le workflow LangGraph a repris et les posts ont été publiés (mock).
        </p>
      </div>
      <Link to="/new" className={cn(buttonVariants({ variant: 'outline' }), 'mt-2 gap-2')}>
        <Plus className="h-4 w-4" />
        Nouvelle publication
      </Link>
    </div>
  )
}
