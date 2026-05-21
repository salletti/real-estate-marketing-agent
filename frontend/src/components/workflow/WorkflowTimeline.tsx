import { CheckCircle2, Clock, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { DraftResponse } from '@/lib/types/api'

type StepState = 'completed' | 'current' | 'locked'

interface WorkflowStep {
  id: string
  label: string
  getState: (draft: DraftResponse) => StepState
}

const WORKFLOW_STEPS: WorkflowStep[] = [
  {
    id: 'received',
    label: 'Bien reçu',
    getState: () => 'completed',
  },
  {
    id: 'facebook',
    label: 'Draft Facebook généré',
    getState: (draft) =>
      draft.content.data.platforms.facebook ? 'completed' : 'locked',
  },
  {
    id: 'instagram',
    label: 'Draft Instagram généré',
    getState: (draft) =>
      draft.content.data.platforms.instagram ? 'completed' : 'locked',
  },
  {
    id: 'review',
    label: 'Validation humaine',
    getState: (draft) => {
      if (draft.status === 'draft' && draft.approval_status === 'pending') return 'current'
      if (draft.status === 'published' || draft.status === 'rejected') return 'completed'
      return 'locked'
    },
  },
  {
    id: 'publish',
    label: 'Publication',
    getState: (draft) => {
      if (draft.status === 'published') return 'completed'
      return 'locked'
    },
  },
]

interface StepIconProps {
  state: StepState
}

function StepIcon({ state }: StepIconProps) {
  if (state === 'completed') {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-green-100">
        <CheckCircle2 className="h-5 w-5 text-green-600" />
      </div>
    )
  }
  if (state === 'current') {
    return (
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100">
        <Clock className="h-5 w-5 animate-pulse text-amber-600" />
      </div>
    )
  }
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100">
      <Lock className="h-4 w-4 text-gray-400" />
    </div>
  )
}

interface WorkflowTimelineProps {
  draft: DraftResponse
}

export function WorkflowTimeline({ draft }: WorkflowTimelineProps) {
  const states = WORKFLOW_STEPS.map((step) => step.getState(draft))

  return (
    <div className="space-y-0">
      {WORKFLOW_STEPS.map((step, index) => {
        const state = states[index]
        const isLast = index === WORKFLOW_STEPS.length - 1
        const prevCompleted = index === 0 || states[index - 1] === 'completed'

        return (
          <div key={step.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <StepIcon state={state} />
              {!isLast && (
                <div
                  className={cn(
                    'my-1 w-0.5 flex-1',
                    prevCompleted && state !== 'locked' ? 'bg-green-300' : 'bg-gray-200',
                  )}
                  style={{ minHeight: '24px' }}
                />
              )}
            </div>
            <div className={cn('pb-4 pt-1', isLast && 'pb-0')}>
              <p
                className={cn(
                  'text-sm font-medium',
                  state === 'completed' && 'text-foreground',
                  state === 'current' && 'text-amber-700',
                  state === 'locked' && 'text-muted-foreground',
                )}
              >
                {step.label}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
