import { Check, X, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useDraftAction } from '@/lib/hooks/useDraft'
import type { LinkResponse } from '@/lib/types/api'

interface ActionConfig {
  label: string
  variant: 'default' | 'destructive' | 'outline'
  icon: React.ReactNode
  confirmMessage?: string
}

const ACTION_CONFIG: Record<string, ActionConfig> = {
  publish: {
    label: 'Publier',
    variant: 'default',
    icon: <Check className="h-4 w-4" />,
  },
  reject: {
    label: 'Rejeter',
    variant: 'destructive',
    icon: <X className="h-4 w-4" />,
    confirmMessage: 'Êtes-vous sûr de vouloir rejeter ce draft ?',
  },
}

interface HateoasActionBarProps {
  links: Record<string, LinkResponse>
  threadId: string
}

export function HateoasActionBar({ links, threadId }: HateoasActionBarProps) {
  const { mutate, isPending } = useDraftAction(threadId)

  const actions = Object.entries(links)
    .map(([key, link]) => ({ key, link, config: ACTION_CONFIG[key] }))
    .filter(({ config }) => config !== undefined)

  if (actions.length === 0) return null

  return (
    <div className="flex items-center gap-3 border-t pt-4">
      <p className="text-sm text-muted-foreground">Actions disponibles :</p>
      {actions.map(({ key, link, config }) => (
        <Button
          key={key}
          variant={config.variant}
          disabled={isPending}
          onClick={() => {
            if (config.confirmMessage && !window.confirm(config.confirmMessage)) return
            mutate({ href: link.href, method: link.method })
          }}
          className="gap-2"
        >
          {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : config.icon}
          {config.label}
        </Button>
      ))}
    </div>
  )
}
