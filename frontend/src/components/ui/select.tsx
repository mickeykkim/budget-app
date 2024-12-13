// src/components/ui/select.tsx
import * as React from "react"
import * as SelectPrimitive from "@radix-ui/react-select"
import { ChevronDown, Check } from "lucide-react"

export function Select({ 
  children, 
  onValueChange,
  value,
  ...props 
}: SelectPrimitive.SelectProps) {
  return (
    <SelectPrimitive.Root 
      onValueChange={onValueChange}
      value={value}
      {...props}
    >
      {children}
    </SelectPrimitive.Root>
  )
}

export function SelectTrigger({ children, ...props }: SelectPrimitive.SelectTriggerProps) {
    return (
      <SelectPrimitive.Trigger
        className="flex items-center justify-between w-full border rounded px-3 py-2"
        {...props}
      >
        {children}
        <SelectPrimitive.Icon>
          <ChevronDown className="h-4 w-4" />
        </SelectPrimitive.Icon>
      </SelectPrimitive.Trigger>
    )
  }

export function SelectContent({ children, ...props }: SelectPrimitive.SelectContentProps) {
  return (
    <SelectPrimitive.Portal>
      <SelectPrimitive.Content 
        position="popper"
        className="z-50 bg-white border rounded shadow-lg"
        {...props}
      >
        <SelectPrimitive.Viewport>
          {children}
        </SelectPrimitive.Viewport>
      </SelectPrimitive.Content>
    </SelectPrimitive.Portal>
  )
}

export function SelectItem({ children, ...props }: SelectPrimitive.SelectItemProps) {
  return (
    <SelectPrimitive.Item
      className="relative px-8 py-2 hover:bg-gray-100 cursor-pointer"
      {...props}
    >
      <SelectPrimitive.ItemIndicator className="absolute left-2">
        <Check className="h-4 w-4" />
      </SelectPrimitive.ItemIndicator>
      {children}
    </SelectPrimitive.Item>
  )
}

export function SelectValue(props: SelectPrimitive.SelectValueProps) {
    return <SelectPrimitive.Value {...props} />
  }
  