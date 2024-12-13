// src/components/ui/alert-dialog.tsx
import React from 'react';
import * as AlertDialogPrimitive from '@radix-ui/react-alert-dialog';
import { Button } from './button';

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  onConfirm: () => void;
}

export function ConfirmDialog({ 
  open, 
  onOpenChange, 
  title, 
  description, 
  onConfirm 
}: ConfirmDialogProps) {
  return (
    <AlertDialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <AlertDialogPrimitive.Portal>
        <AlertDialogPrimitive.Overlay className="fixed inset-0 bg-black/50" />
        <AlertDialogPrimitive.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white p-6 rounded-lg shadow-xl">
          <AlertDialogPrimitive.Title className="text-lg font-semibold mb-2">
            {title}
          </AlertDialogPrimitive.Title>
          <AlertDialogPrimitive.Description className="text-sm text-gray-600 mb-4">
            {description}
          </AlertDialogPrimitive.Description>
          
          <div className="flex justify-end space-x-2">
            <AlertDialogPrimitive.Cancel asChild>
              <Button variant="outline">Cancel</Button>
            </AlertDialogPrimitive.Cancel>
            
            <AlertDialogPrimitive.Action asChild>
              <Button variant="destructive" onClick={onConfirm}>
                Confirm
              </Button>
            </AlertDialogPrimitive.Action>
          </div>
        </AlertDialogPrimitive.Content>
      </AlertDialogPrimitive.Portal>
    </AlertDialogPrimitive.Root>
  );
}