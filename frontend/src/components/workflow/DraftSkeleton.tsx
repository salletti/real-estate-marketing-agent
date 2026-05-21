import { Skeleton } from '@/components/ui/skeleton'

export function DraftSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-6 w-48" />
      <Skeleton className="h-4 w-32" />
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-3 rounded-xl border p-4">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-4 w-40" />
        </div>
        <div className="space-y-3 rounded-xl border p-4">
          <Skeleton className="h-5 w-24" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-4 w-40" />
        </div>
      </div>
    </div>
  )
}
