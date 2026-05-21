import { ThumbsUp, MessageCircle, Share2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import type { FacebookPlatformContent } from '@/lib/types/api'

interface FacebookDraftCardProps {
  content: FacebookPlatformContent
  photos: string[]
}

export function FacebookDraftCard({ content, photos }: FacebookDraftCardProps) {
  // Priorité : photos saisies dans le formulaire, sinon images du backend
  const images = photos.length > 0 ? photos : content.images

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-white">
            <svg viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
              <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold">Votre Agence</p>
            <p className="text-xs text-muted-foreground">Il y a quelques instants · 🌍</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{content.post}</p>

        {images.length > 0 && (
          <div className={`grid gap-1 overflow-hidden rounded-lg ${images.length === 1 ? 'grid-cols-1' : 'grid-cols-2'}`}>
            {images.slice(0, 4).map((url, i) => (
              <img
                key={i}
                src={url}
                alt={`Photo ${i + 1}`}
                className="aspect-video w-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none'
                }}
              />
            ))}
          </div>
        )}

        {content.hashtags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {content.hashtags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-blue-600 text-xs">
                #{tag}
              </Badge>
            ))}
          </div>
        )}

        <div className="flex gap-4 border-t pt-3">
          <button className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-blue-600">
            <ThumbsUp className="h-4 w-4" /> J&apos;aime
          </button>
          <button className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-blue-600">
            <MessageCircle className="h-4 w-4" /> Commenter
          </button>
          <button className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-blue-600">
            <Share2 className="h-4 w-4" /> Partager
          </button>
        </div>
      </CardContent>
    </Card>
  )
}
