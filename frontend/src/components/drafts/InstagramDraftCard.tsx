import { Heart, MessageCircle, Send, Bookmark } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import type { InstagramPlatformContent } from '@/lib/types/api'

interface InstagramDraftCardProps {
  content: InstagramPlatformContent
  photos: string[]
}

export function InstagramDraftCard({ content, photos }: InstagramDraftCardProps) {
  // Priorité : photos saisies dans le formulaire, sinon images du backend
  const images = photos.length > 0 ? photos : content.images
  const mainImage = images[0] ?? null

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400">
            <svg viewBox="0 0 24 24" fill="white" className="h-5 w-5">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold">votre_agence</p>
            <p className="text-xs text-muted-foreground">il y a quelques instants</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {mainImage ? (
          <img
            src={mainImage}
            alt="Photo du bien"
            className="aspect-square w-full rounded-lg object-cover"
          />
        ) : (
          <div className="aspect-square w-full rounded-lg bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
            <p className="text-xs text-muted-foreground">Photo du bien</p>
          </div>
        )}

        <div className="flex justify-between">
          <div className="flex gap-3">
            <button className="text-muted-foreground hover:text-red-500">
              <Heart className="h-5 w-5" />
            </button>
            <button className="text-muted-foreground hover:text-foreground">
              <MessageCircle className="h-5 w-5" />
            </button>
            <button className="text-muted-foreground hover:text-foreground">
              <Send className="h-5 w-5" />
            </button>
          </div>
          <button className="text-muted-foreground hover:text-foreground">
            <Bookmark className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-1">
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            <span className="font-semibold">votre_agence </span>
            {content.caption}
          </p>

          {content.hashtags.length > 0 && (
            <p className="text-sm text-blue-500">
              {content.hashtags.map((tag) => `#${tag}`).join(' ')}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
