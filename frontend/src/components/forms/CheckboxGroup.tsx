import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'

interface CheckboxGroupProps {
  options: readonly string[]
  value: string[]
  onChange: (value: string[]) => void
  labelMap?: Record<string, string>
}

export function CheckboxGroup({ options, value, onChange, labelMap }: CheckboxGroupProps) {
  const toggle = (option: string) => {
    if (value.includes(option)) {
      onChange(value.filter((v) => v !== option))
    } else {
      onChange([...value, option])
    }
  }

  return (
    <div className="flex flex-wrap gap-3">
      {options.map((option) => (
        <div key={option} className="flex items-center gap-2">
          <Checkbox
            id={option}
            checked={value.includes(option)}
            onCheckedChange={() => toggle(option)}
          />
          <Label htmlFor={option} className="cursor-pointer text-sm font-normal">
            {labelMap?.[option] ?? option}
          </Label>
        </div>
      ))}
    </div>
  )
}
