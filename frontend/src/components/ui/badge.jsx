import * as React from 'react'
import { cn } from '../../lib/utils'

const Badge = React.forwardRef(({ className, variant = 'default', ...props }, ref) => {
  return (
    <span
      ref={ref}
      className={cn(
        'inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide',
        className
      )}
      {...props}
    />
  )
})
Badge.displayName = 'Badge'

export { Badge }
