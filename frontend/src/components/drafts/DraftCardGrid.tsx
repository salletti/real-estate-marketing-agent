import { FacebookDraftCard } from './FacebookDraftCard'
import { InstagramDraftCard } from './InstagramDraftCard'
import type { PlatformsContent } from '@/lib/types/api'

interface DraftCardGridProps {
  platforms: PlatformsContent
  photos: string[]
}

export function DraftCardGrid({ platforms, photos }: DraftCardGridProps) {
  const count = (platforms.facebook ? 1 : 0) + (platforms.instagram ? 1 : 0)

  return (
    <div className={`grid gap-6 ${count === 2 ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1 max-w-lg'}`}>
      {platforms.facebook && (
        <FacebookDraftCard content={platforms.facebook} photos={photos} />
      )}
      {platforms.instagram && (
        <InstagramDraftCard content={platforms.instagram} photos={photos} />
      )}
    </div>
  )
}
